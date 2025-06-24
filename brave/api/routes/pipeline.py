from fastapi import APIRouter
from importlib.resources import files, as_file

import json
import os
import glob
from brave.api.config.config import get_settings
from brave.api.service.pipeline import get_pipeline_dir,get_pipeline_list
from collections import defaultdict

pipeline = APIRouter()
# BASE_DIR = os.path.dirname(__file__)

@pipeline.get("/get-pipeline/{name}",tags=['pipeline'])
async def get_pipeline(name):
    pipeline_dir =  get_pipeline_dir()
    # filename = f"{name}.json"
    json_file = f"{pipeline_dir}/{name}/main.json"
    data = {
        "files":json_file,
        # "wrapAnalysisPipeline":name,
        "exists":os.path.exists(json_file)
    }
    if os.path.exists(json_file):
        with open(json_file,"r") as f:
            json_data = json.load(f)
            data.update(json_data)
    return data


def get_config():
    pipeline_dir =  get_pipeline_dir()
    config = f"{pipeline_dir}/config.json"
    if os.path.exists(config):
        with open(config,"r") as f:
            return json.load(f)
    else:
        return {}
    
def get_pipeline_one(item):
    with open(item,"r") as f:
        data = json.load(f)
    data = {
        "path":os.path.basename(os.path.dirname(item)),
        "name":data['name'],
        "category":data['category'],
        "img":f"/brave-api/img/{data['img']}",
        "tags":data['tags'],
        "description":data['description'],
        "order":data['order']
    }
    return data

def get_category(name,key):
    config = get_config()
    if "category" in config:
        category = config['category']
        if name in category:
            return category[name][key]
    return name



@pipeline.get("/list-pipeline",tags=['pipeline'])
async def get_pipeline():
    # json_file = str(files("brave.pipeline.config").joinpath("config.json"))
    # with open(json_file,"r") as f:
    #     config = json.load(f)
    # pipeline_files = files("brave.pipeline")
    pipeline_files = get_pipeline_list()
    pipeline_files = [get_pipeline_one(str(item)) for item in pipeline_files]
    pipeline_files = sorted(pipeline_files, key=lambda x: x["order"])
    grouped = defaultdict(list)
    for item in pipeline_files:
        grouped[item["category"]].append(item)

    result = []


    for category, items in grouped.items():
        result.append({
            "name": get_category(category,"name"),
            # "chineseName": category_name_map.get(category, ""),
            "items": items
        })


    # glob.glob("")
    # data  = [
    #     {
    #         "path":"reads-based-abundance-analysis2",
            
    #     }
    # ]
    return result


def get_pipeline_file(filename):
    nextflow_dict = get_all_pipeline()
    if filename not in nextflow_dict:
        raise HTTPException(status_code=500, detail=f"{filename}不存在!")  
    return nextflow_dict[filename]

def get_all_pipeline():
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/*/nextflow/*.nf")
    nextflow_dict = {os.path.basename(item).replace(".nf",""):item for item in nextflow_list}
    return nextflow_dict



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
    pipeline_files = get_pipeline_list()
    downstream_list = [get_downstream_analysis(item) for item in pipeline_files]
    downstream_list = [item for sublist in downstream_list for item in sublist]
    downstream_dict = {item['saveAnalysisMethod']: item for item in downstream_list  if 'saveAnalysisMethod' in item}
    return downstream_dict[analysis_method]
    
