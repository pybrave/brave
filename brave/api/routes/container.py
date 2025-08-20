
from fastapi import APIRouter
from brave.api.schemas.container import PageContainerQuery,SaveContainer
import brave.api.service.container_service as container_service
from brave.api.config.db import get_engine
from brave.api.config.db import get_engine
import brave.api.service.pipeline as pipeline_service
import uuid

container_controller = APIRouter(prefix="/container")

@container_controller.post("/page", tags=['container'])
async def page_container(query:PageContainerQuery):
    with get_engine().begin() as conn:
        return container_service.page_container(conn,query)

@container_controller.get("/find-by-id/{container_id}", tags=['container'])
async def find_by_id(container_id):
    with get_engine().begin() as conn:
        return container_service.find_container_by_id(conn,container_id)




@container_controller.post("/add-or-update-container",tags=['container'])
async def save_namespace_controller(saveContainer:SaveContainer):
    with get_engine().begin() as conn:
        if saveContainer.container_id:
            find_container= container_service.find_container_by_id(conn,saveContainer.container_id)
            container_id = find_container.container_id 
            container_service.update_container(conn,saveContainer.container_id,saveContainer.dict())
        else:
            str_uuid = str(uuid.uuid4())
            saveContainer.container_id = str_uuid
            container_id = str_uuid
            container_service.save_container(conn,saveContainer.dict())
        container_service.write_all_container(conn,saveContainer.namespace)

    return {"message":"success"}

@container_controller.delete("/delete-container-by-id/{container_id}",tags=['container'])
async def delete_by_container_id(container_id:str):
    with get_engine().begin() as conn:
        find_container = container_service.find_container_by_id(conn,container_id)
        if find_container:
            find_component =  pipeline_service.find_component_by_container_id(conn,container_id)
            if find_component:
                raise HTTPException(status_code=400, detail=f"container {container_id} 存在组件，不能删除")
        container_service.delete_container(conn,container_id)

    container_service.write_all_container(conn,find_container.container_id)
    return {"message":"success"}


