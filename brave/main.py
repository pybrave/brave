# https://github.com/FaztWeb/fastapi-mysql-restapi/blob/main/routes/user.py

from fastapi import FastAPI
from contextlib import asynccontextmanager


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
from brave.api.service.file_watcher_service import FileWatcher
from brave.api.service.process_monitor_service import ProcessMonitor
from brave.api.routes.bio_database import bio_database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from brave.api.config.config import get_settings
from brave.api.service.sse_service import  SSEService  # 从 service.py 导入
from brave.api.routes.namespace import namespace
from brave.api.routes.file_operation import file_operation  
from brave.api.service.sse_service import get_sse_service
from brave.api.service.analysis_result_parse import get_analysis_result_parse_service
from brave.api.service.listener_files_service import get_listener_files_service
from brave.api.routes.setting import setting_controller
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print("✅ 启动后台任务")
    current_loop = asyncio.get_event_loop()
    # print(f"startup 事件循环：{current_loop}")
    global producer_task, broadcast_task
    watch_path = f"{settings.BASE_DIR}/monitor"
    if not  os.path.exists(watch_path):
        os.makedirs(watch_path)

    # asyncio.create_task(watch_folder(monitor))
    # sse_service = SSEService()
    # sse_service = SSESessionService()
    sse_service = get_sse_service()
    listener_files_service = get_listener_files_service()
    analysis_result_parse_service = get_analysis_result_parse_service(
        sse_service=sse_service,
        listener_files_service=listener_files_service
    )
    asyncio.create_task(analysis_result_parse_service.auto_save_analysis_result())
    file_watcher = FileWatcher(
        watch_path=watch_path,
        sse_service=sse_service,
        analysis_result_parse_service=analysis_result_parse_service,
        listener_files_service=listener_files_service
    )
    process_monitor = ProcessMonitor(
        sse_service=sse_service,
        analysis_result_parse_service=analysis_result_parse_service,
        listener_files_service=listener_files_service)

    app.state.sse_service = sse_service
    app.state.file_watcher = file_watcher
    app.state.process_monitor = process_monitor
    asyncio.create_task(file_watcher.watch_folder())
    asyncio.create_task(sse_service.broadcast_loop())
    # asyncio.create_task(sse_service.producer())
    asyncio.create_task(process_monitor.startup_process_event())

    # get_analysis_result_parse(sse_service)
    yield
    
def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "build","assets")), name="assets")
    # frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

    app.mount("/brave-api/img", StaticFiles(directory=os.path.join(frontend_path, "img")), name="img")

    settings = get_settings()
    app.mount("/brave-api/dir", StaticFiles(directory=settings.BASE_DIR), name="base_dir")
    app.mount("/brave-api/work-dir", StaticFiles(directory=settings.WORK_DIR), name="work_dir")

    app.mount("/brave-api/literature/dir", StaticFiles(directory=os.path.join(settings.LITERATURE_DIR)), name="literature_dir")
    app.mount("/brave-api/pipeline-dir", StaticFiles(directory=os.path.join(settings.PIPELINE_DIR)), name="pipeline_dir")

    app.include_router(sample_result,prefix="/brave-api")
    app.include_router(file_parse_plot,prefix="/brave-api")
    app.include_router(sample,prefix="/brave-api")
    app.include_router(analysis_api,prefix="/brave-api")
    app.include_router(bio_database,prefix="/brave-api")
    app.include_router(pipeline,prefix="/brave-api")
    app.include_router(literature_api,prefix="/brave-api")
    app.include_router(sseController,prefix="/brave-api")
    app.include_router(namespace,prefix="/brave-api")
    app.include_router(file_operation,prefix="/brave-api")
    app.include_router(setting_controller,prefix="/brave-api")
    producer_task = None
    broadcast_task = None

    
    # app.state.sse_service = sse_service
    
    
    # 启动后台广播任务
    # @app.on_event("startup")
   

        # asyncio.create_task(broadcast_loop())
        # await startup_process_event()
        # asyncio.create_task(producer())

    # @app.on_event("shutdown")
    # async def on_shutdown():
    #     print("✅ 关闭后台任务")
    #     for task in [producer_task, broadcast_task]:
    #         if task:
    #             task.cancel()
    @app.get("/favicon.ico")
    async def serve_frontend():
        favicon = os.path.join(frontend_path, "build/favicon.ico")
        return FileResponse(favicon)

    @app.get("/html/index.html")
    async def html():
        index_path = os.path.join(frontend_path, "html/index.html")
        return FileResponse(index_path)

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index_path = os.path.join(frontend_path, "build/index.html")
        return FileResponse(index_path)

    return app
# @app.get("/")
# async def read_root():
#     time.sleep(10)
#     print("sleep")
#     print(threading.get_ident())
#     time.sleep(10)
#     print(threading.get_ident())
#     return {"Hello": "World"}
    
# @app.get("/abc")
# def read_root():
#     print("sleep")
#     print(threading.get_ident())
#     time.sleep(10)
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}