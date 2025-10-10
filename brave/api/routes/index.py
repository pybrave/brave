from fastapi import APIRouter


index_api = APIRouter()

@index_api.get("/ping")
async def ping():
    return {"message": "pong"}


