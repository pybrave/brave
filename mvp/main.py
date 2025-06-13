# https://github.com/FaztWeb/fastapi-mysql-restapi/blob/main/routes/user.py

from fastapi import FastAPI

from mvp.api.routes.file_parse_plot import file_parse_plot
from mvp.api.routes.sample_result import sample_result
from mvp.api.routes.sample import sample
from mvp.api.routes.analysis import analysis_api
from mvp.api.routes.pipeline import pipeline

from mvp.api.routes.bio_database import bio_database
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

def create_app() -> FastAPI:
    app = FastAPI()
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "build")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    pipelinie_path = os.path.join(os.path.dirname(__file__), "pipeline")

    app.mount("/mvp-api/img", StaticFiles(directory=os.path.join(pipelinie_path, "img")), name="pipleine_img")

    app.include_router(sample_result,prefix="/mvp-api")
    app.include_router(file_parse_plot,prefix="/mvp-api")
    app.include_router(sample,prefix="/mvp-api")
    app.include_router(analysis_api,prefix="/mvp-api")
    app.include_router(bio_database,prefix="/mvp-api")
    app.include_router(pipeline,prefix="/mvp-api")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index_path = os.path.join(frontend_path, "index.html")
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