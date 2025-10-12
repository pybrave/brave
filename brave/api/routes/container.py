
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from brave.api.config.config import get_settings
from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.core.routers_name import RoutersName
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.schemas.container import ListContainerQuery, PageContainerQuery,SaveContainer
import brave.api.service.container_service as container_service
from brave.api.config.db import get_engine
from brave.api.config.db import get_engine
import brave.api.service.pipeline as pipeline_service
import uuid
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
import asyncio

from brave.app_container import AppContainer

container_controller = APIRouter(prefix="/container")

@container_controller.post("/page", tags=['container'])
@inject
async def page_container(query:PageContainerQuery,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    with get_engine().begin() as conn:
        page_list =  container_service.page_container(conn,query)
    containers = await job_executor.list_running()
    containers_dict = {k: v for d in containers for k, v in d.items()}
    items = []
    for item in page_list['items']:
        if item["container_id"] in containers_dict:
            item["status"] = "running"
            item["docker_id"] = containers_dict[item["container_id"]]
        else:
            item["status"] = "stopped"
        items.append(item)
    page_list['items'] = items
    return page_list

@container_controller.get("/find-by-id/{container_id}", tags=['container'])
async def find_by_id(container_id):
    with get_engine().begin() as conn:
        return container_service.find_container_by_id(conn,container_id)




@container_controller.post("/add-or-update-container",tags=['container'])
@inject
async def save_namespace_controller(saveContainer:SaveContainer, job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    image = ""
    save_container_dict  = saveContainer.model_dump()
    with get_engine().begin() as conn:
        if saveContainer.container_id:
            find_container= container_service.find_container_by_id(conn,saveContainer.container_id)
            container_id = find_container.container_id 
            image = saveContainer.image or find_container.image
            image = job_executor.get_image(image)
            if image:
                save_container_dict.update({"image_id":image.id,"image_status":"exist"})
            else:
                save_container_dict.update({"image_status":"not_exist"})
            container_service.update_container(conn,saveContainer.container_id,save_container_dict)
        else:
            str_uuid = str(uuid.uuid4())
            save_container_dict["container_id"] = str_uuid
            container_id = str_uuid
            image = saveContainer.image
            image = job_executor.get_image(image)
            if image:
                save_container_dict.update({"image_id":image.id,"image_status":"exist"})
            else:
                save_container_dict.update({"image_status":"not_exist"})
            container_service.save_container(conn,save_container_dict)
        if saveContainer.namespace!="default":
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
        if find_container.namespace!="default":
            container_service.write_all_container(conn,find_container.namespace)
    return {"message":"success"}




@container_controller.post("/run-container/{container_id}")
@inject
async def run_container(
    container_id,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):
    settings = get_settings()

    data_dir = str(settings.DATA_DIR)
    analysis_ =  AnalysisExecuterModal(
        analysis_id=container_id,
        container_id=container_id,
        output_dir=data_dir,
        pipeline_script=f"{data_dir}/run.sh",
        run_type="retry"
    )
    # try:
    # raise RuntimeError("oops!")
    await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED,analysis_)
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    
    # job_id = await executor.submit_job(LocalJobSpec(
    #     job_id=analysis_id,
    #     command=["bash", "run.sh"],
    #     output_dir=analysis_['output_dir'],
    #     process_id=analysis_['process_id']
    # ))

    return {"msg":"success"}


@container_controller.post("/stop-container/{container_id}")
@inject
async def run_container(
    container_id,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):
    settings = get_settings()

    data_dir = str(settings.DATA_DIR)
    analysis_ =  AnalysisExecuterModal(
        analysis_id=container_id,
        container_id=container_id,
        output_dir=data_dir,
        pipeline_script=f"{data_dir}/run.sh",
        run_type="retry"
    )
    await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_STOPED,analysis_)


@container_controller.post("/pull-image/{container_id}")
@inject
async def page_container(container_id,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    with get_engine().begin() as conn:
        find_container = container_service.find_container_by_id(conn,container_id)
        

        asyncio.create_task(job_executor.pull_image(container_id,find_container.image))
        container_service.update_container(conn,
                                            container_id,
                                            {"image_status":"pulling"})
    return "success"


@container_controller.post("/list-container-key")
@inject
async def  list_container_key(query:ListContainerQuery,
                               job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    with get_engine().begin() as conn:
        find_container=  container_service.list_container_key(conn,query)
        find_container = [dict(item) for item in find_container]
        containers = await job_executor.list_running()
        
        containers_dict = {k: v for d in containers for k, v in d.items()}
        items = []
        for item in find_container:
            if item["container_id"] in containers_dict:
                item["status"] = "running"
                item["docker_id"] = containers_dict[item["container_id"]]
            else:
                item["status"] = "stopped"
            items.append(item)
    return items


@container_controller.post("/find-container-key")
@inject
async def  find_container_key(query:ListContainerQuery,
                               job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    with get_engine().begin() as conn:
        find_container=  container_service.find_container_key(conn,query)
        if not find_container:
            return {}
    find_container = dict(find_container)
    containers = await job_executor.list_running()
    
    containers_dict = {k: v for d in containers for k, v in d.items()}
    items = []
    if find_container["container_id"] in containers_dict:
        find_container["status"] = "running"
        find_container["docker_id"] = containers_dict[find_container["container_id"]]
    else:
        find_container["status"] = "stopped"
        
    return items
