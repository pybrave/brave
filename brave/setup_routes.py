import asyncio
from fastapi import FastAPI, Request,Response, WebSocket
import os
from fastapi.responses import JSONResponse, StreamingResponse

from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from brave.api.routes.project import project_api
from brave.api.routes.sample_result import sample_result
from brave.api.routes.file_parse_plot import file_parse_plot
from brave.api.routes.sample import sample
from brave.api.routes.analysis import analysis_api
from brave.api.routes.bio_database import bio_database
from brave.api.routes.pipeline import pipeline
from brave.api.routes.literature import literature_api
from brave.api.routes.sse import sseController
from brave.api.routes.namespace import namespace
from brave.api.routes.index import index_api

from brave.api.routes.file_operation import file_operation
from brave.api.routes.setting import setting_controller
from brave.api.config.config import get_settings
from fastapi.responses import FileResponse
from brave.app_manager import AppManager    
from brave.api.routes.container import container_controller
from brave.microbe.routes.entity_relation import entity_relation_api
from brave.microbe.routes.entity import entity_api
from brave.microbe.routes.study import  study_api
from brave.microbe.nlp.nlp import  nlp_api
from brave.api.routes.kegg import kegg_api
from brave.api.routes.component_store import component_store_api
from brave.microbe.routes.llm import llm_api

import httpx
import websockets

def setup_routes(app: FastAPI,manager:AppManager):
  
    
    if "DIR_MAPPING" in os.environ:
        dir_mapping = os.environ["DIR_MAPPING"]
        dir_mapping_list = dir_mapping.split(":")
        prefix = dir_mapping_list[0]
        target = dir_mapping_list[1]
        print(f"Mounting {target} to {prefix}")
        app.mount(prefix, StaticFiles(directory=target), name="dir_mapping")

    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "build","assets")), name="assets")
    # frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    app.mount("/brave-api/img", StaticFiles(directory=os.path.join(frontend_path, "img")), name="img")
    settings = get_settings()
    app.mount("/brave-api/dir", StaticFiles(directory=settings.BASE_DIR, follow_symlink=True), name="base_dir")
    app.mount("/brave-api/analysis-dir", StaticFiles(directory=settings.ANALYSIS_DIR, follow_symlink=True), name="analysis_dir")
    app.mount("/brave-api/data-dir", StaticFiles(directory=settings.DATA_DIR, follow_symlink=True), name="data_dir")

    app.mount("/brave-api/work-dir", StaticFiles(directory=settings.WORK_DIR), name="work_dir")

    app.mount("/brave-api/literature/dir", StaticFiles(directory=os.path.join(settings.LITERATURE_DIR)), name="literature_dir")
    app.mount("/brave-api/pipeline-dir", StaticFiles(directory=os.path.join(settings.PIPELINE_DIR)), name="pipeline_dir")
    app.mount("/brave-api/store-dir", StaticFiles(directory=os.path.join(settings.STORE_DIR)), name="store_dir")
    app.mount("/brave-api/database-dir", StaticFiles(directory=os.path.join(settings.DATABASES_DIR)), name="database_dir")

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
    app.include_router(container_controller,prefix="/brave-api")
    app.include_router(project_api,prefix="/brave-api")
    app.include_router(entity_api,prefix="/brave-api")
    app.include_router(entity_relation_api,prefix="/brave-api")
    app.include_router(study_api, prefix="/brave-api")
    app.include_router(nlp_api, prefix="/brave-api")
    app.include_router(kegg_api, prefix="/brave-api")
    app.include_router(index_api,prefix="/brave-api")
    app.include_router(component_store_api,prefix="/brave-api")
    app.include_router(llm_api,prefix="/brave-api")



    app.get("/brave-api/sse-group")(manager.sse_service.create_endpoint())  
    endpoint = manager.ingress_manager.create_endpoint()
    if endpoint:
        app.post("/brave-api/ingress")(endpoint)
    # curl -X POST http://localhost:5005/brave-api/ingress -d '{"ingress_event": "workflow_log", "workflow_event":"flow_begin","workflow_id": "123", "message": "test"}'
    # app.state.sse_service = sse_service
    
    JUPYTER_SERVER_URL = "http://192.168.3.63:8888" # Replace with your Jupyter server URL

    # @app.api_route("/jupyter/{path:path}",  methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
    # async def proxy_jupyter(request: Request, path: str):
    #     jupyter_url = f"{JUPYTER_SERVER_URL}/jupyter/{path}"

    #     async with httpx.AsyncClient() as client:
    #         proxy_req = client.build_request(
    #             request.method,
    #             jupyter_url,
    #             headers=request.headers.raw,
    #             content=await request.body()
    #         )
    #         response = await client.send(proxy_req, stream=True)
            
    #         return StreamingResponse(response.aiter_raw(), status_code=response.status_code, headers=dict(response.headers))
    
    JUPYTER_SERVER_HTTP = "http://192.168.3.63:8888"  # 你的 Jupyter HTTP 地址
    JUPYTER_SERVER_WS = "ws://192.168.3.63:8888"     # 你的 Jupyter WebSocket  
    # @app.api_route("/jupyter/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
    # async def proxy_jupyter(path: str, request: Request):
    #     async with httpx.AsyncClient() as client:
    #         # Construct the URL for the Jupyter server
    #         jupyter_url = f"{JUPYTER_SERVER_URL}/jupyter/{path}"

    #         # Forward the request
    #         response = await client.request(
    #             method=request.method,
    #             url=jupyter_url,
    #             headers=request.headers,
    #             content=await request.body(),
    #             params=request.query_params
    #         )

    #         # Return the response from Jupyter
    #         return Response(content=response.content, status_code=response.status_code, headers=response.headers)


    # @app.api_route("/jupyter/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    # async def proxy_http(full_path: str, request: Request):
    #     url = f"{JUPYTER_SERVER_HTTP}/jupyter/{full_path}"

    #     async with httpx.AsyncClient() as client:
    #         # 转发请求头，排除host等敏感头
    #         headers = dict(request.headers)
    #         headers.pop("host", None)

    #         response = await client.request(
    #             method=request.method,
    #             url=url,
    #             headers=headers,
    #             content=await request.body(),
    #             params=request.query_params
    #         )

    #     # 返回响应，过滤部分header避免冲突
    #     excluded_headers = ["content-encoding", "transfer-encoding", "connection"]
    #     headers = [(k, v) for k, v in response.headers.items() if k.lower() not in excluded_headers]
    #     return Response(content=response.content, status_code=response.status_code, headers=dict(headers))


    # @app.websocket("/jupyter/{full_path:path}")
    # async def proxy_ws(full_path: str, websocket: WebSocket):
    #     await websocket.accept()
    #     target_url = f"{JUPYTER_SERVER_WS}/jupyter/{full_path}"
    #     try:
    #         async with websockets.connect(target_url) as jupyter_ws:

    #             async def forward_ws_to_client():
    #                 try:
    #                     async for message in jupyter_ws:
    #                         await websocket.send_text(message)
    #                 except websockets.ConnectionClosed:
    #                     pass

    #             async def forward_client_to_ws():
    #                 try:
    #                     while True:
    #                         data = await websocket.receive_text()
    #                         await jupyter_ws.send(data)
    #                 except WebSocketDisconnect:
    #                     pass

    #             # 并发转发，等待任何一方断开
    #             await asyncio.wait([
    #                 forward_ws_to_client(),
    #                 forward_client_to_ws(),
    #             ], return_when=asyncio.FIRST_COMPLETED)

    #     except Exception as e:
    #         await websocket.close()
    
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


    # async def value_error_handler(request: Request, exc: Exception):
    #     return JSONResponse(
    #         status_code=400,
    #         content={"detail": str(exc), "type": "ValueError"}
    #     )

    # # 注册异常处理器
    # app.add_exception_handler(Exception, value_error_handler)
    # @app.exception_handler(Exception)
    @app.get("/favicon.ico")
    async def serve_favicon():
        favicon = os.path.join(frontend_path, "build/favicon.ico")
        return FileResponse(favicon)

    @app.get("/html/index.html")
    async def html():
        index_path = os.path.join(frontend_path, "html/index.html")
        return FileResponse(index_path)
    @app.get("/psycmicrograph.html")
    async def html():
        index_path = os.path.join(frontend_path, "build/psycmicrograph.html")
        return FileResponse(index_path)

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index_path = os.path.join(frontend_path, "build/index.html")
        return FileResponse(index_path)

