from brave.api.schemas.project import AddProject,UpdateProject
from brave.api.models.core import t_project,samples as t_samples,analysis_result as t_analysis_result
import uuid
from fastapi import HTTPException

async def add_project(conn,AddProject:AddProject):
    uuid_str = str(uuid.uuid4())
    stmt = t_project.insert().values(project_id=uuid_str,project_name=AddProject.project_name,metadata_form=AddProject.metadata_form)
    conn.execute(stmt)
    return uuid_str

async def update_project(conn,UpdateProject:UpdateProject):
    stmt = t_project.update().where(t_project.c.project_id==UpdateProject.project_id).values(project_name=UpdateProject.project_name,metadata_form=UpdateProject.metadata_form)
    conn.execute(stmt)
    return UpdateProject.project_id

async def list_project(conn):
    stmt = t_project.select()
    result = conn.execute(stmt)
    return result.mappings().all()

async def find_by_project_id(conn,project_id:str):
    stmt = t_project.select().where(t_project.c.project_id==project_id)
    result = conn.execute(stmt).mappings().first()
    return result

def find_by_project_ids(conn,project_ids:list[str]):
    stmt = t_project.select().where(t_project.c.project_id.in_(project_ids))
    result = conn.execute(stmt).mappings().all()
    return result

async def delete_project(conn,project_id:str):
    stmt = t_samples.select().where(t_samples.c.project==project_id)
    result = conn.execute(stmt).fetchone()
    if result:
        raise HTTPException(status_code=400, detail="Project has samples, cannot be deleted")

    stmt = t_analysis_result.select().where(t_analysis_result.c.project==project_id)
    result = conn.execute(stmt).fetchone()
    if result:
        raise HTTPException(status_code=400, detail="Project has analysis results, cannot be deleted")


    stmt = t_analysis_result.select().where(t_analysis_result.c.project==project_id)
    result = conn.execute(stmt).fetchone()
    if result:
        raise HTTPException(status_code=400, detail="Project has analysis results, cannot be deleted")
    conn.execute(stmt)
    stmt = t_project.delete().where(t_project.c.project_id==project_id)
    conn.execute(stmt)
    return project_id

async def init_db(conn):
    stmt = t_project.select().where(t_project.c.project_id=="default")
    result = conn.execute(stmt).fetchone()
    if not result:
        project_dict = {"project_id":"default","project_name":"default","metadata_form":"[]"}
        stmt = t_project.insert().values(project_dict)
        conn.execute(stmt)