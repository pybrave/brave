import asyncio
import os
from typing import Optional

from brave.api.config.config import get_settings
from brave.api.service.file_watcher_service import FileWatcher
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.service.sse_service import SSESessionService
from brave.api.ingress.manager import IngressManager
from brave.api.workflow_events.handlers.workflow_events import setup_handlers
from brave.api.workflow_events.workflow_queue import WorkflowQueueManager
from dependency_injector.wiring import inject, Provide
from brave.app_container import AppContainer
from brave.api.core.ingress_event_router import IngressEventRouter
from brave.api.core.ingress_event_router import IngressEvent
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
class AppManager:
    @inject
    def __init__(
        self, 
        app,
        workflow_queue_manager: WorkflowQueueManager = Provide[AppContainer.workflow_queue_manager],
        ingress_manager: IngressManager = Provide[AppContainer.ingress_manager],
        ingress_event_router: IngressEventRouter = Provide[AppContainer.ingress_event_router],
        sse_service: SSESessionService = Provide[AppContainer.sse_service],
        analysis_result_parse_service: AnalysisResultParse = Provide[AppContainer.analysis_result_parse_service],
        listener_files_service: ListenerFilesService = Provide[AppContainer.listener_files_service]):

        self.workflow_queue_manager = workflow_queue_manager
        self.ingress_event_router = ingress_event_router
        self.ingress_manager = ingress_manager
        self.sse_service = sse_service
        self.analysis_result_parse_service = analysis_result_parse_service
        self.listener_files_service = listener_files_service

        self.app = app
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

   

        self.file_watcher = FileWatcher(
            watch_path=watch_path,
            sse_service=self.sse_service,
            analysis_result_parse_service=self.analysis_result_parse_service,
            listener_files_service=self.listener_files_service
        )
        self.process_monitor = ProcessMonitor(
            sse_service=self.sse_service,
            analysis_result_parse_service=self.analysis_result_parse_service,
            listener_files_service=self.listener_files_service
        )
      

        self.ingress_manager.register_http(self.app)
        self.tasks.append(asyncio.create_task(self.ingress_manager.start()))
        self.tasks.append(asyncio.create_task(self.workflow_queue_manager.cleanup_loop()))

        # register handler for workflow event
        self.ingress_event_router.register_handler(IngressEvent.WORKFLOW_LOG, self.workflow_queue_manager.dispatch)

        # self.workflow_queue_manager.register_subscriber("", subscriber)

        setup_handlers()

        self.tasks.append(asyncio.create_task(self.sse_service.broadcast_loop()))



        self.tasks.append(asyncio.create_task(self.analysis_result_parse_service.auto_save_analysis_result()))
        self.tasks.append(asyncio.create_task(self.file_watcher.watch_folder()))
        self.tasks.append(asyncio.create_task(self.process_monitor.startup_process_event()))
        # 挂载到 app.state，方便别处访问
        self.app.state.manager = self

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("[AppManager] All background tasks stopped")
