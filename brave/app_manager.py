import asyncio
import os
import json
from typing import Optional

from brave.api.config.config import get_settings
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
# from brave.api.service.file_watcher_service import FileWatcher
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.service.sse_service import SSESessionService
from brave.api.ingress.manager import IngressManager
from brave.api.handlers.workflow_events import setup_handlers   
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
        watchfile_event_router:WatchFileEvenetRouter=Provide[AppContainer.watchfile_event_router]
        ):
        

        self.workflow_queue_manager = workflow_queue_manager
        self.ingress_event_router = ingress_event_router
        self.ingress_manager = ingress_manager
        self.sse_service = sse_service
        self.analysis_result_parse_service = analysis_result_parse_service
        self.listener_files_service = listener_files_service
        self.workflow_event_router = workflow_event_router
        self.watchfile_event_router = watchfile_event_router
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
        self.tasks.append(asyncio.create_task(self.workflow_queue_manager.cleanup_loop()))

        # register handler for workflow event
        self.ingress_event_router.register_handler(IngressEvent.NEXTFLOW_EXECUTOR_EVENT, self.workflow_queue_manager.dispatch)
        self.ingress_event_router.register_handler(IngressEvent.HEARTBEAT, process_heartbeat)

        async def push_default_message(msg):
            await self.sse_service.push_message({"group": "default", "data": json.dumps(msg)})

        #  sse_service.push_message
        self.workflow_event_router.register_handler(WorkflowEvent.ON_FLOW_BEGIN,  push_default_message)
        # self.workflow_event_router.register_handler(WorkflowEvent.ON_FILE_PUBLISH,  self.sse_service.push_message_default)
        self.workflow_event_router.register_handler(WorkflowEvent.ON_PROCESS_COMPLETE,  push_default_message)
        self.workflow_event_router.register_handler(WorkflowEvent.ON_FLOW_COMPLETE,  push_default_message)
        self.workflow_event_router.register_handler(WorkflowEvent.ON_JOB_SUBMITTED,  push_default_message)

        def finished_analysis_handler(msg):
            analysis_id = msg.get("analysis_id")
            if analysis_id:
                asyncio.create_task(analysis_service.finished_analysis(analysis_id))

        self.workflow_event_router.register_handler(WorkflowEvent.ON_PROCESS_COMPLETE, finished_analysis_handler)

        # self.workflow_queue_manager.register_subscriber("", subscriber)

        self.watchfile_event_router.register_handler(WatchFileEvent.WORKFLOW_LOG,push_default_message)
        self.watchfile_event_router.register_handler(WatchFileEvent.TRACE_LOG,  push_default_message)

        setup_handlers()

        self.tasks.append(asyncio.create_task(self.sse_service.broadcast_loop()))



        self.tasks.append(asyncio.create_task(self.analysis_result_parse_service.auto_save_analysis_result()))
        self.tasks.append(asyncio.create_task(self.file_watcher_service.watch_folder()))
        self.tasks.append(asyncio.create_task(self.process_monitor.startup_process_event()))
        # 挂载到 app.state，方便别处访问
        # self.app.state.manager = self

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("[AppManager] All background tasks stopped")
