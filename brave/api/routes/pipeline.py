from fastapi import APIRouter
from importlib.resources import files, as_file
import json
import os
import glob
from brave.api.config.config import get_settings

pipeline = APIRouter()
# BASE_DIR = os.path.dirname(__file__)

@pipeline.get("/get-pipeline/{name}",tags=['pipeline'])
async def get_pipeline(name):
    filename = f"{name}.json"
    json_file = str(files("brave.pipeline.json").joinpath(filename))
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
    data = {
        "path":os.path.basename(item).replace(".json",""),
        "name":data['name'],
        "category":data['category'],
        "img":f"/brave-api/img/{data['img']}",
        "tags":data['tags'],
        "description":data['description'],
        "order":data['order']
    }
    return data



@pipeline.get("/list-pipeline",tags=['pipeline'])
async def get_pipeline():
    json_file = str(files("brave.pipeline.config").joinpath("config.json"))
    with open(json_file,"r") as f:
        config = json.load(f)

    pipeline_files = files("brave.pipeline.json")
    pipeline_files = [get_pipeline_one(str(item)) for item in pipeline_files.iterdir()]
    pipeline_files = sorted(pipeline_files, key=lambda x: x["order"])
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


def get_pipeline_file(filename):
    filename = f"{filename}.nf"
    pipeline_file = str(files("brave.pipeline.nextflow").joinpath(filename))
    if not os.path.exists(pipeline_file):
        raise HTTPException(status_code=500, detail=f"{pipeline_file}不存在!")
    return pipeline_file

def get_downstream_analysis(item):
    with open(item,"r") as f:
        data = json.load(f)
    file_list = [
        item
        for d in data['items']
        if "downstreamAnalysis" in d
        for item in d['downstreamAnalysis']
    ]

    return file_list

@pipeline.get("/find_downstream_analysis/{analysis_method}",tags=['pipeline'])
def get_downstream_analysis_list(analysis_method):
    settings = get_settings()
    pipeline_dir = settings.PIPELINE_DIR
    json_file_list = glob.glob(f"{pipeline_dir}/json/*")
    downstream_list = [get_downstream_analysis(item) for item in json_file_list]
    downstream_list = [item for sublist in downstream_list for item in sublist]
    downstream_dict = {item['saveAnalysisMethod']: item for item in downstream_list}
    return downstream_dict[analysis_method]
    
