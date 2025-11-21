from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends,HTTPException
from importlib.resources import files, as_file

import json
import os
import glob
from brave.api.config.config import get_settings
from brave.api.enum.component_script import ScriptName
from brave.api.service.pipeline import get_pipeline_dir,get_pipeline_list
from brave.api.service import component_store_service

from collections import defaultdict
from brave.api.models.core import t_pipeline_components,t_pipeline_components_relation
import uuid
from brave.api.config.db import get_engine
from sqlalchemy import or_, select, and_, join, func,insert,update
import re
from brave.api.schemas.pipeline import InstallComponent, PagePipelineQuery, PublishComponent, SavePipeline,Pipeline,QueryPipeline,QueryModule, SavePipelineComponentsEdges,SavePipelineRelation,SaveOrder
import brave.api.service.pipeline  as pipeline_service
from sqlalchemy import  Column, Integer, String, Text, select, cast, null,text,case
from sqlalchemy.orm import aliased
from sqlalchemy.sql import union_all
from brave.api.service.sse_service import SSESessionService
import brave.api.utils.service_utils  as service_utils
import asyncio
import time
from starlette.concurrency import run_in_threadpool
from typing import List
import brave.api.service.container_service as container_service
from brave.app_container import AppContainer
import brave.api.service.notebook as notebook_service
import shutil
from fastapi import  File, UploadFile
import shutil
import time
from brave.api.executor.base import JobExecutor


pipeline = APIRouter()

def camel_to_snake(name):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# pipeline,software,file,downstream
# BASE_DIR = os.path.dirname(__file__)
@pipeline.post("/import-pipeline",tags=['pipeline'])
async def import_pipeline():
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
                    "relation_type":"software_output_file",
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
                        "relation_type":"file_script",
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

def format_content(item):
    item = dict(item)
    item = {
        **{k:v for k,v in item.items() if k != "content"},
        **json.loads(item["content"])
    }
    return item
    # pass

@pipeline.get("/get-component-parent/{component_id}",tags=['pipeline'])
async def get_component_parent(component_id,component_type):
    

    base = select(
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.content,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.tags,
        t_pipeline_components.c.description,
        t_pipeline_components.c.file_type,
        t_pipeline_components.c.script_type,
        cast(null(), String(255)).label("relation_type"),
        cast(null(), String(255)).label("parent_component_id"),
        cast(null(), Integer).label("order_index"),
        cast(null(), String(255)).label("relation_id"),
    ).where(
        t_pipeline_components.c.component_id == component_id,
        t_pipeline_components.c.component_type == component_type,
    )

    tp1 = aliased(t_pipeline_components)
    rel = t_pipeline_components_relation
    # fp = aliased(cte)  # 引用递归CTE自身
    # base_alias = base.alias()

    stmt_parenet = select(
        tp1.c.component_id,
        tp1.c.component_type,
        tp1.c.content,
        tp1.c.component_name,
        tp1.c.tags,
        cast(null(), String(255)).label("description"),
        tp1.c.file_type,
        tp1.c.script_type,
        rel.c.relation_type,
        rel.c.parent_component_id,
        rel.c.order_index,
        rel.c.relation_id,
    ).select_from(
        tp1.join(rel, tp1.c.component_id == rel.c.parent_component_id)
    ).where(
        rel.c.component_id == component_id
    )

    # # 合并 base 和 recursive，生成完整的递归CTE
    stmt = base.union_all(stmt_parenet) 
    with get_engine().begin() as conn:
        data = conn.execute(stmt).mappings().all()
    child_item  = next((item for item in data if item["component_type"] == component_type),None)
    if not child_item:
        raise HTTPException(status_code=500, detail=f"{component_id}没有找到!")  

    if component_type == "script":
        child_item = {
            **child_item,
            **json.loads(child_item["content"])
        }
        del child_item["content"]

    parent_item_list = [format_content(item) for item in data if item['component_type'] != component_type]
    # resul_dict= {}
    # resul_dict['script'] = dict(child_item)
    child_item['parent'] = parent_item_list
    return child_item


@pipeline.get("/get-pipeline-dag/{pipeline_id}",tags=['pipeline'])
async def get_pipeline_dag(pipeline_id):
    s_alias = t_pipeline_components.alias("s")
    t_alias = t_pipeline_components.alias("t")
    stmt1 = (
        select(
            t_pipeline_components_relation.c.parent_component_id.label("source"),
            t_pipeline_components_relation.c.component_id.label("target"),
            s_alias.c.component_name.label("source_name"),
            t_alias.c.component_name.label("target_name"),
        )
        .select_from(
            t_pipeline_components_relation
            .join(s_alias, t_pipeline_components_relation.c.parent_component_id == s_alias.c.component_id)
            .join(t_alias, t_pipeline_components_relation.c.component_id == t_alias.c.component_id)
        )
        .where(
            and_(
                t_pipeline_components_relation.c.relation_type == "pipeline_software",
                t_pipeline_components_relation.c.pipeline_id == pipeline_id
            )
        )
    )
    stmt2 = (
        select(t_pipeline_components)
        .distinct()
        .select_from(
            t_pipeline_components_relation
            .join(
                t_pipeline_components,
                or_(
                    t_pipeline_components.c.component_id == t_pipeline_components_relation.c.parent_component_id,
                    t_pipeline_components.c.component_id == t_pipeline_components_relation.c.component_id
                )
            )
        )
        .where(
            and_(
                t_pipeline_components_relation.c.relation_type == "pipeline_software",
                t_pipeline_components_relation.c.pipeline_id == pipeline_id
            )
        )
    )
    stmt3 = select(t_pipeline_components).where(t_pipeline_components.c.component_id == pipeline_id)
    with get_engine().begin() as conn:
        data = conn.execute(stmt1).mappings().all()
        data2 = conn.execute(stmt2).mappings().all()
        data3 = conn.execute(stmt3).mappings().first()
    return {
        **data3,
        "edges":data,
        "nodes":data2
    }

@pipeline.get("/get-pipeline-v2/{name}",tags=['pipeline'])
async def get_pipeline_v2(name,component_type="pipeline"):
    with get_engine().begin() as conn:
        return pipeline_service.get_pipeline_v2(conn,name,component_type)


  
@pipeline.get("/get-component-module-content/{component_id}",tags=['pipeline'])
async def get_module_content(component_id,script_name:ScriptName):
    # module_dir = queryModule.component_id
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    # if queryModule.module_dir:
    #     module_dir = queryModule.module_dir
    module_info:dict = pipeline_service.find_component_module(find_component,script_name)
    # py_module_path = py_module['path']
    if module_info and os.path.exists(module_info['path']):
        with open(module_info['path'],"r") as f:
            module_content = f.read()
    # py_module['content'] = py_module_content
    return {
        "path":module_info['path'], 
        "content":module_content
    }
    

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
        # pipeline_list = sorted(pipeline_list, key=lambda x:x["order"] if x["order"] is not None else x["id"])
    
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
    
@pipeline.post("/find-pipeline",tags=['pipeline'])
async def find_pipeline_by_id(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.find_pipeline_by_id(conn,queryPipeline.component_id)

@pipeline.post("/list-pipeline-components",tags=['pipeline'],response_model=list[Pipeline])
async def list_pipeline(queryPipeline:QueryPipeline):
    with get_engine().begin() as conn:
        return pipeline_service.list_pipeline(conn,queryPipeline)

@pipeline.post("/page-pipeline-components",tags=['pipeline'])
async def page_pipeline(query:PagePipelineQuery ):
    with get_engine().begin() as conn:
        return pipeline_service.page_pipeline(conn,query)


@pipeline.post("/save-pipeline-components-edges",tags=['pipeline'])
async def save_pipeline_components_edges(savePipelineComponentsEdges:SavePipelineComponentsEdges):
    with get_engine().begin() as conn:
        pipeline_service.save_pipeline_components_edges(conn,savePipelineComponentsEdges)
    return {"message":"success"}    

# def get_pipeline_id_by_parent_id(conn, start_id: str) -> str | None:
#     sql = text("""
#         WITH RECURSIVE ancestor_path AS (
#             SELECT
#                 pipeline_id,
#                 parent_pipeline_id,
#                 relation_type
#             FROM relation_pipeline
#             WHERE pipeline_id = :start_id

#             UNION ALL

#             SELECT
#                 rp.pipeline_id,
#                 rp.parent_pipeline_id,
#                 rp.relation_type
#             FROM relation_pipeline rp
#             JOIN ancestor_path ap ON rp.pipeline_id = ap.parent_pipeline_id
#         )
#         SELECT pipeline_id
#         FROM ancestor_path
#         WHERE relation_type = 'pipeline_software'
#         LIMIT 1;
#     """)

#     result = conn.execute(sql, {"start_id": start_id})
#     row = result.first()
#     return row[0] if row else None

@pipeline.post("/find-pipeline-relation/{relation_id}",tags=['pipeline'])
async def find_pipeline_relation(relation_id):
    with get_engine().begin() as conn:    
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
        return conn.execute(stmt).mappings().first()


@pipeline.post("/save-pipeline-relation",tags=['pipeline'])
async def save_pipeline_relation_controller(savePipelineRelation:SavePipelineRelation):
    with get_engine().begin() as conn:  
        await save_pipeline_relation(conn,savePipelineRelation)

        
        return {"message":"success"}

async def save_pipeline_relation(conn,savePipelineRelation):
    save_pipeline_relation_dict = savePipelineRelation.dict()
    # save_pipeline_relation_dict = {k:v for k,v in save_pipeline_relation_dict.items() if k!="pipeline_id"}
    if savePipelineRelation.parent_component_id:
        parent_component = pipeline_service.find_pipeline_by_id(conn,savePipelineRelation.parent_component_id)
        if parent_component:
            component_id = parent_component["component_id"]
    if savePipelineRelation.relation_id:
        stmt = t_pipeline_components_relation.update().values(save_pipeline_relation_dict).where(t_pipeline_components_relation.c.relation_id==savePipelineRelation.relation_id)
    else:
        query_stmt = t_pipeline_components_relation.select().where(
            and_( t_pipeline_components_relation.c.component_id ==  savePipelineRelation.component_id,
                 t_pipeline_components_relation.c.relation_type == savePipelineRelation.relation_type,
                 t_pipeline_components_relation.c.parent_component_id == savePipelineRelation.parent_component_id,)
        )
        exist_relation = conn.execute(query_stmt).fetchone()
        if exist_relation:
            raise HTTPException(status_code=500, detail="This relation already exists and cannot be added again!")
        save_pipeline_relation_dict['relation_id'] = str(uuid.uuid4())
        child_component_count = pipeline_service.get_child_component_count(conn,savePipelineRelation.parent_component_id,savePipelineRelation.relation_type)
        save_pipeline_relation_dict['order_index'] = child_component_count + 1
        stmt = t_pipeline_components_relation.insert().values(save_pipeline_relation_dict)
        conn.execute(stmt)
    
    pipeline_service.write_component_json(component_id)

    # stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==savePipelineRelation.component_id)
    # find_pipeine = conn.execute(stmt).fetchone()
    # await run_in_threadpool(create_pipeline_dir, savePipelineRelation.pipeline_id, find_pipeine.content ,find_pipeine.component_type)
    # pipeline_service.create_wrap_pipeline_dir(savePipelineRelation.pipeline_id)
    # pipeline_service.create_file(savePipelineRelation.pipeline_id, find_pipeine.component_type,content)
    # content = json.loads(find_pipeine.content)


async def update_or_save_components(savePipeline:SavePipeline):
    try:
        json.loads(savePipeline.content)
    except Exception as e:
        # print("component content json error",json.dumps(savePipeline,indent=4))
        # raise HTTPException(status_code=500, detail=f"组件内容不是合法的json格式! 错误信息:{str(e)}")
        raise ValueError(f"The component content is not valid JSON format! Error message:{str(e)}")
 
 
    save_pipeline_dict = savePipeline.dict()
    save_pipeline_dict = {k:v for k,v in save_pipeline_dict.items() if k!="parent_component_id" and k!="pipeline_id" and k!='relation_type' }
    
    with get_engine().begin() as conn:
        find_pipeine = None
        if savePipeline.component_id:
            stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id == savePipeline.component_id)
            find_pipeine = conn.execute(stmt).fetchone()

            if not find_pipeine:
                raise HTTPException(status_code=500, detail=f"根据{savePipeline.component_id}不能找到记录!")
            component_id = find_pipeine.component_id

        if find_pipeine:
            save_pipeline_dict = {k:v for k,v in save_pipeline_dict.items() if k!="component_id" and v is not  None } 
            stmt = t_pipeline_components.update().values(save_pipeline_dict).where(t_pipeline_components.c.component_id==savePipeline.component_id)
            conn.execute(stmt)
            
        else:
           
                
            str_uuid = str(uuid.uuid4())  
            save_pipeline_dict['component_id'] = str_uuid
            component_id = str_uuid
            stmt = t_pipeline_components.insert().values(save_pipeline_dict)
            conn.execute(stmt)
            
            if savePipeline.relation_type:
                await save_pipeline_relation(conn, SavePipelineRelation(
                    component_id=component_id,
                    parent_component_id= savePipeline.parent_component_id,
                    relation_type=savePipeline.relation_type,
                    # pipeline_id=savePipeline.pipeline_id
                ))
    return component_id
@pipeline.post("/save-pipeline",tags=['pipeline'])
async def save_pipeline(savePipeline:SavePipeline):
    component_id = await update_or_save_components(savePipeline)
     
    pipeline_service.write_component_json(component_id)
    # t0 = time.time()
    

    # await asyncio.sleep(0.5)
    # print("文件创建耗时", time.time() - t0)

    return {"message":"success"}

@pipeline.post("/publish-component",tags=['pipeline'])
async def publish_component(publishComponent:PublishComponent):
    setting = get_settings()
    store_path = f"{setting.STORE_DIR}/default"
    if publishComponent.store_path:
        store_path = publishComponent.store_path
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_component_by_id(conn,publishComponent.component_id)
        if not find_component:
            raise HTTPException(status_code=500, detail=f"Cannot find component for {publishComponent.component_id}!")
        publish_component_type = find_component['component_type']
        publish_component_id = find_component['component_id']
        pipeline_dir = pipeline_service.get_pipeline_dir()
        
        component_dir = f"{pipeline_dir}/{publish_component_type}/{publish_component_id}/pipeline_component.json"
        if not os.path.exists(component_dir):
            pipeline_service.write_component_json(publish_component_id)
            # raise HTTPException(status_code=500, detail=f"Component directory {component_dir} does not exist!")

        with open(component_dir,"r") as f:
            component_json = json.load(f)
        for component_item in component_json:
            component_type = component_item["component_type"]
            component_id = component_item["component_id"]
            source_dir = f"{pipeline_dir}/{component_type}/{component_id}"
            target_dir = f"{store_path}/{component_type}/{component_id}"
            if not os.path.exists(source_dir):
                print(f"source dir {source_dir} not exists, skip it!")
                continue
            if os.path.exists(target_dir):
                if publishComponent.force:
                    shutil.rmtree(target_dir)
                    shutil.copytree(source_dir,target_dir)
                    print(f"force publish {source_dir} to {target_dir}")
                else:
                    raise HTTPException(status_code=500, detail=f"Store {target_dir} already exists! If you want to overwrite it, please set force to true.")
            else:
                os.makedirs(os.path.dirname(target_dir),exist_ok=True)
                shutil.copytree(source_dir,target_dir)
                print(f"publish {source_dir} to {target_dir}")

        install_json = {
            "components":{
                "file":[],
                "script":[],
                "software":[],
                "pipeline":[],
            }
        }
        install_file = f"{store_path}/main.json"

        if  os.path.exists(install_file):
            with open(install_file,"r") as f:
                install_json = json.load(f)
  
        for component_item in component_json:
            component_type = component_item["component_type"]
            component_id = component_item["component_id"]
            component_category = component_item.get("category","default")
            component_name = component_item["component_name"]
            order_index = component_item["order_index"]
            if not order_index:
                order_index = 0

            # is_exist = False
            install_json_component_type = install_json["components"][component_type]

            found = False
            for existing_item in install_json_component_type:
                if existing_item["component_id"] == component_id:
                    # ✅ 已存在 → 更新字段
                    existing_item.update({
                        "name": component_name,
                        "category": component_category,
                        "order_index": order_index
                    })
                    found = True
                    break

            if not found:
                # ✅ 不存在 → 添加新项
                install_json_component_type.append({
                    "name": component_name,
                    "component_id": component_id,
                    "category": component_category,
                    "order_index": order_index
                })
            # install_component_id = [ item["component_id"] for item in install_json_component_type ]
            # if component_id not in install_component_id:
            #     install_json["components"][component_type].append({ 
            #                 "name": component_name,
            #                 "component_id": component_id,
            #                 "category": component_category,
            #                 "order_index":order_index
            #         })
            # else:
            #     pass

            # new_install_json_component_type = []
            # for item in install_json_component_type:
            #     if component_id == item["component_id"] :
            #         is_exist = True
            #         # update existing record
            #         item = { 
            #                 "name": component_name,
            #                 "component_id": component_id,
            #                 "category": component_category,
            #                 "order_index":order_index
            #         }

            #     new_install_json_component_type.append(item)

            # if not is_exist:
                # new_install_json_component_type.append({ 
                #             "name": component_name,
                #             "component_id": component_id,
                #             "category": component_category,
                #             "order_index":order_index
                #     })
                    
            

        with open(install_file,"w") as f:
            json.dump(install_json,f)

    return {"message":"success"}

@pipeline.delete("/delete-pipeline-relation/{relation_id}")
async def delete_pipeline_relation(relation_id: str):
    component_id = None
    with get_engine().begin() as conn:
        component_relation = pipeline_service.find_by_relation_id(conn,relation_id)
        if not component_relation:
            raise HTTPException(status_code=500, detail=f"根据{relation_id}不能找到记录!") 
        parent_component = pipeline_service.find_pipeline_by_id(conn,component_relation.parent_component_id)
        if parent_component:
            component_id = parent_component["component_id"]
        stmt = t_pipeline_components_relation.delete().where(t_pipeline_components_relation.c.relation_id == relation_id)
        conn.execute(stmt)
    if component_id:
        pipeline_service.write_component_json(component_id)
    return {"message":"success"}



@pipeline.delete("/delete-component/{component_id}")
async def delete_component(component_id: str):

    with get_engine().begin() as conn:
        find_component = pipeline_service.find_component_by_id(conn,component_id)
        if not find_component:
            raise HTTPException(status_code=500, detail=f"Cannot find component for {component_id}!")
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.parent_component_id ==component_id)
        parent_find_pipeine = conn.execute(stmt).fetchone()
        stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.component_id ==component_id)
        child_find_pipeine = conn.execute(stmt).fetchall()

        if  parent_find_pipeine or child_find_pipeine:
            raise HTTPException(status_code=500, detail=f"Cannot delete because there are existing associations!") 
        else:
            # find_component = pipeline_service.find_component_by_id(conn,component_id)
            stmt = t_pipeline_components.delete().where(t_pipeline_components.c.component_id == component_id)
            conn.execute(stmt)
            # pipeline_service.delete_wrap_pipeline_dir(component_id)

    pipeline_service.delete_component_file(find_component)

    return {"message":"success"}

@pipeline.get("/find-by-component-id/{component_id}",tags=['pipeline'])
async def find_by_components_id(component_id):
    with get_engine().begin() as conn:
        stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id == component_id)
        return conn.execute(stmt).mappings().first()

    
@pipeline.post("/copy-component/{component_id}",tags=['pipeline'])
async def copy_component(component_id):
    pipeline_dir = pipeline_service.get_pipeline_dir()
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_component_by_id(conn,component_id)
        component = dict(find_component)

        component['component_name'] = f"{component['component_name']}_copy"
        component['component_id'] = None
        new_components =  SavePipeline(**component)
        component_id = await update_or_save_components(new_components)

    pipeline_service.copy_component_json(find_component,component_id)
    
    return {"message":"success"}


async def install_github_component(installComponent:InstallComponent):
    force = installComponent.force
    pipeline_dir = pipeline_service.get_pipeline_dir()
    component_path = f"{installComponent.path}/pipeline_component.json?ref={installComponent.branch}"
    components_info =component_store_service.get_github_file_content_by_url(component_path,token=installComponent.token)
    components_info = json.loads(components_info)
    path_list = installComponent.path.split("/")
    install_component_id = path_list[-1]
    install_component_type = path_list[-2]
    source_prefix = installComponent.path.replace(f"/{install_component_type}/{install_component_id}","")

    for install_info in components_info:
        if "component_id" not in install_info:
            raise HTTPException(status_code=500, detail=f"{component_path} is not valid component store!")
        if "component_type" not in install_info:
            raise HTTPException(status_code=500, detail=f"{component_path} is not valid component store!")
        component_id = install_info["component_id"]
        component_type = install_info["component_type"]
        
        target_path = f"{pipeline_dir}/{component_type}/{component_id}"
        source_url = f"{source_prefix}/{component_type}/{component_id}?ref={installComponent.branch}"
        if not os.path.exists(target_path):
            await asyncio.to_thread(component_store_service.download_github_folder,source_url,target_path,installComponent.token)
        
            print("download_github_folder",source_url,target_path)
        else:
            if force:
                shutil.rmtree(target_path)
                # component_store_service.download_github_folder(source_url,target_path,installComponent.token)
                await asyncio.to_thread(component_store_service.download_github_folder,source_url,target_path,installComponent.token)
        
                print("force download_github_folder",source_url,target_path)
    
    install_target_path = f"{pipeline_dir}/{install_component_type}/{install_component_id}"
    with get_engine().begin() as conn:
        pipeline_service.import_component(conn,install_target_path,force)
        pipeline_service.import_component_relation(conn,install_target_path,force)
        container_service.import_container(conn,install_target_path,force)
        # pipeline_service.import_component(conn,path,force)

def install_local_component(installComponent:InstallComponent):
    force = installComponent.force
    pipeline_dir = pipeline_service.get_pipeline_dir()
    with open(installComponent.path,"r") as f:
        data = json.load(f)
    path = os.path.dirname(installComponent.path)


    with get_engine().begin() as conn:
        pipeline_service.import_component(conn,path,force)
        pipeline_service.import_component_relation(conn,path,force)
        container_service.import_container(conn,path,force)

    # install all components
    store_dir  =  os.path.dirname(installComponent.path)
    store_dir = os.path.dirname(store_dir)
    store_dir = os.path.dirname(store_dir)


    with open(f"{path}/pipeline_component.json","r") as f:
        components_list = json.load(f)
    for item in components_list:
        component_id = item["component_id"]
        component_type = item["component_type"]
        source_path = f"{store_dir}/{component_type}/{component_id}"
        install_path = f"{pipeline_dir}/{component_type}/{component_id}"

        if not os.path.exists(install_path):
            # os.makedirs(install_path)
            shutil.copytree(source_path, install_path)
            print("copytree",source_path, install_path)
        else:
            if force:   
                shutil.rmtree(install_path)
                shutil.copytree(source_path, install_path)
                print("force copytree",source_path, install_path)

@pipeline.post("/install-components",tags=['pipeline'])
@inject
async def install_component(installComponent:InstallComponent,
    job_executor:JobExecutor = Depends(Provide[AppContainer.job_executor_selector])
):
    if installComponent.address=="github":
        await install_github_component(installComponent)
    elif installComponent.address=="local":
        install_local_component(installComponent)
    else:
        raise HTTPException(status_code=500, detail=f"Not support {installComponent.address} yet!")
    asyncio.create_task(job_executor.update_images_status())
    return {"message":"success"}

    





@pipeline.get("/get-depend-component/{component_id}",tags=['pipeline'])
async def get_depend_component(component_id):
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn, component_id)
        if not find_component:
            raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
        child_depend_component = pipeline_service.get_child_depend_component(conn, component_id)
        parent_depend_component = pipeline_service.get_parent_depend_component(conn, component_id)
        return list(child_depend_component) + list(parent_depend_component)


@pipeline.post("/save-component-relation-order",tags=['pipeline'])
async def save_component_relation_order(saveOrder:list[SaveOrder]):
    with get_engine().begin() as conn:
        pipeline_service.save_order(conn,saveOrder)
    return {"message":"success"}


@pipeline.post("/update-component-description/{component_id}",tags=['pipeline'])
async def update_component_description(component_id,description ):
    with get_engine().begin() as conn:
        pipeline_service.update_component_description(conn,component_id,description)
    return {"message":"success"}





@pipeline.post("/component/convert-ipynb/{component_id}",tags=['pipeline'])
async def convert_ipynb(component_id):
    # module_dir = queryModule.component_id
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    module_info:dict = pipeline_service.find_component_module(find_component, ScriptName.main)
    script_path  = module_info['path']
    ipynb_path = os.path.dirname(script_path)
    ipynb_path = f"{ipynb_path}/main.ipynb"
    if os.path.exists(script_path) and os.path.exists(ipynb_path):
        shutil.copy(script_path, f"{script_path}.tmp")
        notebook_service.convert_notebook(ipynb_path, script_path)
        return "success"
    raise HTTPException(status_code=404, detail=f"{script_path}或{ipynb_path}不存在!")


# @analysis_api.post("/analysis/convert-ipynb/{analysis_id}")
# async def convert_ipynb(analysis_id):
#     with get_engine().begin() as conn:
#         find_analysis = analysis_service.find_analysis_by_id(conn,analysis_id)
#     script_path  = find_analysis["pipeline_script"]
#     ipynb_path = os.path.dirname(script_path)
#     ipynb_path = f"{ipynb_path}/main.ipynb"
#     if os.path.exists(script_path) and os.path.exists(ipynb_path):
#         shutil.copy(script_path, f"{script_path}.tmp")
#         notebook_service.convert_notebook(ipynb_path, script_path)
#         return "success"
#     raise HTTPException(status_code=404, detail=f"{script_path}或{ipynb_path}不存在!")


@pipeline.post("/component/upload/{component_id}")
async def upload_image(component_id,file: UploadFile = File(...)):
    # 限制只能上传图片类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=404, detail=f"只允许上传图片文件!")
    with get_engine().begin() as conn:
        find_component = pipeline_service.find_pipeline_by_id(conn,component_id)
        find_component = {
            **{k:v for k,v in find_component.items() if k != "content"},
            **json.loads(find_component["content"])
        }
        if not find_component:
            raise HTTPException(status_code=500, detail=f"根据{component_id}不能找到记录!")
    module_info:dict = pipeline_service.find_component_module(find_component, ScriptName.main)
    script_path  = module_info['path']
    file_path = os.path.dirname(script_path)
    name, ext = os.path.splitext(file.filename)

    # file_path = os.path.join(file_path, file.filename)
    filename = f"main{ext}"
    file_path = f"{file_path}/{filename}"

    # 保存文件到本地
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    settings = get_settings()
    url_suffix = file_path.replace(str(settings.PIPELINE_DIR),"")
    ts_str = str(int(time.time()))

    url = f"/brave-api/pipeline-dir{url_suffix}?v={ts_str}"
    return {"filename": filename, "url":url}

@pipeline.get("/component/get-all-category")
async def get_all_category():
    with get_engine().begin() as conn:
        return pipeline_service.get_all_category(conn)
    