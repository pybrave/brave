import json
import os
import glob
from brave.api.config.config import get_settings
from pathlib import Path
import shutil
from fastapi import HTTPException
from brave.api.schemas.pipeline import PagePipelineQuery, SavePipeline,Pipeline,QueryPipeline,QueryModule
from brave.api.config.db import get_engine
from brave.api.models.core import t_namespace, t_pipeline_components, t_pipeline_components_relation
import importlib.resources as resources
from sqlalchemy import delete, select, and_, join, func,insert,update


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

def find_module(namespace,module_type,module_dir,module_name,file_type):
    if not module_name:
        if module_type == "nextflow":
            module_name = "main"
        else:
            return get_default_module(module_type)

        # raise HTTPException(status_code=500, detail=f"模块名称不能为空!")
    # if module_name =="default":
       
    all_module = get_all_module(namespace,file_type)
    if module_name is None: 
        module_name = module_type
    if module_dir not in all_module:
        # return get_default_module(module_type)
        raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}/{module_name}没有找到!")
    py_module_dir = all_module[module_dir]

    if module_name not in py_module_dir:
        #  return get_default_module(module_type)
        raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}/{module_name}没有找到!")
    py_module = py_module_dir[module_name]
    return py_module

def get_default_module(module_type):
    if module_type == "py_parse_analysis":
        py_parse_analysis = resources.files("brave.parse").joinpath("py_parse_analysis.py")
        return {
            "module":"brave.parse.py_parse_analysis",
            "path":str(py_parse_analysis)
        }
    if module_type == "py_parse_analysis_result":
        py_parse_analysis_result = resources.files("brave.parse").joinpath("py_parse_analysis_result.py")
        return {
            "module":"brave.parse.py_parse_analysis_result",
            "path":str(py_parse_analysis_result)
        }
    raise HTTPException(status_code=500, detail=f"{module_type}没有找到默认模块!")
def get_all_module(namespace,file_type):
    suffix = file_type
    # if module_type.startswith("py_"):
    #     suffix = "py"
    # else:
    #     suffix = "nf"
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/{namespace}/*/*/*.{suffix}")
    result = {}
    for item in nextflow_list:
        
        parts = item.split(os.sep)
        dir_name = parts[-2]
        filename = os.path.basename(item).replace(f".{suffix}","")
        if dir_name not in result:
                result[dir_name] = {}
        item_module = get_module_name(item)
        result[dir_name][filename] = {"module":item_module,"path":item}
    
  
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

def create_file(namespace,component_id,content,component_type):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    if component_type == "pipeline":
        analysisPipline = f"{pipeline_dir}/pipeline/{component_id}/main.nf"
        # pipelinieJson = f"{pipeline_dir}/main.json"
        if not os.path.exists(analysisPipline):
            dir_ = os.path.dirname(analysisPipline)
            if not os.path.exists(dir_):
                os.makedirs(dir_) 
            with open(analysisPipline,"w") as f:
                f.write("")
        # if not os.path.exists(parseAnalysisModule):
        #     with open(parseAnalysisModule,"w") as f:
        #         f.write("")

    if component_type == "software":
        # parseAnalysisModule = f"{pipeline_dir}/software/{component_id}/main.py"
        analysisPipline = f"{pipeline_dir}/software/{component_id}/main.nf"
        # dir_list = [parseAnalysisModule,analysisPipline]
        # for item in dir_list:
        dir_ = os.path.dirname(analysisPipline)
        if not os.path.exists(dir_):
            os.makedirs(dir_) 
        
        if not os.path.exists(analysisPipline):
            with resources.files("brave.templete").joinpath("nextflow.nf").open("r") as f:
                content_text = f.read()
            with open(analysisPipline,"w") as f:
                f.write(content_text)
        # if not os.path.exists(parseAnalysisModule):
        #     with resources.files("brave.templete").joinpath("py_parse_analysis.py").open("r") as f:
        #         content_text = f.read()
        #     with open(parseAnalysisModule,"w") as f:
        #         f.write(content_text)
        
        # if "parseAnalysisResultModule" in  content:
        #     parseAnalysisResultModule = content['parseAnalysisResultModule']
        #     for item in parseAnalysisResultModule:
        #         item_file = f"{pipeline_dir}/software/{component_id}/{item['module']}.py"
        #         dir_ = os.path.dirname(item_file)
        #         if not os.path.exists(dir_):
        #             os.makedirs(dir_) 
        #         if not os.path.exists(item_file):
        #             with resources.files("brave.templete").joinpath("py_parse_analysis_result.py").open("r") as f:
        #                 content_text = f.read()
        #             with open(item_file,"w") as f:
        #                 f.write(content_text)

    if component_type == "script":
        py_plot = f"{pipeline_dir}/script/{component_id}/{content['moduleName']}.py"
        py_plot_dir = os.path.dirname(py_plot)
        if not os.path.exists(py_plot):
            if not os.path.exists(py_plot_dir):
                os.makedirs(py_plot_dir)
            with resources.files("brave.templete").joinpath("py_plot.py").open("r") as f:
                content_text = f.read()
            with open(py_plot,"w") as f:
                f.write(content_text)
                        
def find_pipeline_by_id(conn,component_id):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.component_id ==component_id)
    find_pipeine = conn.execute(stmt).mappings().first()
    return find_pipeine

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
    if queryPipeline.namespace is not None:
        conditions.append(t_pipeline_components.c.namespace == queryPipeline.namespace)
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
    content = json.loads(item['content'])
    item = {**{k:v for k,v in item.items() if k != 'content'},**content}
    if 'img' in item:
        item['img'] = f"/brave-api/img/{item['img']}"
    return item

def page_pipeline(conn,query:PagePipelineQuery):
    stmt =select(
        t_pipeline_components,
        t_namespace.c.name.label("namespace_name")
    ) 
    
    # Left join with t_namespace to get namespace name
    stmt = stmt.select_from(
       t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    )

    conditions = []
    if query.component_type is not None:
        conditions.append(t_pipeline_components.c.component_type == query.component_type)
    
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


def write_all_component(conn,namespace):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.namespace == namespace)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [ {k:v for k,v in item.items() if k!="id"} for item in find_pipeline]
    with open(f"{pipeline_dir}/pipeline_component.json","w") as f:
        json.dump(find_pipeline,f)
     

def import_component(conn,namespace,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    with open(f"{pipeline_dir}/pipeline_component.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component = find_pipeline_by_id(conn,item['component_id'])
        if find_pipeline_component:
            if force:
                update_stmt = update(t_pipeline_components).where(t_pipeline_components.c.component_id == item['component_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components).values(item))    

def write_all_component_relation(conn,namespace):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.namespace == namespace)
    find_pipeline = conn.execute(stmt).mappings().all()
    find_pipeline = [ {k:v for k,v in item.items() if k!="id"} for item in find_pipeline]
    with open(f"{pipeline_dir}/pipeline_component_relation.json","w") as f:
        json.dump(find_pipeline,f)

def import_component_relation(conn,namespace,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    with open(f"{pipeline_dir}/pipeline_component_relation.json","r") as f:
        find_pipeline = json.load(f)
    for item in find_pipeline:
        find_pipeline_component_relation = find_by_relation_id(conn,item['relation_id'])
        if find_pipeline_component_relation:
            if force:
                update_stmt = update(t_pipeline_components_relation).where(t_pipeline_components_relation.c.relation_id == item['relation_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_pipeline_components_relation).values(item))   


def find_by_relation_id(conn,relation_id:str):
    stmt = t_pipeline_components_relation.select().where(t_pipeline_components_relation.c.relation_id == relation_id)
    find_pipeline = conn.execute(stmt).mappings().first()
    return find_pipeline



def find_component_by_namespace(conn,namespace):
    stmt = t_pipeline_components.select().where(t_pipeline_components.c.namespace == namespace)
    return conn.execute(stmt).mappings().all()


def get_child_depend_component(conn,namespace, component_id):
    
    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.name,
        t_pipeline_components.c.description,
        t_pipeline_components.c.namespace
        ).select_from(
            t_pipeline_components_relation.outerjoin(
                t_pipeline_components,
                t_pipeline_components_relation.c.component_id == t_pipeline_components.c.component_id,
            )
        ).where(
            t_pipeline_components_relation.c.parent_component_id == component_id,
            t_pipeline_components_relation.c.namespace == namespace
        )
    


    return conn.execute(stmt).mappings().all()

def get_parent_depend_component(conn, namespace, component_id):

    stmt = select(
        t_pipeline_components_relation.c.relation_id,
        t_pipeline_components_relation.c.relation_type,
        t_pipeline_components.c.component_id,   
        t_pipeline_components.c.component_type,
        t_pipeline_components.c.name,
        t_pipeline_components.c.description,
        t_pipeline_components.c.namespace
    ).select_from(
        t_pipeline_components_relation.outerjoin(
            t_pipeline_components,
            t_pipeline_components_relation.c.parent_component_id == t_pipeline_components.c.component_id,
        )
    ).where(
        t_pipeline_components_relation.c.component_id == component_id,
        t_pipeline_components_relation.c.namespace == namespace
    )
    return conn.execute(stmt).mappings().all()