import os
from fastapi import APIRouter
from brave.api.config.config import get_settings
import glob
import json
from collections import defaultdict
from brave.api.config.db import get_engine
import brave.api.service.pipeline as pipeline_service

component_store_api = APIRouter(prefix="/component-store",tags=["component_store"])

def open_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["file_path"] = file_path
    
    return data

@component_store_api.get("/list")
async def list_components(store_name,component_type):
    settings = get_settings()
    store_dir = settings.STORE_DIR

    file_list = glob.glob(f"{store_dir}/{store_name}/{component_type}/*/install.json")
    file_list = [open_file(file) for file in file_list]
    component_ids= [ item["component_id"] for item in file_list]
    with get_engine().begin() as conn: 
        component_installed =  pipeline_service.find_by_component_ids(conn,component_ids)
    
    installed_dict = { item["component_id"]:item for item in component_installed}
    for item in file_list:
        if item["component_id"] in installed_dict:
            item["installed"] = True
        else:
            item["installed"] = False
    
    for item in file_list:
        if "img" in item and item["img"] !="":
            img_dir = item["file_path"].replace(str(settings.STORE_DIR),"")
            img_dir = os.path.dirname(img_dir)
            img_name=item["img"]
            item["img"] = f"/brave-api/store-dir{img_dir}/{img_name}"
            
    return file_list

def format_store(file_path):
    filename = os.path.basename(file_path)
    if os.path.exists(f"{file_path}/main.json"):
        with open(f"{file_path}/main.json", 'r', encoding='utf-8') as f:
            name = json.load(f).get("name", filename)
    else:
        name = filename
    
    return {
        "store_name":os.path.basename(file_path),
        "store_path":file_path,
        "name":name
    }


@component_store_api.get("/list-stores")
async def list_components_dir():
    settings = get_settings()
    store_dir = settings.STORE_DIR
    file_list = glob.glob(f"{store_dir}/*")
    file_list = [ format_store(file) for file in file_list if os.path.isdir(file)]  
    return file_list



@component_store_api.get("/list-by-type/{store_name}")
async def list_components_by_type(store_name:str,component_type:str):
    components = await list_components(store_name,component_type)

    return components




