

import json
import os
import uuid
from brave.api.models.core import t_namespace
from brave.api.schemas.namespace import SaveNamespace
import  brave.api.service.namespace_service as namespace_service
from fastapi import APIRouter, HTTPException
from brave.api.config.db import get_engine
import brave.api.service.pipeline as pipeline_service
import brave.api.service.container_service as container_service

namespace = APIRouter()

@namespace.post("/save-or-update-namespace",tags=['namespace'])
async def save_namespace_controller(saveNamespace:SaveNamespace):
    if saveNamespace.volumes:
        try:
            json.loads(saveNamespace.volumes)
        except Exception as e:
            raise RuntimeError(f"The volumes field is not in legal JSON format: {e}")
    with get_engine().begin() as conn:
        if saveNamespace.namespace_id:
            find_namespace = namespace_service.find_namespace(conn,saveNamespace.namespace_id)

            namespace_id = find_namespace.namespace_id 
            namespace_service.update_namespace(conn,saveNamespace.namespace_id,saveNamespace.dict())
        else:
            str_uuid = str(uuid.uuid4())
            saveNamespace.namespace_id = str_uuid
            namespace_id = str_uuid
            namespace_service.save_namespace(conn,saveNamespace.model_dump())
    
    # namespace = f"{pipeline_dir}/{namespace_id}"
    # if not os.path.exists(namespace):
    #     os.makedirs(namespace)
    # with open(f"{namespace}/namespace.json","w") as f:
    #     f.write(json.dumps(saveNamespace.dict()))
    namespace_service.write_namespace(namespace_id,saveNamespace.model_dump())
    return {"message":"success"}

@namespace.get("/list-namespace",tags=['namespace'])
async def list_namespace():
    with get_engine().begin() as conn:
        return namespace_service.list_namespace(conn)

    

@namespace.delete("/delete-namespace-by-id/{namespace_id}",tags=['namespace'])
async def delete_namespace_by_namespace_id(namespace_id:str):
    with get_engine().begin() as conn:
        find_namespace = namespace_service.find_namespace(conn,namespace_id)
        if find_namespace:
            find_component =  pipeline_service.find_component_by_namespace(conn,find_namespace.namespace_id)
            if find_component:
                raise HTTPException(status_code=400, detail=f"namespace {find_namespace.name} 存在组件，不能删除")
            container_services = container_service.find_by_namespace(conn,namespace_id)
            if container_services:
                raise HTTPException(status_code=400, detail=f"namespace {find_namespace.name} 存在容器，不能删除")

        if find_namespace:
            namespace_service.delete_namespace(conn,namespace_id)
            return {"message":"success"}


@namespace.get("/find-namespace-by-id/{namespace_id}",tags=['namespace'])
async  def find_by_id(namespace_id):
    with get_engine().begin() as conn:
        find_namespace = namespace_service.find_namespace(conn,namespace_id)
        if not find_namespace:
            raise HTTPException(status_code=404, detail=f"Namespace with id {namespace_id} not found")
        return find_namespace