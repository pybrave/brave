import json
from fastapi import APIRouter, HTTPException
from brave.api.schemas.project import AddProject,UpdateProject
from brave.api.service import project_service
from brave.api.config.db import get_engine
from pathlib import Path
from brave.api.config.config import get_settings
import os 

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
    



@project_api.get("/list-project-dir/{project_id}")
async def list_dir_v2(
    project_id: str,
    path: str = "",
    keyword: str = "",
    page: int = 1,
    type: str = "data",
    limit: int = 20,
):
    
    settings = get_settings()
    if type=="analysis":
        real_path = f"{settings.ANALYSIS_DIR}/{project_id}"
    else:
        real_path = f"{settings.DATA_DIR}/{project_id}"

    if path:
        real_path = f"{real_path}/{path}"
    full_path = Path(  real_path).resolve()
    if not full_path.exists() or not full_path.is_dir() :
        full_path_str = str(full_path)
        if full_path_str.endswith(project_id) or full_path_str.endswith(f"{project_id}/") :
            os.makedirs(full_path_str, exist_ok=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid path")

    items = []
    for item in full_path.iterdir():
        if keyword.lower() in item.name.lower():
            items.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime,
            })

    # 分页处理
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    paged_items = items[start:end]

    return {
        "items": paged_items,
        "total": total,
        "page": page,
        "limit": limit,
    }