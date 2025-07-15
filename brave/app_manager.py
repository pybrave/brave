import asyncio
import os

from brave.api.config.config import get_settings
from brave.api.service.analysis_result_parse import get_analysis_result_parse_service
from brave.api.service.file_watcher_service import FileWatcher
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.service.sse_service import get_sse_service
from brave.api.workflow_events.manager import WorkflowEventSystem
from brave.api.workflow_events.handlers.workflow_events import setup_handlers
class AppManager:
    def __init__(self, app):
        self.app = app
        self.tasks = []
        # 预先声明属性，后面启动时赋值
        self.sse_service = None
        self.listener_files_service = None
        self.analysis_result_parse_service = None
        self.file_watcher = None
        self.process_monitor = None
        self.wes = None

    async def start(self):
        settings = get_settings()
        watch_path = f"{settings.BASE_DIR}/monitor"
        if not os.path.exists(watch_path):
            os.makedirs(watch_path)

        self.sse_service = get_sse_service()
        self.listener_files_service = get_listener_files_service()
        self.analysis_result_parse_service = get_analysis_result_parse_service(
            sse_service=self.sse_service,
            listener_files_service=self.listener_files_service
        )

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

        self.wes = WorkflowEventSystem()
        self.wes.register_http(self.app)
        self.tasks.append(asyncio.create_task(self.wes.cleanup_loop()))

        self.tasks.append(asyncio.create_task(self.analysis_result_parse_service.auto_save_analysis_result()))
        self.tasks.append(asyncio.create_task(self.file_watcher.watch_folder()))
        self.tasks.append(asyncio.create_task(self.sse_service.broadcast_loop()))
        self.tasks.append(asyncio.create_task(self.process_monitor.startup_process_event()))
        self.tasks.append(asyncio.create_task(self.wes.start()))
        setup_handlers()
        # 挂载到 app.state，方便别处访问
        self.app.state.manager = self

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("[AppManager] All background tasks stopped")
