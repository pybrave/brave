from fastapi import APIRouter,HTTPException
from importlib.resources import files, as_file

import json
import os
import glob
from brave.api.config.config import get_settings
from brave.api.service.pipeline import get_pipeline_dir,get_pipeline_list
from collections import defaultdict
from brave.api.models.core import t_pipeline_components,t_pipeline_components_relation
import uuid
from brave.api.config.db import get_engine
from sqlalchemy import select, and_, join, func,insert,update
import re
from brave.api.schemas.pipeline import SavePipeline,Pipeline,QueryPipeline,QueryModule,SavePipelineRelation
import brave.api.service.pipeline  as pipeline_service
from sqlalchemy import  Column, Integer, String, Text, select, cast, null,text
from sqlalchemy.orm import aliased
from sqlalchemy.sql import union_all
import brave.api.utils.service_utils  as service_utils
import asyncio
import time
from starlette.concurrency import run_in_threadpool
from typing import List

pipeline = APIRouter()

def camel_to_snake(name):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# pipeline,software,file,downstream
# BASE_DIR = os.path.dirname(__file__)
@pipeline.post("/import-pipeline",tags=['pipeline'])
async def get_pipeline():
    pipeline_files = get_pipeline_list()
    new_pipeline_components_list = [] 
    new_pipeline_components_relation_list = []
    with get_engine().begin() as conn:
        pipeline_list = find_db_pipeline(conn, "pipeline")
        db_pipeline_key_list = [item.install_key for item in pipeline_list ]
        for pipeline_item_file in pipeline_files:
            json_data = get_pipeine_content(pipeline_item_file)
            install_key = os.path.basename( os.path.dirname(pipeline_item_file))
            if install_key in db_pipeline_key_list:
                continue
            pipeline_item = {k:v for k,v in json_data.items() if  k !="items"}
            pipeline_components_id =install_key# str(uuid.uuid4())
            # pipeline_id  = pipeline_components_id
            new_pipeline_components_list.append({
                "component_id":pipeline_components_id,
                "install_key":install_key,
                # "pipeline_key":wrap_pipeline_key,
                # "parent_pipeline_id":"0",
                "component_type":"pipeline",
                "content":json.dumps(pipeline_item)
            })

            keys_to_remove = [ 'inputFile','outputFile']
            for analysis_software in json_data['items']:
                analysis_software_ = {k:v for k,v in analysis_software.items() if  k not in keys_to_remove}
                analysis_software_uuid = str(uuid.uuid4())
                new_pipeline_components_list.append({
                    "component_id":analysis_software_uuid,
                    "install_key":install_key,
                    # "parent_pipeline_id":wrap_pipeline_uuid,
                    # "pipeline_key":wrap_pipeline_key,
                    "component_type":"software",
                    "content":json.dumps(analysis_software_)
                })
                new_pipeline_components_relation_list.append({
                    "relation_type":"pipeline_software",
                    "install_key":install_key,
                    "component_id":analysis_software_uuid,
                    "parent_component_id":pipeline_components_id,
                    # "pipeline_id":pipeline_id
                })
                for key in keys_to_remove:
                    add_analysis_file( analysis_software_uuid,install_key,analysis_software,key,new_pipeline_components_list,new_pipeline_components_relation_list)
                # key= "parseAnalysisResultModule"
        insert_stmt = insert(t_pipeline_components).values(new_pipeline_components_list)
        conn.execute(insert_stmt)
        insert_stmt = insert(t_pipeline_components_relation).values(new_pipeline_components_relation_list)
        conn.execute(insert_stmt)
        return {
            "pipeline":new_pipeline_components_list,
            "relation_pipeline":new_pipeline_components_relation_list
        }
        

def add_analysis_file(analysis_software_uuid,install_key,pipeline_item,key,new_pipeline_components_list,new_pipeline_components_relation_list):
    if key in pipeline_item:
              
        for analysis_file in pipeline_item[key]:
            analysis_file_uuid = str(uuid.uuid4())  
            # if key=='downstreamAnalysis':
            analysis_file_ = {k:v for k,v in analysis_file.items() if  k !="downstreamAnalysis"}
            new_pipeline_components_list.append({
                "component_id":analysis_file_uuid,
                "install_key":install_key,
                # "parent_pipeline_id":pipeline_uuid,
                # "pipeline_key":wrap_pipeline_key,
                "component_type":"file",
                "content":json.dumps(analysis_file_)
            })
            if key=="inputFile":
                new_pipeline_components_relation_list.append({
                    "relation_type":"software_input_file",
                    "install_key":install_key,
                    "component_id":analysis_file_uuid,
                    # "pipeline_id":pipeline_id,
                    "parent_component_id":analysis_software_uuid
                }) 
            elif  key=="outputFile":
                new_pipeline_components_relation_list.append({
                    "relation_type":"software_ouput_file",
                    "install_key":install_key,
                    "component_id":analysis_file_uuid,
                    # "pipeline_id":pipeline_id,
                    "parent_component_id":analysis_software_uuid
                })
            if "downstreamAnalysis" in analysis_file:
                for downstream_analysis in analysis_file["downstreamAnalysis"]:
                    downstream_analysis_uuid = str(uuid.uuid4()) 
                    new_pipeline_components_list.append({
                        "component_id":downstream_analysis_uuid,
                        "install_key":install_key,
                        # "parent_pipeline_id":item_uuid,
                        # "pipeline_key":wrap_pipeline_key,
                        "component_type":"downstream",
                        "content":json.dumps(downstream_analysis)
                    })
                    new_pipeline_components_relation_list.append({
                        "relation_type":"file_downstream",
                        # "pipeline_id":pipeline_id,
                        "install_key":install_key,
                        "component_id":downstream_analysis_uuid,
                        "parent_component_id":analysis_file_uuid
                    })

            # else:
            # new_pipeline_list.append({
            #     "pipeline_id":item_uuid,
            #     "parent_pipeline_id":pipeline_uuid,
            #     "pipeline_key":wrap_pipeline_key,
            #     "pipeline_type":camel_to_snake(key),
            #     "content":json.dumps(item)
            # })

def find_db_pipeline(conn, component_type):
    return conn.execute(t_pipeline_components.select() 
        .where(t_pipeline_components.c.component_type==component_type)).fetchall()

@pipeline.get("/get-pipeline/{name}",tags=['pipeline'])
async def get_pipeline(name):
    pipeline_dir =  get_pipeline_dir()
    

    # filename = f"{name}.json"
    json_file = f"{pipeline_dir}/{name}/main.json"
    data = {
        # "files":json_file,
        # # "wrapAnalysisPipeline":name,
        # "exists":os.path.exists(json_file)
    }
    if os.path.exists(json_file):
        json_data = get_pipeine_content(json_file)
        data.update(json_data)
    return data

def get_pipeline_item(item):
    content= json.loads(item.content)
    return {
        "id":item.id,
        "pipeline_id":item.pipeline_id,
        "pipeline_key":item.pipeline_key,
        "parent_pipeline_id":item.parent_pipeline_id,
        "pipeline_order":item.pipeline_order,
        "pipeline_type":item.pipeline_type,
        **content
    }



@pipeline.get("/get-pipeline-v2/{name}",tags=['pipeline'])
async def get_pipeline_v2(name):
   # 创建递归 CTE
    base = select(
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.install_key,
        t_pipeline_components.c.content,
        cast(null(), String).label("relation_type"),
        cast(null(), String).label("parent_component_id"),
        # cast(null(), String).label("pipeline_id"),
        cast(null(), String).label("relation_id")
    ).where(
        t_pipeline_components.c.component_id == name,
        t_pipeline_components.c.component_type == "pipeline"
    )

    # 递归部分
    tp2 = aliased(t_pipeline_components)
    trp = t_pipeline_components_relation
    fp = aliased(t_pipeline_components)

    recursive = select(
        tp2.c.component_id,
        tp2.c.component_type,
        tp2.c.install_key,
        tp2.c.content,
        trp.c.relation_type,
        trp.c.parent_component_id,
        # trp.c.pipeline_id ,
        trp.c.relation_id
    ).join(trp, tp2.c.component_id == trp.c.component_id) \
    .join(fp, fp.c.component_id == trp.c.parent_component_id) 
    # .where(trp.c.pipeline_id == name) 

    # union_all 并组成 CTE
    cte = base.union_all(recursive).cte("full_pipeline", recursive=True)

    # 查询最终结果
    final_query = select(cte)


    # 执行查询
    with get_engine().begin() as conn:
        data = conn.execute(final_query).mappings().all()
        
    id_to_node = {item["component_id"]: get_one_data(item) for item in data}
    children_map = defaultdict(list)
    for item in data:
        pid = item.get("parent_component_id")
        if pid:
            children_map[pid].append(item["component_id"])
    # 获取根 pipeline_id
    root_id = next((item["component_id"] for item in data if item["component_type"] == "pipeline"),None)
    if not root_id:
        raise HTTPException(status_code=500, detail=f"{name}没有找到!")  
        
    result = build_pipeline_structure(id_to_node,children_map,root_id)
    return result

def get_one_data(item):
    content = json.loads(item["content"])
    item = {k:v for k,v in item.items() if k!="content"}
    return {**item, **content }

def build_pipeline_structure(id_to_node,children_map,pid):
    node = id_to_node[pid]
    result = {**node}
    items = []
    for child_id in children_map.get(pid, []):
        child = id_to_node[child_id]
        content = child
        if child["component_type"] == "software":
            item = {**content}
            input_files = []
            output_files = []
            for sub_id in children_map.get(child_id, []):
                sub = id_to_node[sub_id]
                sub_content = sub
                if sub["relation_type"] == "software_input_file":
                    input_files.append(sub_content)
                elif sub["relation_type"] == "software_ouput_file":
                    sub_out = {**sub_content, "downstreamAnalysis": []}
                    for ds_id in children_map.get(sub["component_id"], []):
                        downstream = id_to_node[ds_id]
                        sub_out["downstreamAnalysis"].append(downstream)
                    output_files.append(sub_out)


            if input_files:
                item["inputFile"] = input_files
            if output_files:
                item["outputFile"] = output_files
            if "upstreamFormJson" in content:
                item["upstreamFormJson"] = content["upstreamFormJson"]
            items.append(item)
    if items:
        result["items"] = items
    return result


@pipeline.get("/get-pipeline-v3/{name}",tags=['pipeline'])
async def get_pipeline_v3(name):
    with get_engine().begin() as conn:
        pipeline_list = conn.execute(t_pipeline.select() 
            .where(t_pipeline.c.pipeline_key==name)).fetchall()
        # wrap_pipeline = [item for item in pipeline_list if item.pipeline_type=='wrap_pipeline']
        data = [get_pipeline_item(item) for item in pipeline_list]
   
        wrap = next(d for d in data if d["pipeline_type"] == "wrap_pipeline")
        sub_pipelines = [d for d in data if d["pipeline_type"] == "pipeline" and d["parent_pipeline_id"] == wrap["pipeline_id"]]
        items = []
        for sub in sub_pipelines:
            parent_id = sub["pipeline_id"]
            # parseAnalysisResultModule = [
            #     d for d in data if d["pipeline_type"] == "parse_analysis_result_module" and d["parent_pipeline_id"] == parent_id
            # ]
            # inputAnalysisMethod = [
            #     d for d in data if d["pipeline_type"] == "input_analysis_method" and d["parent_pipeline_id"] == parent_id
            # ]
            # # upstreamFormJson = [
            # #     d for d in data if d["pipeline_type"] == "upstream_form_json" and d["parent_pipeline_id"] == parent_id
            # # ]
            # analysisMethod = [
            #     d for d in data if d["pipeline_type"] == "analysis_method" and d["parent_pipeline_id"] == parent_id
            # ]

            # downstreamAnalysis 有 formJson 嵌套，要特殊处理
            downstreamAnalysis = [
                d for d in data if d["pipeline_type"] == "downstream_analysis" and d["parent_pipeline_id"] == parent_id
            ]
            # downstreamAnalysis = []
            # for d in downstream_raw:
            #     entry = {k: d[k] for k in d if k != "formJson"}
            #     # 查找 formJson 子项
            #     children = [
            #         f for f in data if f.get("pipeline_type") == "form_json" and f["parent_pipeline_id"] == d["pipeline_id"]
            #     ]
            #     if children:
            #         entry["formJson"] = children
            #     downstreamAnalysis.append(entry)
            
            items.append({
                # "name": sub["name"],
                # "analysisPipline": sub.get("analysisPipline"),
                # "parseAnalysisModule": sub.get("parseAnalysisModule"),
                **sub,
                # "parseAnalysisResultModule": parseAnalysisResultModule,
                # "inputAnalysisMethod": inputAnalysisMethod,
                # # "upstreamFormJson": upstreamFormJson,
                # "analysisMethod": analysisMethod,
                "downstreamAnalysis": downstreamAnalysis
            })

    result = {
        **wrap,
        "items": items
    }
    return result
     # with open("test/file.json","w") as f:
        #     f.write(json.dumps(pipeline_list))
    
@pipeline.post("/get-module-content",tags=['pipeline'])
async def get_module_content(queryModule:QueryModule):
    module_dir = queryModule.pipeline_id
    if queryModule.module_dir:
        module_dir = queryModule.module_dir
    py_module = pipeline_service.find_module(queryModule.module_type,module_dir,queryModule.module_name)
    return py_module
    

def get_pipeine_content(json_file):
    markdown_dict = get_all_markdown()
    with open(json_file,"r") as f:
        json_data = json.load(f)
        # update_downstream_markdown(json_data.items)
        for item1 in  json_data['items']:
            if "markdown" in item1:
                content = get_markdown_content(markdown_dict,item1['markdown'] )
                item1['markdown'] = content
            if "downstreamAnalysis" in item1:
                for item2 in item1['downstreamAnalysis']:
                    if "markdown" in item2:
                        content = get_markdown_content(markdown_dict,item2['markdown'] )
                        item2['markdown'] = content
    return json_data

def get_config():
    pipeline_dir =  get_pipeline_dir()
    config = f"{pipeline_dir}/config.json"
    if os.path.exists(config):
        with open(config,"r") as f:
            return json.load(f)
    else:
        return {}
    

def get_category(name,key):
    config = get_config()
    if "category" in config:
        category = config['category']
        if name in category:
            return category[name][key]
    return name

def get_pipeline_one_v2(item):
    try:
        data = json.loads(item.content)
        result = {
            "id":item.id,
            "component_id":item.component_id,
            "path":item.component_id,
            "name":data['name'],
            "category":data['category'],
            "img":f"/brave-api/img/{data['img']}",
            "tags":data['tags'],
            "description":data['description'] if 'description' in data else "",
            "order":item.order_index
        }
        return  result
    except (ValueError, TypeError):
        return {
            "id":item.id,
            "pipeline_id":item.component_id,
            "path":item.component_id,
            "name":"unkonw",
            "category":"unkonw",
            "img":f"/brave-api/img/unkonw",
            "tags":["unkonw"],
            "description":"unkonw",
            "order":item.order_index
        }       
@pipeline.get("/list-pipeline-v2",tags=['pipeline'])
async def list_pipeline_v2():
    with get_engine().begin() as conn:
        wrap_pipeline_list = find_db_pipeline(conn, "pipeline")
        pipeline_list = [get_pipeline_one_v2(item) for item in wrap_pipeline_list]
        pipeline_list = sorted(pipeline_list, key=lambda x:x["order"] if x["order"] is not None else x["id"])
    
    grouped = defaultdict(list)
    for item in pipeline_list:
        grouped[item["category"]].append(item)

    result = []
    for category, items in grouped.items():
        result.append({
            "name": get_category(category,"name"),
            "items": items
        })
    return result
    # pass

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

# @pipeline.get("/list-pipeline",tags=['pipeline'])
# async def get_pipeline():
#     # json_file = str(files("brave.pipeline.config").joinpath("config.json"))
#     # with open(json_file,"r") as f:
#     #     config = json.load(f)
#     # pipeline_files = files("brave.pipeline")
#     pipeline_files = get_pipeline_list()
#     pipeline_files = [get_pipeline_one(str(item)) for item in pipeline_files]
#     pipeline_files = sorted(pipeline_files, key=lambda x: x["order"])
#     grouped = defaultdict(list)
#     for item in pipeline_files:
#         grouped[item["category"]].append(item)

#     result = []
#     for category, items in grouped.items():
#         result.append({
#             "name": get_category(category,"name"),
#             "items": items
#         })
#     return result


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



def get_all_markdown():
    pipeline_dir =  get_pipeline_dir()
    markdown_list = glob.glob(f"{pipeline_dir}/*/markdown/*.md")
    markdown_dict = {os.path.basename(item).replace(".md",""):item for item in markdown_list}
    return markdown_dict

def get_markdown_content(markdown_dict,name):
    markdown_file = markdown_dict[name]
    with open(markdown_file,"r") as f:
        content = f.read()
    return content

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
async def get_downstream_analysis_list(analysis_method):
    pipeline_files = get_pipeline_list()
    downstream_list = [get_downstream_analysis(item) for item in pipeline_files]
    downstream_list = [item for sublist in downstream_list for item in sublist]
    downstream_dict = {item['saveAnalysisMethod']: item for item in downstream_list  if 'saveAnalysisMethod' in item}
    return downstream_dict[analysis_method]
    
@pipeline.post("/find-pipeline",tags=['pipeline'],response_model=Pipeline)
async def find_pipeline_by_id(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.find_pipeline_by_id(conn,queryPipeline.component_id)

@pipeline.post("/list-pipeline-components",tags=['pipeline'],response_model=list[Pipeline])
async def list_pipeline(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.list_pipeline(conn,queryPipeline)


def get_pipeline_id_by_parent_id(conn, start_id: str) -> str | None:
    sql = text("""
        WITH RECURSIVE ancestor_path AS (
            SELECT
                pipeline_id,
                parent_pipeline_id,
                relation_type
            FROM relation_pipeline
            WHERE pipeline_id = :start_id

            UNION ALL

            SELECT
                rp.pipeline_id,
                rp.parent_pipeline_id,
                rp.relation_type
            FROM relation_pipeline rp
            JOIN ancestor_path ap ON rp.pipeline_id = ap.parent_pipeline_id
        )
        SELECT pipeline_id
        FROM ancestor_path
        WHERE relation_type = 'pipeline_software'
        LIMIT 1;
    """)

    result = conn.execute(sql, {"start_id": start_id})
    row = result.first()
    return row[0] if row else None

@pipeline.post("/find-pipeline-relation/{relation_id}",tags=['pipeline'])
async def find_pipeline_relation(relation_id):
    with get_engine().begin() as conn:    
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
        return conn.execute(stmt).mappings().first()


@pipeline.post("/save-pipeline-relation",tags=['pipeline'])
async def save_pipeline(savePipelineRelation:SavePipelineRelation):
    save_pipeline_relation_dict = savePipelineRelation.dict()
    save_pipeline_relation_dict = {k:v for k,v in save_pipeline_relation_dict.items() if k!="pipeline_id"}
    with get_engine().begin() as conn:  
        # if not savePipelineRelation.relation_id:
            

        # if savePipelineRelation.relation_type == 'pipeline_software':
        #     # stmt = t_relation_pipeline.select().where(t_relation_pipeline.c.parent_pipeline_id == savePipelineRelation.parent_pipeline_id )
        #     # find_relation = conn.execute(stmt).fetchone()
        #     first_pipeline_id =  savePipelineRelation.parent_component_id

        # else:
        #     first_pipeline_id = get_pipeline_id_by_parent_id(conn, savePipelineRelation.parent_component_id)

        if savePipelineRelation.relation_id:
            stmt = t_pipeline_components_relation.update().values(save_pipeline_relation_dict).where(t_pipeline_components_relation.c.relation_id==savePipelineRelation.relation_id)
        else:
            stmt = t_pipeline_components_relation.insert().values(save_pipeline_relation_dict)
        conn.execute(stmt)

        stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==savePipelineRelation.component_id)
        find_pipeine = conn.execute(stmt).fetchone()
        pipeline_service.create_wrap_pipeline_dir(savePipelineRelation.pipeline_id)
        content = json.loads(find_pipeine.content)
        # pipeline_service.create_file(savePipelineRelation.pipeline_id, find_pipeine.component_type,content)
        return {"message":"success"}

@pipeline.post("/save-pipeline",tags=['pipeline'])
async def save_pipeline(savePipeline:SavePipeline):
    
 
    save_pipeline_dict = savePipeline.dict()
    
    with get_engine().begin() as conn:
        find_pipeine = None
        if savePipeline.component_id:
            stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==savePipeline.component_id)
            find_pipeine = conn.execute(stmt).fetchone()
            component_id = find_pipeine.component_id
            if not find_pipeine:
                raise HTTPException(status_code=500, detail=f"根据{savePipeline.component_id}不能找到记录!")

        if find_pipeine:
            save_pipeline_dict = {k:v for k,v in save_pipeline_dict.items() if k!="component_id" and v is not  None} 
            stmt = t_pipeline_components.update().values(save_pipeline_dict).where(t_pipeline_components.c.component_id==savePipeline.component_id)
        else:
            str_uuid = str(uuid.uuid4())  
            save_pipeline_dict['component_id'] = str_uuid
            component_id = str_uuid
          
            stmt = t_pipeline_components.insert().values(save_pipeline_dict)
        conn.execute(stmt)

    
    # t0 = time.time()
    if savePipeline.component_type=="pipeline":
        await run_in_threadpool(create_pipeline_dir, component_id, savePipeline)

    # await asyncio.sleep(0.5)
    # print("文件创建耗时", time.time() - t0)

    return {"message":"success"}


def create_pipeline_dir(component_id,savePipeline):
    pipeline_service.create_wrap_pipeline_dir(component_id)
    content = json.loads(savePipeline.content)
    pipeline_service.create_file(component_id,savePipeline.component_type,content)


@pipeline.delete("/delete-pipeline-relation/{relation_id}")
async def delete_user(relation_id: str):
    with get_engine().begin() as conn:
        stmt = t_pipeline_components_relation.delete().where(t_pipeline_components_relation.c.relation_id == relation_id)
        conn.execute(stmt)
        return {"message":"success"}



@pipeline.delete("/delete-pipeline/{pipeline_id}")
async def delete_user(pipeline_id: str):
    with get_engine().begin() as conn:
        stmt = t_pipeline.select().where(t_pipeline.c.parent_pipeline_id ==pipeline_id)
        find_pipeine = conn.execute(stmt).fetchone()

        if  find_pipeine:
            raise HTTPException(status_code=500, detail=f"不能删除存在关联!") 
        else:
            stmt = t_pipeline.delete().where(t_pipeline.c.pipeline_id == pipeline_id)
            conn.execute(stmt)
            pipeline_service.delete_wrap_pipeline_dir(pipeline_id)
            return {"message":"success"}
