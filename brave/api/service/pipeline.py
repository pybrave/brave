from collections import defaultdict
import json
import os
import glob
import uuid

from dependency_injector.wiring import Provide
from sqlalchemy.orm import aliased
from brave.api.config.config import get_settings
from pathlib import Path
import shutil
from fastapi import Depends, HTTPException
from brave.api.schemas.pipeline import PagePipelineQuery, SavePipeline,Pipeline,QueryPipeline,QueryModule,SaveOrder,SavePipelineComponentsEdges
from brave.api.config.db import get_engine
from brave.api.models.core import  t_pipeline_components, t_pipeline_components_edges, t_pipeline_components_relation
import importlib.resources as resources
from sqlalchemy import delete, select, and_, join, func,insert,update,or_
from datetime import datetime
from brave.api.enum.component_script import ScriptName
from sqlalchemy import  Column, Integer, String, Text, select, cast, null,text,case
from .notebook import generate_notebook
import brave.api.service.container_service as container_service

def get_pipeline_dir():
    settings = get_settings()
    return settings.PIPELINE_DIR

def get_pipeline_list():
    pipeline_dir =  get_pipeline_dir()
    pipeline_files = glob.glob(f"{pipeline_dir}/*/main.json")
    return pipeline_files
def get_module_name(item):
    pipeline_dir =  get_pipeline_dir()
    item_module = item.replace(f"{pipeline_dir}/","").replace("/",".")
    item_module = Path(item_module).stem 
    return item_module
    # return {os.path.basename(item).replace(".py",""):item_module} 
    # f'reads-alignment-based-abundance-analysis.py_plot.{module_name}'

def find_component_module(component,script_name:ScriptName) -> dict:
    # content = json.loads(component['content'])
    if "script_type" not in component:
        raise HTTPException(status_code=500, detail=f"script_type not found!")
    if script_name == ScriptName.main:
        script_type = component['script_type']
        if script_type == "nextflow":
            file_type = "nf"
        elif script_type == "python":
            file_type = "py"
        elif script_type == "shell":
            file_type = "sh"
        elif script_type == "r":
            file_type = "R"
        elif script_type == "jupyter":
            file_type = "ipynb"
        else:
            raise HTTPException(status_code=500, detail=f"script_type {script_type} not found!")
    else:
        file_type = "py"
    module_info = find_module(component['component_id'],script_name,file_type)
    if module_info:
        return module_info
    else:
        if script_name == ScriptName.main:
            create_file(component['component_id'],component['component_type'],file_type)
            module_info = find_module(component['component_id'],script_name,file_type)
            if not module_info:
                raise HTTPException(status_code=500, detail=f"组件{component.component_id}的{script_name.value}模块没有找到!")
            return module_info
        else:
            default_module = get_default_module(script_name)
            return default_module
        # else:
        #     raise HTTPException(status_code=500, detail=f"{script_name.value}没有找到默认模块!")





def find_module(module_dir,script_name:ScriptName,file_type):
    # if script_name == ScriptName.input_parse:
    # if not module_name:
    #     if  module_type == "script":
    #         module_name = "main"
    #     else:
    #         return get_default_module(module_type)

        # raise HTTPException(status_code=500, detail=f"模块名称不能为空!")
    # if module_name =="default":
       
    path_dict = get_all_module(file_type)
    # if module_name is None: 
    #     module_name = module_type
    if module_dir in path_dict:
        module_dict = path_dict[module_dir]
        if script_name.value in module_dict:
            module_info = module_dict[script_name.value]
            return module_info
    return None
        # return get_default_module(module_type)
        # raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}没有找到!")
    

    # if script_name.value not in py_module_dir:
    #     raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}/{script_name.value}没有找到!")

    
    # return py_module

def get_default_module(script_name:ScriptName):
    if script_name == ScriptName.input_parse:
        py_parse_analysis = resources.files("brave.parse").joinpath("py_parse_analysis.py")
        return {
            "module":"brave.parse.py_parse_analysis",
            "path":str(py_parse_analysis)
        }
    if script_name == ScriptName.output_parse:
        py_parse_analysis_result = resources.files("brave.parse").joinpath("py_parse_analysis_result.py")
        return {
            "module":"brave.parse.py_parse_analysis_result",
            "path":str(py_parse_analysis_result)
        }
    raise HTTPException(status_code=500, detail=f"{script_name.value}没有找到默认模块!")
def get_all_module(file_type):
    suffix = file_type
    # if module_type.startswith("py_"):
    #     suffix = "py"
    # else:
    #     suffix = "nf"
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/*/*/*.{suffix}")
    result = {}
    for item in nextflow_list:
        
        parts = item.split(os.sep)
        dir_name = parts[-2]
        filename = os.path.basename(item).replace(f".{suffix}","")
        if dir_name not in result:
                result[dir_name] = {}
        
        item_module = get_module_name(item)
        result[dir_name][filename] = {
            "module":item_module,
            "path":item
        }
    
  
    # nextflow_dict = {os.path.basename(item).replace(".py",""):get_module_name(item) for item in nextflow_list}
    return result

def delete_wrap_pipeline_dir(pipeline_key):
    pipeline_dir =  get_pipeline_dir()
    src  =f"{pipeline_dir}/{pipeline_key}"
    dst  =f"{pipeline_dir}/bin"
    if not os.path.exists(dst):
        os.makedirs(dst)
    if os.path.exists(src):
        shutil.move(src,dst)

# def create_wrap_pipeline_dir(pipeline_key):
#     pipeline_dir = get_pipeline_dir()
#     img = f"{pipeline_dir}/{pipeline_key}/img"
#     nextflow = f"{pipeline_dir}/{pipeline_key}/nextflow"
#     py_parse_analysis = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis"
#     py_parse_analysis_result = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis_result"
#     py_plot = f"{pipeline_dir}/{pipeline_key}/py_plot"
    # dir_list = [img, nextflow,py_parse_analysis,py_parse_analysis_result,py_plot]
    # for item in dir_list:
    #     if not os.path.exists(item):
    #         os.makedirs(item) 

def create_file(component_id,component_type,file_type):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}"

    content_text = ""
    if file_type == "py":
        with resources.files("brave.templete").joinpath(f"py_plot.py").open("r") as f:
            content_text = f.read()
    elif file_type == "nf":
        with resources.files("brave.templete").joinpath("nextflow.nf").open("r") as f:
            content_text = f.read()
    elif file_type == "R":
        with resources.files("brave.templete").joinpath("py_plot.R").open("r") as f:
            content_text = f.read()
    # if component_type == "pipeline":
    analysis_file = f"{pipeline_dir}/{component_type}/{component_id}/main.{file_type}"
    if not os.path.exists(analysis_file):
        dir_ = os.path.dirname(analysis_file)
        if not os.path.exists(dir_):
            os.makedirs(dir_) 
        if file_type=="ipynb":
            generate_notebook(analysis_file)
        else:
            with open(analysis_file,"w") as f:
                f.write(content_text)
            ipynb_path = os.path.dirname(analysis_file)
            generate_notebook(f"{ipynb_path}/main.ipynb")
    
    return analysis_file
        # if not os.path.exists(parseAnalysisModule):
        #     with open(parseAnalysisModule,"w") as f:
        #         f.write("")

    # if component_type == "software":
    #     # parseAnalysisModule = f"{pipeline_dir}/software/{component_id}/main.py"
    #     analysisPipline = f"{pipeline_dir}/software/{component_id}/main.{file_type}"
    #     # dir_list = [parseAnalysisModule,analysisPipline]
    #     # for item in dir_list:
    #     dir_ = os.path.dirname(analysisPipline)
    #     if not os.path.exists(dir_):
    #         os.makedirs(dir_) 
        
    #     if not os.path.exists(analysisPipline):
  
    #         with open(analysisPipline,"w") as f:
    #             f.write(content_text)
    #     return analysisPipline
    #     # if not os.path.exists(parseAnalysisModule):
    #     #     with resources.files("brave.templete").joinpath("py_parse_analysis.py").open("r") as f:
    #     #         content_text = f.read()
    #     #     with open(parseAnalysisModule,"w") as f:
    #     #         f.write(content_text)
        
    #     # if "parseAnalysisResultModule" in  content:
    #     #     parseAnalysisResultModule = content['parseAnalysisResultModule']
    #     #     for item in parseAnalysisResultModule:
    #     #         item_file = f"{pipeline_dir}/software/{component_id}/{item['module']}.py"
    #     #         dir_ = os.path.dirname(item_file)
    #     #         if not os.path.exists(dir_):
    #     #             os.makedirs(dir_) 
    #     #         if not os.path.exists(item_file):
    #     #             with resources.files("brave.templete").joinpath("py_parse_analysis_result.py").open("r") as f:
    #     #                 content_text = f.read()
    #     #             with open(item_file,"w") as f:
    #     #                 f.write(content_text)

    # if component_type == "script":
   

    #     py_plot = f"{pipeline_dir}/script/{component_id}/main.{file_type}"
    #     py_plot_dir = os.path.dirname(py_plot)
    #     if not os.path.exists(py_plot):
    #         if not os.path.exists(py_plot_dir):
    #             os.makedirs(py_plot_dir)
  
    #         with open(py_plot,"w") as f:
    #             f.write(content_text)

    #     nb_file = f"{pipeline_dir}/script/{component_id}/main.ipynb"
    #     if not os.path.exists(nb_file):
    #         generate_notebook(nb_file)

    #     return py_plot
    # raise HTTPException(status_code=500, detail=f"component_type {component_type} not create file!")


def find_component_by_id(conn,component_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    find_pipeine = conn.execute(stmt).mappings().first()
    return find_pipeine

def find_pipeline_by_id(conn,component_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    find_component = conn.execute(stmt).mappings().first()
    
    # component_type = find_component["component_type"]
    if find_component:
        find_component = dict(find_component)
        if find_component["container_id"]:
            find_container = container_service.find_container_by_id(conn,find_component["container_id"])
            find_component['container'] = find_container
        if find_component["sub_container_id"]:
            find_container = container_service.find_container_by_id(conn,find_component["sub_container_id"])
            find_component['sub_container'] = find_container

    # if find_component and find_component["server_container_id"]:
    #     find_component = dict(find_component)
    #     find_container = container_service.find_container_by_id(conn,find_component["container_id"])
    #     find_component['container'] = find_container
        # find_component['container_name'] = find_container["name"]
    return find_component

def find_component_by_parent_id(conn,parent_id,relation_type=None):
    stmt = (
        select(
            t_pipeline_components_relation,  # 关系表所有字段
            t_pipeline_components  # 组件表所有字段
        )
        .select_from(
            t_pipeline_components_relation.outerjoin(
                t_pipeline_components,
                t_pipeline_components_relation.c.component_id == t_pipeline_components.c.component_id
            )
        )
        .where(t_pipeline_components_relation.c.parent_component_id == parent_id)
    )

    if relation_type is not None:
        stmt = stmt.where(t_pipeline_components_relation.c.relation_type == relation_type)

    result = conn.execute(stmt).mappings().all()
    return result



def list_pipeline(conn,queryPipeline:QueryPipeline):
    stmt = t_pipeline_components.select() 
  
    conditions = []
    if queryPipeline.component_type is not None:
        conditions.append(t_pipeline_components.c.component_type == queryPipeline.component_type)

    # if analysisResultQuery.ids is not None:
    #     conditions.append(analysis_result.c.id.in_(analysisResultQuery.ids))
    # if analysisResultQuery.analysis_method is not None:
    #     conditions.append(analysis_result.c.analysis_method.in_(analysisResultQuery.analysis_method))
    # if analysisResultQuery.analysis_type is not None:
    #     conditions.append(analysis_result.c.analysis_type == analysisResultQuery.analysis_type)
    stmt= stmt.where(and_( *conditions))

    # stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_type ==queryPipeline.component_type)
    find_pipeine = conn.execute(stmt).fetchall()
    return find_pipeine

def format_pipeline_componnet_one(item):
    try:
        content = json.loads(item['content'])
        item = {**content,**{k:v for k,v in item.items() if k != 'content'}}
        if 'img' in item:
            if not item['img']:
                item['img'] = f"/brave-api/img/pipeline.jpg"
    except Exception as e:
        print("component json error",json.dumps(item,indent=4))
 
        # else:
    return item

def page_pipeline(conn,query:PagePipelineQuery):
    stmt =select(
        t_pipeline_components,
    ) 
    
   

    conditions = []
    if query.component_type is not None:
        conditions.append(t_pipeline_components.c.component_type == query.component_type)
    if query.category is not None and query.category !="all":
        conditions.append(t_pipeline_components.c.category == query.category)

    if query.keywords:
        keyword_pattern = f"%{query.keywords}%"
        conditions.append(
            or_(
                t_pipeline_components.c.component_name.ilike(keyword_pattern),
                t_pipeline_components.c.tags.ilike(keyword_pattern),
                t_pipeline_components.c.description.ilike(keyword_pattern)
            )
        )

    stmt = stmt.where(and_(*conditions))
    count_stmt = select(func.count()).select_from(t_pipeline_components).where(and_(*conditions))

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [dict(item) for item in find_pipeline]
    find_pipeline = [format_pipeline_componnet_one(item) for item in find_pipeline]

    total = conn.execute(count_stmt).scalar()
    return {
        "items": find_pipeline,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }



 
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Type {type(o)} not serializable")



def find_by_relation_id(conn,relation_id:str):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
    find_pipeline = conn.execute(stmt).mappings().first()
    return find_pipeline



def find_component_by_container_id(conn,container_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.container_id == container_id)
    return conn.execute(stmt).mappings().all()

def get_child_depend_component(conn, component_id):
    
    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.description,
        ).select_from(
            t_pipeline_components_relation.outerjoin(
                t_pipeline_components,
                t_pipeline_components_relation.c.component_id == t_pipeline_components.c.component_id,
            )
        ).where(
            t_pipeline_components_relation.c.parent_component_id == component_id,
        )
    


    return conn.execute(stmt).mappings().all()

def get_parent_depend_component(conn, component_id):

    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,   
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.description,
    ).select_from(
        t_pipeline_components_relation.outerjoin(
            t_pipeline_components,
            t_pipeline_components_relation.c.parent_component_id == t_pipeline_components.c.component_id,
        )
    ).where(
        t_pipeline_components_relation.c.component_id == component_id,
    )
    return conn.execute(stmt).mappings().all()




def get_child_component_count(conn, component_id,relation_type):
    stmt = select(func.count()).select_from(t_pipeline_components_relation).where(
        t_pipeline_components_relation.c.parent_component_id == component_id,
        t_pipeline_components_relation.c.relation_type == relation_type,
    )
    return conn.execute(stmt).scalar()


def save_order(conn,saveOrderList:list[SaveOrder]):
    for saveOrder in saveOrderList:
        stmt = update(t_pipeline_components_relation).where(t_pipeline_components_relation.c.relation_id == saveOrder.relation_id).values(order_index=saveOrder.order_index)
        conn.execute(stmt)



def save_pipeline_components_edges(conn,savePipelineComponentsEdges:SavePipelineComponentsEdges):
    # stmt = delete(t_pipeline_components_edges).where(t_pipeline_components_edges.c.pipeline_id == savePipelineComponentsEdges.component_id)
    # conn.execute(stmt)
    # for pipeline_components_edge in savePipelineComponentsEdges.pipeline_components_edges:
    #     stmt = insert(t_pipeline_components_edges).values(
    #         source=pipeline_components_edge.source,
    #         sourceHandle=pipeline_components_edge.sourceHandle,
    #         target=pipeline_components_edge.target,
    #         targetHandle=pipeline_components_edge.targetHandle,
    #         pipeline_id=savePipelineComponentsEdges.component_id
    #     )
    #     conn.execute(stmt)
        
    update_stmt = update(t_pipeline_components).where(
        t_pipeline_components.c.component_id == savePipelineComponentsEdges.component_id
        ).values(position=savePipelineComponentsEdges.position,
        edges=savePipelineComponentsEdges.edges  )
    conn.execute(update_stmt)





def get_pipeline_v2(conn,name,component_type="pipeline"):
    base = (select(
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.content,
        t_pipeline_components.c.component_name,
        t_pipeline_components.c.position,
        t_pipeline_components.c.edges,
        t_pipeline_components.c.description,
        t_pipeline_components.c.file_type,
        t_pipeline_components.c.script_type,
        cast(null(), String(255)).label("relation_type"),
        cast(null(), String(255)).label("parent_component_id"),
        cast(null(), String(255)).label("order_index"),
        cast(null(), String(255)).label("relation_id"),
    ).where(
        t_pipeline_components.c.component_id == name,
        t_pipeline_components.c.component_type == component_type,
    ).cte(name="base", recursive=True))


    # 递归 CTE 定义
    # cte = base.cte(name="full_pipeline", recursive=True)

    tp1 = aliased(t_pipeline_components)
    rel = t_pipeline_components_relation
    # fp = aliased(cte)  # 引用递归CTE自身
    base_alias = base.alias()

    recursive = select(
        tp1.c.component_id,
        tp1.c.component_type,
        tp1.c.content,
        tp1.c.component_name,
        tp1.c.position,
        tp1.c.edges,
        tp1.c.description,
        # cast(null(), String(255)).label("description"),
        tp1.c.file_type,
        tp1.c.script_type,
        rel.c.relation_type,
        rel.c.parent_component_id,
        rel.c.order_index,
        rel.c.relation_id,
    ).select_from(
        tp1.join(rel, tp1.c.component_id == rel.c.component_id)
        .join(base_alias, rel.c.parent_component_id == base_alias.c.component_id)
    )

    # # 合并 base 和 recursive，生成完整的递归CTE
    cte = base.union_all(recursive) #.cte(name="full_pipeline", recursive=True)

    # # 最终查询排序
    final_query = select(cte).order_by(
        case((cte.c.order_index == None, 1), else_=0),
        cte.c.order_index
        # func.coalesce(cte.c.order_index, cte.c.relation_id),
    )
    # 执行查询
    # with get_engine().begin() as conn:
    # [dict(item) for item in data]
    data = conn.execute(final_query).mappings().all()
    unique_data = {row["relation_id"]: row for row in data}
    data = list(unique_data.values())
    if  len(data) < 0:
        raise HTTPException(status_code=500, detail=f"{name}没有找到!")  
    id_to_node = {(item["component_id"], item["relation_type"]): get_one_data(item) for item in data}
    children_map = defaultdict(list)
    for item in data:
        parent_id = item.get("parent_component_id")
        if parent_id:
            # parent_key = (parent_id, item["relation_id"])  # parent 的唯一标识
            child_key = (item["component_id"], item["relation_type"])
            children_map[parent_id].append(child_key)
    # 获取根 pipeline_id
    root_item  = next((item for item in data if item["component_type"] == component_type),None)
    if not root_item:
        raise HTTPException(status_code=500, detail=f"{name}没有找到!")  
    # root_key = (root_item["component_id"], None)
    if component_type == "software":
        result = build_software_structure(id_to_node,children_map,root_item)
    elif component_type == "pipeline":
        result = build_pipeline_structure(id_to_node,children_map,root_item)
    elif component_type == "file":
        result = build_file_structure(id_to_node,children_map,root_item)
    else:
        raise HTTPException(status_code=500, detail=f"{component_type}没有结构解析!")  
    return result

def get_one_data(item):
    try:
        content = json.loads(item["content"])
    except Exception as e:
        print("component json error",json.dumps(dict(item),indent=4))
        print("component json error",e)
        content = {}
    # end try
    
    item = {k:v for k,v in item.items() if k!="content"}
    return { **content,**item }

def build_file_structure(id_to_node,children_map,root_item):
    
    item = {**root_item, "downstreamAnalysis": []}
    for ds_id in children_map.get(item["component_id"], []):
        downstream = id_to_node[ds_id]
        item["downstreamAnalysis"].append(downstream)
    return item

def  build_software_structure(id_to_node,children_map,root_item):
    # result = {**root_item}
    item = {**root_item}
    input_files = []
    output_files = []
    for sub_id in children_map.get(root_item["component_id"], []):
        sub = id_to_node[sub_id]
        sub_content = sub
        if sub["relation_type"] == "software_input_file":
            input_files.append(sub_content)
        elif sub["relation_type"] == "software_output_file":
            sub_out = {**sub_content, "downstreamAnalysis": []}
            for ds_id in children_map.get(sub["component_id"], []):
                downstream = id_to_node[ds_id]
                sub_out["downstreamAnalysis"].append(downstream)
            output_files.append(sub_out)    
    return {**item, "inputFile":input_files, "outputFile":output_files}

def build_pipeline_structure(id_to_node,children_map,root_item):
    # node = id_to_node[pid]
    result = {**root_item}
    edges = []
    if "edges" in root_item and root_item["edges"]:
        edges = json.loads(root_item["edges"])
    edges_target_file_set = set( edge['targetHandle'] for edge in edges )
    items = []
    for child_id in children_map.get(root_item["component_id"], []):
        child = id_to_node[child_id]
        content = child
        if child["component_type"] == "software":
            item = {**content}
            item = {k:v for k,v in item.items() if v is not None}
            input_files = []
            output_files = []
            for sub_id in children_map.get(child_id[0], []):
                sub = id_to_node[sub_id]
                sub_content = sub
                if sub["relation_type"] == "software_input_file":
                    sub_content = {k:v for k,v in sub_content.items() if v is not None}
                    input_files.append(sub_content)
                elif sub["relation_type"] == "software_output_file":
                    sub_out = {**sub_content, "downstreamAnalysis": []}
                    sub_out = {k:v for k,v in sub_out.items() if v is not None}
                    for ds_id in children_map.get(sub["component_id"], []):
                        downstream = id_to_node[ds_id]
                        downstream = {k:v for k,v in downstream.items() if v is not None}
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
        # result["items"] = items
        # item["databases"] for item in items if "databases" in item
        result["databases"] = [
             db for item in items if "databases" in item for db in item["databases"]
        ]
        result["upstreamFormJson"] = [
            db for item in items if "upstreamFormJson" in item and isinstance(item["upstreamFormJson"],list) and len(item["upstreamFormJson"]) > 0   for db in item["upstreamFormJson"]
        ]
        result["software"] = items
        # if items and len(items) > 0 and "inputFile" in items[0]:
        #     result["inputFile"] = items[0]["inputFile"]
        # else:
        #     result["inputFile"] = []
        input_file_list = [file for item in items if "inputFile" in item for file in item["inputFile"]]
        inputFile = []
        input_file_component_ids = set()
        for file in input_file_list:
            if file["component_id"] not in edges_target_file_set and file["component_id"] not in input_file_component_ids:
                inputFile.append(file)
                input_file_component_ids.add(file["component_id"])
        # for software in items:
        #     if 


        result["inputFile"] = inputFile
    return result


  
def update_component_description(conn, component_id,description):
    stmt = t_pipeline_components.update().where(t_pipeline_components.c.component_id ==component_id).values(description=description)
    conn.execute(stmt)
    # pass







def get_components(conn, component_id):
    base = (
        select(t_pipeline_components)
        .where(t_pipeline_components.c.component_id == component_id)
        .cte(name="base", recursive=True)
    )
    tp1 = aliased(t_pipeline_components)
    rel = t_pipeline_components_relation
    base_alias = base.alias()

    # Use INNER JOINs for the recursive part to comply with MySQL's CTE restrictions
    recursive = (
        select(tp1)
        .select_from(
            tp1.join(rel, tp1.c.component_id == rel.c.component_id)
               .join(base_alias, rel.c.parent_component_id == base_alias.c.component_id)
        )
    )

    cte = base.union_all(recursive)
    final_query = select(cte)
    data = conn.execute(final_query).mappings().all()
    return data

def get_component_relation(conn,component_id):
    base = (select(
        t_pipeline_components_relation
    ).where(
        t_pipeline_components_relation.c.parent_component_id == component_id,
    ).cte(name="base", recursive=True))
    tr1 = aliased(t_pipeline_components_relation)

    base_alias = base.alias()

    recursive = select(tr1).select_from(
        tr1.join(base_alias, tr1.c.parent_component_id == base_alias.c.component_id)
    )

    cte = base.union_all(recursive) 
    final_query = select(cte)
    data = conn.execute(final_query).mappings().all()
    return data

def delete_component_file(component):
    component_type = component["component_type"]
    component_id = component["component_id"]
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{component_type}/{component_id}"
    if os.path.exists(pipeline_dir):
        shutil.rmtree(pipeline_dir)

def copy_component_json(component, component_id):
    pipeline_dir = get_pipeline_dir()
    source_component_id = component["component_id"]
    component_type = component["component_type"]
    source_component_dir = f"{pipeline_dir}/{component_type}/{source_component_id}/main.*"
    target_component_dir = f"{pipeline_dir}/{component_type}/{component_id}"
    source_component_file_list = glob.glob(source_component_dir)
    if not os.path.exists(target_component_dir):
        os.makedirs(target_component_dir)
        
    for source_file in source_component_file_list:
        filename = os.path.basename(source_file)
        target_file = f"{target_component_dir}/{filename}"
        shutil.copyfile(source_file,target_file)

# for publish components relation list
def find_relation_by_component_id(conn, component_id):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.component_id == component_id)
    find_components_relation = conn.execute(stmt).mappings().all()
    return find_components_relation

# for publish components relation list
def find_relation_by_parent_component_id(conn, parent_component_id):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.parent_component_id == parent_component_id)
    find_components_relation = conn.execute(stmt).mappings().all()
    return find_components_relation

def find_relation_in_parent_component_ids(conn, parent_component_ids):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.parent_component_id.in_(parent_component_ids))
    find_components_relation = conn.execute(stmt).mappings().all()
    return find_components_relation


# for publish component list
def find_component_list_in_ids(conn,component_ids):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id.in_(component_ids))
    find_components = conn.execute(stmt).mappings().all()
    return find_components

def write_component_json(component_id):
    with get_engine().begin() as conn:
        current_component = find_component_by_id(conn,component_id)
        if not current_component:
            raise HTTPException(status_code=500, detail=f"组件{component_id}没有找到!")
        current_component = dict(current_component)
        component_type = current_component["component_type"]

        if component_type =="script":
            component_relation_list = find_relation_by_component_id(conn,component_id)
            parent_component_ids = [ item['parent_component_id'] for item in component_relation_list ]
            component_list = find_component_list_in_ids(conn,parent_component_ids)
            component_list.append(current_component)
        elif component_type =="file" or component_type =="software" or component_type =="pipeline":
        #     component_list = [current_component]
        #     component_relation_list = []
        # elif component_type =="software" or component_type =="pipeline":
        #     component_relation_list = find_relation_by_parent_component_id(conn,component_id)
        #     component_ids = [ item['component_id'] for item in component_relation_list ]
        #     component_list = find_component_list_in_ids(conn,component_ids)
        #     component_list.append(current_component)
        # elif component_type =="pipeline":
        #     # find all child software component by pipeline component id
        #     component_relation_list =  find_relation_by_parent_component_id(conn,component_id)
        #     component_ids = [ item['component_id'] for item in component_relation_list ]
        #     component_list = find_component_list_in_ids(conn,component_ids)
          
        #     # find all child file component by software component id
        #     component_ids = [item["component_id"] for item in component_list]
        #     file_relation_list = find_relation_in_parent_component_ids(conn, component_ids)
        #     file_component_ids = [ item['component_id'] for item in file_relation_list ]
        #     file_component_list = find_component_list_in_ids(conn,file_component_ids)
        #     component_list = component_list + file_component_list
        #     component_relation_list = component_relation_list + file_relation_list
        #     component_list.append(current_component)

            component_list = get_components(conn,component_id)
            component_relation_list =  get_component_relation(conn,component_id)
        else:
            raise HTTPException(status_code=500, detail=f"组件类型{component_type}不支持导出!")
            # component_list = get_components(conn,component_id)
            # component_relation_list =  get_component_relation(conn,component_id)
    

        container_id_list = [ item['container_id'] for item in component_list if item['container_id'] is not None ]
        container_list = container_service.find_by_container_ids(conn,container_id_list)
    
    # current_component = [item for item in component_list if item.component_id == component_id]
 
    # current_component = current_component[0]
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{component_type}/{component_id}"
    if not os.path.exists(pipeline_dir):
        os.makedirs(pipeline_dir)
    
    pipeline_component_file = f"{pipeline_dir}/pipeline_component.json"
    pipeline_component_relation_file = f"{pipeline_dir}/pipeline_component_relation.json"
    with open(pipeline_component_file,"w") as f:
        json.dump([ {k:v for k,v in item.items() if k!="id"} for item in component_list],f, default=datetime_converter)
    with open(pipeline_component_relation_file,"w") as f:
        json.dump([ {k:v for k,v in item.items() if k!="id" and k!="created_at" and k!="updated_at"} for item in component_relation_list],f, default=datetime_converter)    

    container_file = f"{pipeline_dir}/container.json"
    container_list = [ {k:v for k,v in item.items() if k!="id" and k!="created_at" and k!="updated_at"} for item in container_list]
    with open(container_file,"w") as f:
        json.dump(container_list,f)
    
    install_file = f"{pipeline_dir}/install.json"
    with open(install_file,"w") as f:
        json.dump({
            "component_type":component_type,
            "component_id":component_id,
            "category":current_component["category"] if current_component["category"] else "default",
            "component_name":current_component["component_name"],
            "img":os.path.basename(current_component["img"]) if current_component["img"] else "",
        },f)
    

        # component = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    print(f"export pipeline_component_file: {pipeline_component_file}!")
    print(f"export pipeline_component_relation_file: {pipeline_component_relation_file}!")
    print(f"export container_file: {container_file}!")

    pass



def import_component_relation(conn,path,force=False):
    # pipeline_dir = get_pipeline_dir()
    with open(f"{path}/pipeline_component_relation.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component_relation = find_by_relation_id(conn,item['relation_id'])
        if find_pipeline_component_relation:
            if force:
                update_stmt = update(t_pipeline_components_relation).where(t_pipeline_components_relation.c.relation_id == item['relation_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components_relation).values(item))   
def import_component(conn,path,force=False):

    with open(f"{path}/pipeline_component.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component = find_pipeline_by_id(conn,item['component_id'])
        if find_pipeline_component:
            if force:
                update_stmt = update(t_pipeline_components).where(t_pipeline_components.c.component_id == item['component_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components).values(item))   

def import_component_json(conn,find_pipeline,force=False):

    # with open(f"{path}/pipeline_component.json","r") as f:
    #     find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component = find_pipeline_by_id(conn,item['component_id'])
        if find_pipeline_component:
            if force:
                update_stmt = update(t_pipeline_components).where(t_pipeline_components.c.component_id == item['component_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components).values(item))   





# Find components by a list of component IDs
def find_by_component_ids(conn,component_ids):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id.in_(component_ids))
    find_pipeline = conn.execute(stmt).mappings().all()
    return find_pipeline


def get_all_category(conn):
    stmt = select(t_pipeline_components.c.category).distinct().where(t_pipeline_components.c.category != None)
    categories = conn.execute(stmt).scalars().all()
    return categories
    
def get_example(conn,component_id):
    component = find_component_by_id(conn,component_id)
    if not component:
        raise HTTPException(status_code=500, detail=f"组件{component_id}没有找到!")
    component_type = component["component_type"]
    if(component_type != "file"):
        raise HTTPException(status_code=500, detail=f"组件{component_id}不是file类型!")
    pipeline_dir = get_pipeline_dir()
    component_dir = f"{pipeline_dir}/{component_type}/{component_id}"
    if not os.path.exists(component_dir):
        raise HTTPException(status_code=500, detail=f"组件{component_id}文件目录没有找到!")
    example_file = f"{component_dir}/example.tsv"
    if not os.path.exists(component_dir):
        raise HTTPException(status_code=500, detail=f"组件{example_file}示例文件没有找到!")
    example_suffix  = example_file.replace(str(pipeline_dir),"")
    example_url = f"/brave-api/pipeline-dir{example_suffix}" 
    return example_file,example_url,component