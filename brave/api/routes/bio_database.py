import uuid
from fastapi import APIRouter
import pandas as pd
import json

from sqlalchemy import select

from brave.api.config.db import get_engine
from brave.api.models.core import t_bio_database
from brave.api.schemas.bio_database import AddBioDatabase, QueryBiodatabase, UpdateBioDatabase
import brave.api.service.bio_database_service as bio_database_service

bio_database = APIRouter()

@bio_database.get("/fast-api/get_metaphlan_clade")
async def get_metaphlan_clade():
    with open("/ssd1/wy/workspace2/nextflow-fastapi/databases/clade.json") as f:
        data = json.load(f)
    return data


@bio_database.post("/list-bio-database",tags=["bio_database"])
async def list_bio_database(query: QueryBiodatabase):
    with get_engine().begin() as conn:
        result = bio_database_service.list_bio_database(conn,query)
    return result

@bio_database.get("/fast-api/get_bio_database_by_id")
async def get_bio_database_by_id(database_id: str):
    with get_engine().begin() as conn:
        result = bio_database_service.get_bio_database_by_id(conn,database_id)
    return result



@bio_database.post("/add-bio-database",tags=["bio_database"])
async def add_bio_database(database: AddBioDatabase):
    unique_id = str(uuid.uuid4())
    with get_engine().begin() as conn:
        conn.execute(t_bio_database.insert().values(database_id=unique_id,**database.model_dump()))
    return {"message": "Database added successfully"}


@bio_database.post("/update-bio-database",tags=["bio_database"])
async def update_bio_database(database: UpdateBioDatabase):
    with get_engine().begin() as conn:
        conn.execute(t_bio_database.update().where(t_bio_database.c.database_id == database.database_id).values(**database.model_dump()))
    return {"message": "Database updated successfully"}


@bio_database.delete("/delete-bio-database/{database_id}",tags=["bio_database"])
async def delete_bio_database(database_id: int):
    with get_engine().begin() as conn:
        conn.execute(t_bio_database.delete().where(t_bio_database.c.id == database_id))
    return {"message": "Database deleted successfully"}


# async def get_database_content_by_name(name: str):
#     with get_engine().begin() as conn:
#         stmt = select(t_bio_database).where(t_bio_database.c.name == name)
#         result = conn.execute(stmt).first()
        
#     return result