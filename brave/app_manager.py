import asyncio
import os
import json
from typing import Optional

from brave.api.config.config import get_settings
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
# from brave.api.service.file_watcher_service import FileWatcher
from brave.api.handlers import analysis_executer
from brave.api.handlers import git_executer
from brave.api.llm.tool_manager import ToolManager
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.service.realtime_service import RealtimeService
from brave.api.config.db import get_engine
from brave.api.service import namespace_service, project_service
from brave.api.service import analysis_node_service
from brave.api.ingress.manager import IngressManager
from brave.api.handlers import workflow_events,analysis_result   
from brave.api.core.workflow_queue import WorkflowQueueManager
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from brave.api.core.event import IngressEvent
from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.core.heartbeat import process_heartbeat
from brave.api.core.routers.watch_file_event_router import WatchFileEvenetRouter
from brave.api.service.file_watcher_service import FileWatcherService
from brave.api.core.event import WatchFileEvent
from brave.api.core.event import WorkflowEvent
from brave.api.core.routers_name import RoutersName
from brave.api.schemas.analysis import AnalysisExecuterModal
import  brave.api.service.analysis_service as analysis_service
from brave.api.executor.base import JobExecutor
from brave.api.executor.local_executor import LocalExecutor
from py2neo import Graph
from brave.api.llm.tool_register import register_tools
class AppManager:
    @inject
    def __init__(
        self, 
        workflow_queue_manager: WorkflowQueueManager = Provide[AppContainer.workflow_queue_manager],
        ingress_manager: IngressManager = Provide[AppContainer.ingress_manager],
        ingress_event_router: IngressEventRouter = Provide[AppContainer.ingress_event_router],
        realtime_service: RealtimeService = Provide[AppContainer.realtime_service],
        analysis_result_parse_service: AnalysisResultParse = Provide[AppContainer.analysis_result_parse_service],
        listener_files_service: ListenerFilesService = Provide[AppContainer.listener_files_service],
        workflow_event_router:WorkflowEventRouter=Provide[AppContainer.workflow_event_router],
        watchfile_event_router:WatchFileEvenetRouter=Provide[AppContainer.watchfile_event_router],
        event_bus:EventBus=Provide[AppContainer.event_bus],
        job_executor:JobExecutor=Provide[AppContainer.job_executor_selector],
        config = Provide[AppContainer.config],
        tool_manager:ToolManager=Provide[AppContainer.tool_manager]
    ):
        self.config = config
        self.graph: Graph | None = None
        self.workflow_queue_manager = workflow_queue_manager
        self.ingress_event_router = ingress_event_router
        self.ingress_manager = ingress_manager
        self.realtime_service = realtime_service
        # Backward compatibility for existing code paths.
        # self.sse_service = realtime_service
        self.analysis_result_parse_service = analysis_result_parse_service
        self.listener_files_service = listener_files_service
        self.workflow_event_router = workflow_event_router
        self.watchfile_event_router = watchfile_event_router
        self.event_bus = event_bus
        self.job_executor = job_executor
        self.tool_manager = tool_manager
        self.config = config
        self.tasks = []
        # 预先声明属性，后面启动时赋值
        self.file_watcher = None
        self.process_monitor = None
        self.wes = None

    async def _recover_stopping_dag_analysis(self, analysis_id: str):
        with get_engine().begin() as conn:
            node_items = analysis_node_service.find_running_analysis_node(conn)
            running_nodes = [item for item in node_items if item.get("analysis_id") == analysis_id]

        for node in running_nodes:
            run_id = str(node.get("run_id") or "")
            if not run_id:
                continue
            payload = AnalysisExecuterModal(
                analysis_id=str(node.get("analysis_node_id") or ""),
                run_id=run_id,
                run_type=str(node.get("run_type") or "node"),
            )
            try:
                await self.event_bus.dispatch(
                    RoutersName.ANALYSIS_EXECUTER_ROUTER,
                    AnalysisExecutorEvent.ON_ANALYSIS_STOPED,
                    payload,
                )
            except Exception as exc:
                print(
                    f"[AppManager] Failed to stop recovered DAG node: "
                    f"analysis_id={analysis_id} run_id={run_id} err={exc}"
                )

        wait_timeout_seconds = 60
        wait_interval_seconds = 1
        elapsed = 0
        while elapsed < wait_timeout_seconds:
            with get_engine().begin() as conn:
                node_items = analysis_node_service.find_running_analysis_node(conn)
                running_count = len([item for item in node_items if item.get("analysis_id") == analysis_id])
            if running_count == 0:
                await analysis_service.finished_analysis(analysis_id, "job", "stopped")
                print(f"[AppManager] Recovered stopping DAG analysis to stopped: {analysis_id}")
                return
            await asyncio.sleep(wait_interval_seconds)
            elapsed += wait_interval_seconds

        print(f"[AppManager] Recover stopping DAG timed out: {analysis_id}")

    async def _recover_running_dag_analysis(self):
        with get_engine().begin() as conn:
            running_dag_analysis = analysis_service.find_running_dag_analysis(conn)

        if not running_dag_analysis:
            return

        for item in running_dag_analysis:
            analysis_id = item.get("analysis_id")
            if not analysis_id:
                continue

            if item.get("job_status") == "stopping":
                asyncio.create_task(
                    self._recover_stopping_dag_analysis(analysis_id),
                    name=f"recover-stop-{analysis_id}",
                )
                print(f"[AppManager] Recovering stopping DAG analysis: {analysis_id}")
                continue

            run_id = item.get("run_id") or f"job-{analysis_id}"
            payload = AnalysisExecuterModal(
                analysis_id=analysis_id,
                run_id=run_id,
                run_type="job",
            )

            try:
                await self.event_bus.dispatch(
                    RoutersName.ANALYSIS_EXECUTER_ROUTER,
                    AnalysisExecutorEvent.ON_DAG_SUBMITTED,
                    payload,
                )
                print(f"[AppManager] Recovered running DAG analysis: {analysis_id}")
            except Exception as exc:
                print(f"[AppManager] Failed to recover DAG analysis {analysis_id}: {exc}")
        


    async def start(self):
        settings = get_settings()
        watch_path = f"{settings.BASE_DIR}/monitor"
        if not os.path.exists(watch_path):
            os.makedirs(watch_path)

        # self.graph = Graph(
        #     self.settings.bolt_url,
        #     auth=(self.settings.user, self.settings.password)
        # )
        
        if settings.NEO4J_BOLT:
            # conn_str = "neo4j:password@bolt://localhost:7687"
            conn_str = settings.NEO4J_BOLT
            user_pass, address = conn_str.split("@", 1)
            user, password = user_pass.split(":", 1)

            self.graph = Graph(address, auth=(user, password))
            # self.graph  = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

        self.file_watcher_service = FileWatcherService(
            watch_path=watch_path,
            watchfile_event_router=self.watchfile_event_router
        ) 
        self.process_monitor = ProcessMonitor(
            sse_service=self.realtime_service,
            analysis_result_parse_service=self.analysis_result_parse_service,
            listener_files_service=self.listener_files_service
        )
      
        # register http ingress
        # self.ingress_manager.register_http(self.app)
        self.tasks.append(asyncio.create_task(self.ingress_manager.start()))

        # register handler for ingress event
        self.ingress_event_router.register_handler(IngressEvent.HEARTBEAT, process_heartbeat)

        # register  handler for workflow  queue
        # self.ingress_event_router.register_handler(IngressEvent.NEXTFLOW_EXECUTOR_EVENT, self.workflow_queue_manager.dispatch)
        # self.workflow_queue_manager.register_subscriber(WorkflowEvent.ON_FLOW_BEGIN, self.workflow_event_router.dispatch)
        # self.tasks.append(asyncio.create_task(self.workflow_queue_manager.cleanup_loop()))



        async def workflow_evnet_dispatch(msg:dict):
            try:
                event = WorkflowEvent(msg.get("workflow_event"))
            except ValueError:
                event = msg.get("workflow_event")
                print(f"[WorkflowEventRouter] Unknown event type '{event}'", msg)
                return
            analysis_id = msg.get("analysis_id")
            if analysis_id:
                await self.workflow_event_router.dispatch(event,analysis_id,msg)

        self.ingress_event_router.register_handler(IngressEvent.NEXTFLOW_EXECUTOR_EVENT,  workflow_evnet_dispatch)





        # async def push_default_message(analysis_id:str,msg:dict):
        #     await self.sse_service.push_message({"group": "default", "data": json.dumps(msg)})


        
        # #  sse_service.push_message
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_FLOW_BEGIN,  push_default_message)
        # # self.workflow_event_router.register_handler(WorkflowEvent.ON_FILE_PUBLISH,  self.sse_service.push_message_default)
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_PROCESS_COMPLETE,  push_default_message)
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_FLOW_COMPLETE,  push_default_message)
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_JOB_SUBMITTED,  push_default_message)

     
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_FLOW_COMPLETE, finished_analysis_handler)

        # self.workflow_queue_manager.register_subscriber("", subscriber)

        async def push_file_watch_message(msg:dict):
            await self.realtime_service.push_message({"group": "default", "data": json.dumps(msg)})

        # self.watchfile_event_router.register_handler(WatchFileEvent.WORKFLOW_LOG,push_file_watch_message)
        # self.watchfile_event_router.register_handler(WatchFileEvent.TRACE_LOG,  push_file_watch_message)

        # setup_handlers()
        analysis_executer.setup_handlers()
        git_executer.setup_handlers()
        workflow_events.setup_handlers()
        analysis_result.setup_handlers()
        await self._recover_running_dag_analysis()
        self.tasks.append(asyncio.create_task(self.realtime_service.broadcast_loop()))
        # self.tasks.append(asyncio.create_task(self.ws_service.broadcast_loop()))

        # self.tasks.append(asyncio.create_task(self.analysis_result_parse_service.auto_save_analysis_result()))
        self.tasks.append(asyncio.create_task(self.file_watcher_service.watch_folder()))
        self.tasks.append(asyncio.create_task(self.process_monitor.startup_process_event()))
        # 挂载到 app.state，方便别处访问
        # self.app.state.manager = self

        # init db
        with get_engine().begin() as conn: 
            await namespace_service.init_db(conn)
            await project_service.init_db(conn)
        
        register_tools(self.tool_manager, self.realtime_service)

        

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.graph = None
        print("[AppManager] All background tasks stopped")
