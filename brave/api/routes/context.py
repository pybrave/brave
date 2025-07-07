

import json
import os
import uuid
from brave.api.models.core import t_context
from brave.api.schemas.context import SaveContext
import  brave.api.service.context_service as context_service
from fastapi import APIRouter, HTTPException
from brave.api.config.db import get_engine
import brave.api.service.pipeline as pipeline_service

context = APIRouter()

@context.post("/save-or-update-context",tags=['context'])
async def save_context_controller(saveContext:SaveContext):
    pipeline_dir = pipeline_service.get_pipeline_dir()
    with get_engine().begin() as conn:
        if saveContext.context_id:
            find_context = context_service.find_context(conn,saveContext.context_id)
            # if find_context:
                # raise HTTPException(status_code=400, detail=f"context_id {saveContext.context_id} 存在，不能更新")
            context_id = saveContext.context_id
            context_service.update_context(conn,saveContext.context_id,saveContext.dict())
        else:
            str_uuid = str(uuid.uuid4())
            saveContext.context_id = str_uuid
            context_id = str_uuid
            context_service.save_context(conn,saveContext.dict())
    
    namespace = f"{pipeline_dir}/{context_id}"
    if not os.path.exists(namespace):
        os.makedirs(namespace)
    with open(f"{namespace}/namespace.json","w") as f:
        f.write(json.dumps(saveContext.dict()))
    return {"message":"success"}

@context.get("/list-context-by-type/{type}",tags=['context'])
async def list_context_by_type(type:str):
    with get_engine().begin() as conn:
        return context_service.list_context_by_type(conn,type)

    

@context.delete("/delete-namespace-by-context-id/{context_id}",tags=['context'])
async def delete_context_by_context_id(context_id:str):
    with get_engine().begin() as conn:
        find_context = context_service.find_context(conn,context_id)
        if find_context:
            find_component =  pipeline_service.find_component_by_namespace(conn,find_context.context_id)
            if find_component:
                raise HTTPException(status_code=400, detail=f"namespace {find_context.name} 存在，不能删除")
        context_service.delete_context(conn,context_id)
        return {"message":"success"}