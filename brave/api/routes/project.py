import json
from fastapi import APIRouter
from brave.api.schemas.project import AddProject,UpdateProject
from brave.api.service import project_service
from brave.api.config.db import get_engine

project_api = APIRouter(prefix="/project")

@project_api.post("/add-project")
async def add_project(AddProject:AddProject):
    with get_engine().begin() as conn:
        project_id = await project_service.add_project(conn,AddProject)
        return {"project_id":project_id}

@project_api.post("/update-project")
async def update_project(UpdateProject:UpdateProject):
    with get_engine().begin() as conn:
        project_id = await project_service.update_project(conn,UpdateProject)
        return {"project_id":project_id}
    
def get_one_project(item):
    if not item:
        return {}
    item = dict(item)
    try:
        item['metadata_form'] = json.loads(item['metadata_form'])
    except:
        item["metadata_form"] = []

    return item

@project_api.get("/list-project")
async def list_project():
    with get_engine().begin() as conn:
        projects = await project_service.list_project(conn)
        projects = [get_one_project(item) for item in projects]
        return projects


@project_api.get("/find-by-project-id/{project_id}")
async def find_by_project_id(project_id:str):
    with get_engine().begin() as conn:
        project = await project_service.find_by_project_id(conn,project_id)
        return get_one_project(project)

@project_api.delete("/delete-project/{project_id}")
async def delete_project(project_id:str):
    with get_engine().begin() as conn:
        project_id = await project_service.delete_project(conn,project_id)
        return {"project_id":project_id}