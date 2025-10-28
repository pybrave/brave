import asyncio
import os
import json
from typing import Optional

from brave.api.config.config import get_settings
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
# from brave.api.service.file_watcher_service import FileWatcher
from brave.api.handlers import analysis_executer
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.service.sse_service import SSESessionService
from brave.api.config.db import get_engine
from brave.api.service import namespace_service, project_service
from brave.api.ingress.manager import IngressManager
from brave.api.handlers import workflow_events,analysis_result   
from brave.api.core.workflow_queue import WorkflowQueueManager
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
from brave.api.core.routers.ingress_event_router import IngressEventRouter
from brave.api.core.event import IngressEvent
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.core.heartbeat import process_heartbeat
from brave.api.core.routers.watch_file_event_router import WatchFileEvenetRouter
from brave.api.service.file_watcher_service import FileWatcherService
from brave.api.core.event import WatchFileEvent
from brave.api.core.event import WorkflowEvent
import  brave.api.service.analysis_service as analysis_service
from brave.api.executor.base import JobExecutor
from brave.api.executor.local_executor import LocalExecutor
from py2neo import Graph

class AppManager:
    @inject
    def __init__(
        self, 
        workflow_queue_manager: WorkflowQueueManager = Provide[AppContainer.workflow_queue_manager],
        ingress_manager: IngressManager = Provide[AppContainer.ingress_manager],
        ingress_event_router: IngressEventRouter = Provide[AppContainer.ingress_event_router],
        sse_service: SSESessionService = Provide[AppContainer.sse_service],
        analysis_result_parse_service: AnalysisResultParse = Provide[AppContainer.analysis_result_parse_service],
        listener_files_service: ListenerFilesService = Provide[AppContainer.listener_files_service],
        workflow_event_router:WorkflowEventRouter=Provide[AppContainer.workflow_event_router],
        watchfile_event_router:WatchFileEvenetRouter=Provide[AppContainer.watchfile_event_router],
        job_executor:JobExecutor=Provide[AppContainer.job_executor_selector],
        config = Provide[AppContainer.config]   
        
        ):
        self.config = config
        self.graph: Graph | None = None
        self.workflow_queue_manager = workflow_queue_manager
        self.ingress_event_router = ingress_event_router
        self.ingress_manager = ingress_manager
        self.sse_service = sse_service
        self.analysis_result_parse_service = analysis_result_parse_service
        self.listener_files_service = listener_files_service
        self.workflow_event_router = workflow_event_router
        self.watchfile_event_router = watchfile_event_router
        self.job_executor = job_executor
        self.config = config
        self.tasks = []
        # 预先声明属性，后面启动时赋值
        self.file_watcher = None
        self.process_monitor = None
        self.wes = None
        


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
            sse_service=self.sse_service,
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
            await self.sse_service.push_message({"group": "default", "data": json.dumps(msg)})

        # self.watchfile_event_router.register_handler(WatchFileEvent.WORKFLOW_LOG,push_file_watch_message)
        # self.watchfile_event_router.register_handler(WatchFileEvent.TRACE_LOG,  push_file_watch_message)

        # setup_handlers()
        analysis_executer.setup_handlers()
        workflow_events.setup_handlers()
        analysis_result.setup_handlers()
        self.tasks.append(asyncio.create_task(self.sse_service.broadcast_loop()))



        # self.tasks.append(asyncio.create_task(self.analysis_result_parse_service.auto_save_analysis_result()))
        self.tasks.append(asyncio.create_task(self.file_watcher_service.watch_folder()))
        self.tasks.append(asyncio.create_task(self.process_monitor.startup_process_event()))
        # 挂载到 app.state，方便别处访问
        # self.app.state.manager = self

        # init db
        with get_engine().begin() as conn: 
            await namespace_service.init_db(conn)
            await project_service.init_db(conn)

        

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.graph = None
        print("[AppManager] All background tasks stopped")
