from fastapi import APIRouter
scm = APIRouter()


@scm.get("/scm-store")
async def scm_store(scm: str):
    pass