import asyncio
import json
import os
import shutil
import signal
import time
from dependency_injector.wiring import Provide, inject

from fastapi import APIRouter, Depends, HTTPException

from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import GitExecutorEvent
from brave.api.core.routers_name import RoutersName
from brave.api.schemas.store import CreateStore, PageStoreQuery, StoreQuery
from  brave.api.service import store_service 

from brave.api.utils import git_utils
from brave.app_container import AppContainer

store_api = APIRouter()


@store_api.post("/delete-store/{store_id}",tags=['pipeline'])
@inject
async def delete_store(store_id:str):
    with get_engine().begin() as conn:
        store_service.delete_store(conn,store_id)
    return {"message":"success"}



@store_api.post("/clone-store",tags=['pipeline'])
@inject
async def clone_store(createStore: CreateStore,
                        evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) ):
    with get_engine().begin() as conn:
        find_store = store_service.find_store_by_url(conn, createStore.url)
        if find_store:
            return {
                "store_id": find_store.get("store_id"),
                "already_exists": True,
                "message": "success",
            }


        settings = get_settings()
        store_path = f"{settings.STORE_DIR}"
        url = createStore.url
        # url_lists = url.split("/")
        # if len(url_lists) < 2:
        #     raise HTTPException(status_code=400, detail=f"Invalid git url: {url}")
        
        # filename = url_lists[-1]
        # # target_path is owner/repo
        # url_path = url_lists[-2:]
        # path_name = f"{url_path[0]}/{filename.replace('.git','')}"
        path_name, filename = git_utils.get_path_name_from_url(url)
        target_path = f"{store_path}/{path_name}"
        # 创建父目录
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))

        publish_urls = git_utils.build_publish_urls(path_name)

        # target_path = f"{store_path}/{filename.replace('.git','')}"

        # createStore.path = target_path
        # createStore.status = "running"
        # createStore.log = f"git clone {createStore.url} {target_path}"
        # createStore.path_name = filename.replace('.git', '')

        store_data = {
            "url": createStore.url,
            "path": target_path,
            "status": "running",
            "path_name": path_name,
            "publish_urls": publish_urls,
            "name":path_name
            # "log": f"git clone {createStore.url} {target_path}",
            # "category": createStore.category,
        }
       
        store_id = store_service.create_store(conn, store_data)

    asyncio.create_task(evenet_bus.dispatch(RoutersName.GIT_EXECUTER_ROUTER, GitExecutorEvent.ON_GIT_CLONE, {
        "url": createStore.url,
        "target_path": target_path,
        "store_id": store_id,
    }))

    return {
        "store_id":store_id,
        "message": "success",
    }


    # lock_file = f"{target_path}.lock"

    # if not acquire_lock(lock_file):
    #     raise HTTPException(status_code=500, detail=f"Another download task is running for {filename}, please try again later!")
    # if os.path.exists(target_path):
    #     if force:
    #         shutil.rmtree(target_path)
    #     else:
    #         release_lock(lock_file)
    #         return {
    #             "message": "success",
    #             "target_path": target_path,
    #             "cmd": f"git clone {url} {target_path}",
    #             "info": {
    #                 "message": f"Store {target_path} already exists! If you want to overwrite it, please set force to true.",
    #                 "pid": None,
    #             },
    #         }

    # store_id = create_store_record(
    #     name=filename.replace('.git', ''),
    #     url=url,
    #     status="running",
    #     log=f"git clone {url} {target_path}",
    # )

    # try:
    #     proc = await asyncio.create_subprocess_exec(
    #         "git",
    #         "clone",
    #         url,
    #         target_path,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #     )
    # except Exception as e:
    #     delete_store_record(store_id)
    #     release_lock(lock_file)
    #     raise HTTPException(status_code=500, detail=f"Git clone failed: {str(e)}")

    # update_lock(
    #     lock_file,
    #     {
    #         "status": "running",
    #         "pid": proc.pid,
    #         "url": url,
    #         "target_path": target_path,
    #         "store_id": store_id,
    #         "operation": "clone",
    #     },
    # )

    # monitor_task = asyncio.create_task(monitor_clone_process(proc, lock_file))
    # DOWNLOAD_TASKS[lock_file] = monitor_task

    # return {
    #     "message": "success",
    #     "target_path": target_path,
    #     "cmd": f"git clone {url} {target_path}",
    #     "info": {
    #         "status": "submitted",
    #         "pid": proc.pid,
    #     },
    # }

@store_api.post("/list-stores", tags=['pipeline'])
def list_stores(query: StoreQuery ):
    with get_engine().begin() as conn:
        stores = store_service.list_store(conn, query)
       
    return stores

@store_api.get("/list-tree-stores", tags=['pipeline'])
def list_tree_stores():
    with get_engine().begin() as conn:
        stores = store_service.list_store(conn,None)
        # 根据category生成children的树状结构
        # {
        #     category:"xxx",
        #     children:[
        #         {
        #             ... store
        #         }
        #     ]
        # }
        category_tree = {}
        for store in stores:
            category = store.get("category") or "uncategorized"
            if category not in category_tree:
                category_tree[category] = {
                    "category": category,
                    "children": [],
                }
            category_tree[category]["children"].append(store)

        return list(category_tree.values())

@store_api.post("/page-stores", tags=['pipeline'])
async def page_stores(query:PageStoreQuery):
    with get_engine().begin() as conn:
        stores = store_service.page_store(conn, query)
   
    return stores


@store_api.post("/git-stop/{store_id}", tags=['pipeline'])
@inject
async def git_stop(store_id: str, evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) ):
    with get_engine().begin() as conn:
        find_store = store_service.find_store_by_id(conn,store_id)
        if not find_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        
        if find_store.get("status") not in ["running","pulling"]:
            raise HTTPException(status_code=400, detail=f"Store with id {store_id} is not in a valid state for stop operation")

        asyncio.create_task(evenet_bus.dispatch(RoutersName.GIT_EXECUTER_ROUTER, GitExecutorEvent.ON_GIT_STOP, {
            "target_path": find_store.get("path"),
            "store_id": store_id,
        }))
        return {
            "message": "success",
            "target_path": find_store.get("path")
            }
    # settings = get_settings()
    # store_path = f"{settings.STORE_DIR}"
    # url = createStore.url
    # filename = url.split("/")[-1]
    # target_path = f"{store_path}/{filename.replace('.git','')}"
    # CreateStore(
    #     url=url,
    #     path=target_path,
    #     name=filename.replace('.git', ''),
    #     status="stopped",
    # )

    # lock_file = f"{target_path}.lock"

    # lock_data = read_lock(lock_file)
    # if not lock_data:
    #     raise HTTPException(status_code=404, detail=f"Lock file not found for {filename}")

    # pid = lock_data.get("pid")
    # process_status = "pid_missing"
    # if pid:
    #     process_status = stop_process(int(pid))

    # task = DOWNLOAD_TASKS.pop(lock_file, None)
    # if task and not task.done():
    #     task.cancel()

    # release_lock(lock_file)
    # return {
    #     "message": "success",
    #     "target_path": target_path,
    #     "lock_file": lock_file,
    #     "pid": pid,
    #     "process_status": process_status,
    # }

@store_api.get("/find-store-by-id/{store_id}", tags=['pipeline'])
async def find_store_by_id(store_id: str):
    with get_engine().begin() as conn:
        find_store = store_service.find_store_by_id(conn,store_id)
        if not find_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        return find_store



@store_api.post("/save-store", tags=['pipeline'])
async def save_store(createStore: CreateStore):
    store_id = createStore.store_id
    url = createStore.url
    path_name, filename = git_utils.get_path_name_from_url(createStore.url)

    publish_urls = []
    # is_ssh= True
    if  url is not None:
        # if is_ssh:
        publish_urls = [
            {
                "name": "github",
                "ssh": f"git@github.com:{path_name}.git",
                "https": f"https://github.com/{path_name}.git"
            }, {
                "name": "gitee",
                "ssh": f"git@gitee.com:{path_name}.git",
                "https": f"https://gitee.com/{path_name}.git"   
            }
        ]
           
        # else:
        #     createStore.publish_urls = {
        #         "github": f"https://github.com/{path_name}.git",
        #         "gitee": f"https://gitee.com/{path_name}.git"
        #     }
    with get_engine().begin() as conn:
    

        if store_id:
        
            find_store = store_service.find_store_by_id(conn,store_id)
            if not find_store:
                raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
            update_data = {
                **createStore.dict(exclude_none=True),
                "status": "done",
                "publish_urls": publish_urls,
            }
            store_service.update_store(conn, store_id, update_data)
            # write_metadata({
            #     **find_store,
            #     **createStore.dict()
            # })
        else:

            find_store = store_service.find_by_path_name(conn,path_name)
            if find_store:
                raise HTTPException(status_code=400, detail=f"Store with path_name {path_name} already exists")
            settings = get_settings()
            store_path = f"{settings.STORE_DIR}"

            # path_name = createStore.path_name
            if createStore.name is  None:
                createStore.name = filename
            # filename = url.split("/")[-1]
            # createStore.path = 
            # createStore.status = "done"
            store_path = f"{store_path}/{path_name}"
            if not os.path.exists(store_path):
                os.makedirs(store_path)
                print(f"Created directory at {store_path}")
            
            # createStore.url = {
            #     "github": f"https://github.com/{path_name}.git",
            #     "gitee": f"https://gitee.com/{path_name}.git",
            # }
            
            # version = str(int(time.time()))
            store_data = {
                **createStore.dict(exclude_none=True),
                "path": store_path,
                "status":"done",
                "path_name": path_name,
                "version": createStore.version,
                "publish_urls": publish_urls,
            }
            store_data.pop("store_id", None)
            store_service.create_store(conn, store_data)
            # write_metadata(store_data)
    
            
    return {"message":"success"}

                        
@store_api.post("/git-pull/{store_id}", tags=['pipeline'])
@inject
async def git_pull(store_id: str,
                    evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus])):
    with get_engine().begin() as conn:
        find_store = store_service.find_store_by_id(conn,store_id)
        if not find_store:
            raise HTTPException(status_code=404, detail=f"Store with id {store_id} not found")
        status = find_store.get("status")
        if status != "done":
            raise HTTPException(status_code=400, detail=f"Store with id {store_id} is not in a valid state for pull operation")
        
        store_service.update_store_status(conn, store_id,"pulling")
        asyncio.create_task(evenet_bus.dispatch(RoutersName.GIT_EXECUTER_ROUTER, GitExecutorEvent.ON_GIT_PULL, {
            "target_path": find_store.get("path"),
            "url": find_store.get("url"),
            "store_id": store_id,
        }))
        return {
            "message": "success",
            "target_path": find_store.get("path"),
            "url": find_store.get("url"),
            }
    # settings = get_settings()
    # store_path = f"{settings.STORE_DIR}"
    # url = createStore.url
    # filename = url.split("/")[-1]
    # target_path = f"{store_path}/{filename.replace('.git','')}"
    # lock_file = f"{target_path}.lock"

    # if not acquire_lock(lock_file):
    #     raise HTTPException(status_code=500, detail=f"Another task is running for {filename}, please try again later!")

    # if not os.path.exists(target_path):
    #     release_lock(lock_file)
    #     raise HTTPException(status_code=404, detail=f"Store {target_path} not found!")
    # if not os.path.isdir(target_path):
    #     release_lock(lock_file)
    #     raise HTTPException(status_code=400, detail=f"Store path {target_path} is not a directory!")

    # store_id = create_store_record(
    #     name=filename.replace('.git', ''),
    #     url=url,
    #     status="running",
    #     log=f"git -C {target_path} pull",
    # )
    
    # try:
    #     proc = await asyncio.create_subprocess_exec(
    #         "git",
    #         "-C",
    #         target_path,
    #         "pull",
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #     )

    #     update_lock(
    #         lock_file,
    #         {
    #             "status": "running",
    #             "pid": proc.pid,
    #             "url": url,
    #             "target_path": target_path,
    #             "store_id": store_id,
    #             "operation": "pull",
    #         },
    #     )

    #     monitor_task = asyncio.create_task(monitor_pull_process(proc, lock_file))
    #     DOWNLOAD_TASKS[lock_file] = monitor_task

    #     return {
    #         "message": "success",
    #         "target_path": target_path,
    #         "cmd": f"git -C {target_path} pull",
    #         "info": {
    #             "status": "submitted",
    #             "pid": proc.pid,
    #         },
    #     }
    # except Exception as e:
    #     delete_store_record(store_id)
    #     release_lock(lock_file)
    #     raise HTTPException(status_code=500, detail=f"Git pull failed: {str(e)}")


