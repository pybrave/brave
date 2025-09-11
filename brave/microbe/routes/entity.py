from fastapi import APIRouter
from brave.api.config.db import get_engine
from brave.microbe.models.core import t_taxonomy
from brave.microbe.service import study_service
from brave.microbe.service import  disease_service
from brave.microbe.utils.import_ncbi_taxonomy import merge_all
from sqlalchemy import insert
import brave.microbe.service.taxonomy_service as taxonomy_service
from brave.microbe.schemas.entity import PageEntity

entity_api = APIRouter(prefix="/entity")


@entity_api.get("/import")
def import_taxonomy():
    with get_engine().begin() as conn:
        # 读取三张表并合并
        taxonomy = merge_all(
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/nodes.dmp",
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/names.dmp",
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/division.dmp"
        )
        # taxonomy["taxonomy_id"] = f"TAX{taxonomy['tax_id']}"
        taxonomy["taxonomy_id"] = "TAX" + taxonomy["tax_id"].astype(str)
        records = taxonomy.to_dict(orient="records")
        batch_size = 20000  # 每次 1w 行，自己调节

        inserted = 0
        with get_engine().begin() as conn:  # type: Connection
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(t_taxonomy)
                conn.execute(stmt, batch)
                inserted += len(batch)
                print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}


@entity_api.post("/page/{entity}")
async def page_entity(entity: str, query: PageEntity):
    with get_engine().begin() as conn:
        if entity == "taxonomy":    
            result = taxonomy_service.page_taxonomy(conn, query)
        elif entity == "study":
            result = study_service.page_study(conn, query)  
        elif entity == "disease":
            result = disease_service.page_disease(conn, query)
        else:
            raise ValueError("Unsupported entity type")
    return result   

@entity_api.get("/get/{entity}/{entity_id}")
async def get_entity(entity: str, entity_id: str):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.find_taxonomy_by_id(conn, entity_id)
        elif entity == "study":
            result = study_service.find_study_by_id(conn, entity_id)
        elif entity == "disease":
            result = disease_service.find_disease_by_id(conn, entity_id)
        else:
            raise ValueError("Unsupported entity type")
    return result

@entity_api.put("/update/{entity}/{entity_id}")
async def update_entity(entity: str, entity_id: str, updateData: dict):
    with get_engine().begin() as conn:
        if entity == "taxonomy":
            taxonomy_service.update_taxonomy(conn, entity_id, updateData)
        elif entity == "study":
            study_service.update_study(conn, entity_id, updateData) 
        elif entity == "disease":
            disease_service.update_disease(conn, entity_id, updateData)  
        else:
            raise ValueError("Unsupported entity type")
    return {"message": "Entity updated successfully"}

@entity_api.post("/add/{entity}")
async def add_entity(entity: str, data: dict):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            taxonomy_service.add_taxonomy(conn, data)
        elif entity == "study":
            study_service.add_study(conn, data)     
        elif entity == "disease":   
            disease_service.add_disease(conn, data)
        else:
            raise ValueError("Unsupported entity type")
    return {"message": "Entity added successfully"}



@entity_api.get("/find-by-name/{entity}/{keywords}")
async def get_entity(entity: str, keywords: str):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.find_taxonomy_by_keywords(conn, keywords)
        elif entity == "study":
            result = study_service.find_study_by_keywords(conn, keywords)
        elif entity == "disease":
            result = disease_service.find_disease_by_keywords(conn, keywords)
        else:
            raise ValueError("Unsupported entity type")
    return result



@entity_api.get("/details/{entity}/{entity_id}")
async def get_entity(entity: str, entity_id: str):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.details_taxonomy_by_id(conn, entity_id)
        elif entity == "study":
            result = study_service.details_study_by_id(conn, entity_id)
        elif entity == "disease":
            result = disease_service.details_disease_by_id(conn, entity_id)
        else:
            raise ValueError("Unsupported entity type")
    return result

@entity_api.get("/import/{entity}")
async def import_entitys(entity: str, entity_list: list[dict]):
    with get_engine().begin() as conn:
        if entity == "taxonomy":
            result = taxonomy_service.import_taxonomy(conn, entity_list)
        elif entity == "study":
            result = study_service.import_studies(conn, entity_list)
        elif entity == "disease":
            result = disease_service.import_diseases(conn, entity_list)
        else:
            raise ValueError("Unsupported entity type")
    return result