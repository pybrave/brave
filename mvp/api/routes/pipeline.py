from fastapi import APIRouter
from importlib.resources import files
import json
import os
import glob
pipeline = APIRouter()
# BASE_DIR = os.path.dirname(__file__)

@pipeline.get("/get-pipeline/{name}",tags=['pipeline'])
async def get_pipeline(name):
    filename = f"{name}.json"
    json_file = str(files("mvp.pipeline.json").joinpath(filename))
    data = {
        "files":json_file,
        "exists":os.path.exists(json_file)
    }
    if os.path.exists(json_file):
        with open(json_file,"r") as f:
            json_data = json.load(f)
            data.update(json_data)
    return data

def get_pipeline_one(item):
    with open(item,"r") as f:
        data = json.load(f)
    return {
        "path":os.path.basename(item).replace(".json",""),
        "name":data['name'],
        "category":data['category'],
        "img":f"/mvp-api/img/{data['img']}",
        "tags":data['tags']
    }
@pipeline.get("/list-pipeline",tags=['pipeline'])
async def get_pipeline():
    json_file = str(files("mvp.pipeline.config").joinpath("config.json"))
    with open(json_file,"r") as f:
        config = json.load(f)

    pipeline_files = files("mvp.pipeline.json")
    pipeline_files = [get_pipeline_one(str(item)) for item in pipeline_files.iterdir()]
    # glob.glob("")
    # data  = [
    #     {
    #         "path":"reads-based-abundance-analysis2",
            
    #     }
    # ]
    return {
        "pipeline":pipeline_files,
        "config":config
    }