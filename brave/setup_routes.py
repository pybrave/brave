from fastapi import FastAPI
import os
from fastapi.staticfiles import StaticFiles
from brave.api.routes.sample_result import sample_result
from brave.api.routes.file_parse_plot import file_parse_plot
from brave.api.routes.sample import sample
from brave.api.routes.analysis import analysis_api
from brave.api.routes.bio_database import bio_database
from brave.api.routes.pipeline import pipeline
from brave.api.routes.literature import literature_api
from brave.api.routes.sse import sseController
from brave.api.routes.namespace import namespace
from brave.api.routes.file_operation import file_operation
from brave.api.routes.setting import setting_controller
from brave.api.config.config import get_settings
from fastapi.responses import FileResponse
from brave.app_manager import AppManager    

def setup_routes(app: FastAPI,manager:AppManager):
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

    app.get("/brave-api/sse-group")(manager.sse_service.create_endpoint())  
    endpoint = manager.ingress_manager.create_endpoint()
    if endpoint:
        app.post("/brave-api/ingress")(endpoint)
    # curl -X POST http://localhost:5005/brave-api/ingress -d '{"ingress_event": "workflow_log", "workflow_event":"flow_begin","workflow_id": "123", "message": "test"}'
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
    async def serve_favicon():
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
