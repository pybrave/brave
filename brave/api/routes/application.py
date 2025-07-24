from fastapi import APIRouter,Request
from brave.api.service import application_service
from brave.api.config.db import get_engine
from fastapi.responses import Response

import httpx

application_api = APIRouter()

@application_api.get("/list-application")
async def list_application():
    with get_engine().begin() as conn:
        return await application_service.list_application(conn)


# @application_api.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
# async def proxy_jupyter(path: str, request: Request):
#     async with httpx.AsyncClient(base_url=f"http://10.110.1.11:8888") as client:
#         req = client.build_request(
#             request.method,
#             f"/{path}",
#             headers=request.headers.raw,
#             content=await request.body()
#         )
#         resp = await client.send(req, stream=True)
#         return Response(
#             content=await resp.aread(),
#             status_code=resp.status_code,
#             headers=dict(resp.headers)
#         )
