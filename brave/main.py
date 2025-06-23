# https://github.com/FaztWeb/fastapi-mysql-restapi/blob/main/routes/user.py

from fastapi import FastAPI

from brave.api.routes.file_parse_plot import file_parse_plot
from brave.api.routes.sample_result import sample_result
from brave.api.routes.sample import sample
from brave.api.routes.analysis import analysis_api
from brave.api.routes.pipeline import pipeline
from brave.api.routes.literature import literature_api

from brave.api.routes.bio_database import bio_database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from brave.api.config.config import get_settings

def create_app() -> FastAPI:
    app = FastAPI()
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "build","assets")), name="assets")
    # frontend_path = os.path.join(os.path.dirname(__file__), "frontend")

    app.mount("/brave-api/img", StaticFiles(directory=os.path.join(frontend_path, "img")), name="img")

    settings = get_settings()
    app.mount("/brave-api/dir", StaticFiles(directory=settings.BASE_DIR), name="base_dir")
    app.mount("/brave-api/literature/dir", StaticFiles(directory=os.path.join(settings.LITERATURE_DIR)), name="literature_dir")

    app.include_router(sample_result,prefix="/brave-api")
    app.include_router(file_parse_plot,prefix="/brave-api")
    app.include_router(sample,prefix="/brave-api")
    app.include_router(analysis_api,prefix="/brave-api")
    app.include_router(bio_database,prefix="/brave-api")
    app.include_router(pipeline,prefix="/brave-api")
    app.include_router(literature_api,prefix="/brave-api")

    @app.get("/favicon.ico")
    async def serve_frontend():
        favicon = os.path.join(frontend_path, "build/favicon.ico")
        return FileResponse(favicon)

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