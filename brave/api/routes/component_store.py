from fastapi import APIRouter
from brave.api.config.config import get_settings
import glob
import json
from collections import defaultdict

component_store_api = APIRouter(prefix="/component-store",tags=["component_store"])

def open_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data["file_path"] = file_path
    return data

@component_store_api.get("/list")
async def scm_store():
    settings = get_settings()
    store_dir = settings.STORE_DIR
    file_list = glob.glob(f"{store_dir}/*/*/*/install.json")
    file_list = [open_file(file) for file in file_list]
    file_dict = defaultdict(list)
    for item in file_list:
        if "script" in item["file_path"]:
            file_dict["script"].append(item)
        elif "software" in item["file_path"]:
            file_dict["software"].append(item)
        elif "pipeline" in item["file_path"]:
            file_dict["pipeline"].append(item)
        elif "file" in item["file_path"]:
            file_dict["file"].append(item)

    return file_dict
