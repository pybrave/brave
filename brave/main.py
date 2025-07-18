# https://github.com/FaztWeb/fastapi-mysql-restapi/blob/main/routes/user.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from dependency_injector import providers

from brave.api.routes.file_parse_plot import file_parse_plot
from brave.api.routes.sample_result import sample_result
from brave.api.routes.sample import sample
from brave.api.routes.analysis import analysis_api
from brave.api.routes.pipeline import pipeline
from brave.api.routes.literature import literature_api
from brave.api.routes.sse import sseController
import asyncio
# from brave.api.service.watch_service import watch_folder,startup_process_event
from brave.api.service.sse_service import SSESessionService
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.routes.bio_database import bio_database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from brave.api.config.config import get_settings
from brave.api.service.sse_service import  SSEService  # 从 service.py 导入
from brave.api.routes.namespace import namespace
from brave.api.routes.file_operation import file_operation  
# from brave.api.service.sse_service import get_sse_service
# from brave.api.service.analysis_result_parse import get_analysis_result_parse_service
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.routes.setting import setting_controller
from brave.app_manager import AppManager
from brave.app_container import AppContainer
from brave.setup_routes import setup_routes
container = AppContainer()
container.wire(modules=["brave.api.routes"], packages=["brave.api.routes"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = AppManager()
    # container.app_manager.override(providers.Object(manager))
    await manager.start()
    setup_routes(app,manager)
    
    app.state.manager = manager 
    yield 
    await manager.stop()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     settings = get_settings()
#     print("✅ 启动后台任务")
#     current_loop = asyncio.get_event_loop()
#     # print(f"startup 事件循环：{current_loop}")
#     global producer_task, broadcast_task
#     watch_path = f"{settings.BASE_DIR}/monitor"
#     if not  os.path.exists(watch_path):
#         os.makedirs(watch_path)

#     # asyncio.create_task(watch_folder(monitor))
#     # sse_service = SSEService()
#     # sse_service = SSESessionService()
#     sse_service = get_sse_service()
#     listener_files_service = get_listener_files_service()
#     analysis_result_parse_service = get_analysis_result_parse_service(
#         sse_service=sse_service,
#         listener_files_service=listener_files_service
#     )
#     asyncio.create_task(analysis_result_parse_service.auto_save_analysis_result())
#     file_watcher = FileWatcher(
#         watch_path=watch_path,
#         sse_service=sse_service,
#         analysis_result_parse_service=analysis_result_parse_service,
#         listener_files_service=listener_files_service
#     )
#     process_monitor = ProcessMonitor(
#         sse_service=sse_service,
#         analysis_result_parse_service=analysis_result_parse_service,
#         listener_files_service=listener_files_service)

#     app.state.sse_service = sse_service
#     app.state.file_watcher = file_watcher
#     app.state.process_monitor = process_monitor
#     asyncio.create_task(file_watcher.watch_folder())
#     asyncio.create_task(sse_service.broadcast_loop())
#     # asyncio.create_task(sse_service.producer())
#     asyncio.create_task(process_monitor.startup_process_event())

#     wes = WorkflowEventSystem()
#     wes.register_http(app)
#     wes_task = asyncio.create_task(wes.start())
#     # get_analysis_result_parse(sse_service)
#     yield
#     if wes_task: 
#         wes_task.cancel()
#         print("[System] WorkflowEventSystem stopped")
    
def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app
