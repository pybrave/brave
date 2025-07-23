import os
from watchfiles import awatch
from importlib.resources import files
from importlib import import_module
from brave.api.config.db import get_engine
from brave.api.core.event import WatchFileEvent
from brave.api.models.core import analysis
import asyncio
import inspect
import logging
from brave.api.service.sse_service import   SSESessionService
from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.listener_files_service import ListenerFilesService
from brave.api.core.routers.watch_file_event_router import WatchFileEvenetRouter
from brave.app_container import AppContainer
from dependency_injector.wiring import Provide

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileWatcherService:
    def __init__(
        self, 
        watch_path: str,
        watchfile_event_router:WatchFileEvenetRouter=Provide[AppContainer.watchfile_event_router]
        # sse_service: SSESessionService, 
        # analysis_result_parse_service: AnalysisResultParse,
        # listener_files_service: ListenerFilesService
    ):
        """
        初始化 FileWatcher 实例。
        
        :param watch_path: 要监控的文件夹路径
        :param listener_prefix: 监听器文件名前缀，默认是 "file"
        """
        self.watch_path = watch_path
        self.watchfile_event_router = watchfile_event_router
        # self.sse_service = sse_service
        # self.analysis_result_parse_service = analysis_result_parse_service
        # self.listener_files_service = listener_files_service

    # def _load_listener_files(self):
    #     """加载所有符合条件的文件监听器"""
    #     listener_files = files("brave.api.listener")
    #     return [
    #         item.stem
    #         for item in listener_files.iterdir()
    #         if item.is_file() and item.name.endswith(".py")
    #         and item.name != "__init__.py" and item.name.startswith(self.listener_prefix)
    #     ]

    # async def execute_listener(self, func, args):
    #     """执行文件变更后的监听器函数"""
    #     if isinstance(self.listener_files, list) and len(self.listener_files) > 0:
    #         for name in self.listener_files:
    #             full_module = f"brave.api.listener.{name}"
    #             mod = import_module(full_module)
    #             if hasattr(mod, func):
    #                 run_func = getattr(mod, func)
    #                 if inspect.iscoroutinefunction(run_func):
    #                     # 如果是异步函数，创建一个异步任务
    #                     await run_func(**args)
    #                 else:
    #                     # 否则通过线程池执行
    #                     await asyncio.to_thread(run_func, **args)

    async def watch_folder(self):
        """文件变更监控任务"""
        print(f"开始监控文件夹: {self.watch_path}")
        async for changes in awatch(self.watch_path, recursive=False, step=3000):

            for change, file_path in changes:
                event:WatchFileEvent
                if "trace" in file_path:
                    event = WatchFileEvent.TRACE_LOG
                    analysis_id = os.path.basename(file_path).replace(".trace.log","")
                elif "workflow" in file_path:
                    event =WatchFileEvent.WORKFLOW_LOG
                    analysis_id = os.path.basename(file_path).replace(".workflow.log","")   
                else:
                    continue
                await self.watchfile_event_router.dispatch(event,{"event_type":event.value,"file_path":file_path,"analysis_id":analysis_id})   
                # # 触发文件变更事件
                # await self.listener_files_service.execute_listener("file_change",
                #  {"change": change, 
                #  "file_path": file_path, 
                #  "sse_service": 
                #  self.sse_service,
                #  "analysis_result_parse_service":self.analysis_result_parse_service})


# 示例：如何使用 FileWatcher 类
# async def main():
#     # 创建 FileWatcher 实例并开始监控
#     file_watcher = FileWatcher(watch_path="path_to_your_folder")
#     await file_watcher.watch_folder()

# 在 FastAPI 或其他异步环境中调用
# asyncio.run(main())  # 如果直接运行，可以这样调用
