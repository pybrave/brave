
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
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


async def format_container(job_executor, container_list):
    containers = await job_executor.list_running()
    containers_dict = {item["name"]: item["id"] for item in containers }
    items = []

    for item in container_list:
        container_id = item["container_id"]
        run_id = f"retry-{container_id}"
        if run_id in containers_dict:
            item["status"] = "running"
            item["docker_id"] = containers_dict[run_id]
        else:
            item["status"] = "stopped"
        items.append(item)
    return items

@container_controller.post("/page", tags=['container'])
@inject
async def page_container(query:PageContainerQuery,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    with get_engine().begin() as conn:
        page_list =  container_service.page_container(conn,query)

    page_list['items'] = await format_container(job_executor, page_list["items"])
    return page_list

@container_controller.get("/find-by-id/{container_id}", tags=['container'])
async def find_by_id(container_id):
    with get_engine().begin() as conn:
        return container_service.find_container_by_id(conn,container_id)




@container_controller.post("/add-or-update-container",tags=['container'])
@inject
async def save_container_controller(saveContainer:SaveContainer, job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
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
   
    return {"message":"success"}




@container_controller.post("/run-container/{container_id}")
@inject
async def run_container(
    container_id,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):
    settings = get_settings()

    base_dir = str(settings.BASE_DIR)
    run_id = f"retry-{container_id}"
    analysis_ =  AnalysisExecuterModal(
        analysis_id=container_id,
        container_id=container_id,
        output_dir=base_dir,
        pipeline_script=f"{base_dir}/run.sh",
        run_id=run_id
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
async def stop_container(
    container_id,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):
    settings = get_settings()

    base_dir = str(settings.BASE_DIR)
    run_id = f"retry-{container_id}"
    analysis_ =  AnalysisExecuterModal(
        analysis_id=container_id,
        container_id=container_id,
        output_dir=base_dir,
        pipeline_script=f"{base_dir}/run.sh",
        run_id=run_id
    )
    await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_STOPED,analysis_)


@container_controller.post("/stop-container-by-run-id/{run_id}")
@inject
async def run_container_by_run_id(
    run_id,
    # executor: JobExecutor = Depends(get_executor_dep),
    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) 
    ):
    settings = get_settings()

    base_dir = str(settings.BASE_DIR)

    analysis_ =  AnalysisExecuterModal(
        analysis_id=run_id,
        container_id=run_id,
        output_dir=base_dir,
        pipeline_script=f"{base_dir}/run.sh",
        run_id=run_id
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
        items = await format_container(job_executor, find_container)
        
    return items




@container_controller.get("/inspect/{container_id}", tags=['container'])
@inject
async def get_inspect(container_id: str,
                        run_type:Optional[str]=None,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    run_id = container_id
    if  run_type:
        run_id = f"{run_type}-{container_id}"
    container_attr = await job_executor.get_container_attr(run_id)
    if container_attr:
        return container_attr
    else:
        raise HTTPException(status_code=404, detail=f"Container {run_id} not found or not running")




@container_controller.get("/image-inspect/{image_name}", tags=['container'])
@inject
async def get_image_inspect(image_name: str,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    image_attr = await job_executor.get_image_attr(image_name)
    if image_attr:
        return image_attr
    else:
        raise HTTPException(status_code=404, detail=f"Image {image_name} not found")
    


@container_controller.get("/list-running-container", tags=['container'])
@inject
async def list_running_container(
                        force: Optional[bool] = False,
                         job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector]) ):
    if force:
        return await job_executor.refresh_list_running()
    else:
        return await job_executor.list_running()
    

def get_image_name(container):
    tags = container.image.tags
    if tags and len(tags) > 0:
        return tags[0]
    else:
        return "<none>:<none>"

def get_container_analysis_id(container):
    labels = container.labels
    if "analysis_id" in labels:
        return labels["analysis_id"]
    else:
        return ""
@container_controller.post("/find-running-container", tags=['container'])
@inject
async def find_running_containers(label_filter: dict = Body(...), job_executor: JobExecutor = Depends(Provide[AppContainer.job_executor_selector])):
    label_str = ",".join(f"{k}={v}" for k, v in label_filter.items())
    label_filter = {"label": label_str}
    containers =  job_executor.find_running_containers(label_filter)
    containers = [{"status": container.status,"analysis_id":get_container_analysis_id(container),"image_id": container.image.id,"image": get_image_name(container), "run_id": container.name, "name": container.name, "id": container.id} for container in containers]
    return containers