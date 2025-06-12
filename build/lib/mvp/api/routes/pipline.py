from fastapi import APIRouter
from importlib.resources import files
import json
import os
pipline = APIRouter()
# BASE_DIR = os.path.dirname(__file__)

@pipline.get("/get-pipline/{name}",tags=['pipline'])
async def get_pipline(name):
    filename = f"{name}.json"
    json_file = str(files("mvp.pipline").joinpath(filename))
    data = {
        "files":json_file,
        "exists":os.path.exists(json_file)
    }
    if os.path.exists(json_file):
        with open(json_file,"r") as f:
            json_data = json.load(f)
            data.update(json_data)
    return data