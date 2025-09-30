
from fastapi import APIRouter
from brave.api.config.db import get_engine
from brave.microbe.service import study_service
from brave.microbe.utils import pubmed
study_api = APIRouter(prefix="/study")


@study_api.get("/mining-study/{entity_id}")
async def get_entity( entity_id: str):
    with get_engine().begin() as conn:
        result = study_service.mining_study(conn, entity_id)
    return result

@study_api.post("/get-fulltext/{entity_id}")
async def get_pmc_fulltext(entity_id: str):
    with get_engine().begin() as conn:
        study = study_service.mining_study(conn, entity_id)
        pmcid = study["pmcid"]
        fulltext = await pubmed.get_pmc_fulltext(pmcid)
        study_service.update_study(conn, entity_id, {"fulltext": fulltext})
    return {"message": "Full text updated successfully"}