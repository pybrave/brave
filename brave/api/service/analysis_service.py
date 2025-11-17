from operator import and_, or_
from brave.api.config.db import get_engine
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.core.routers_name import RoutersName
from brave.api.models.core import analysis as t_analysis, t_pipeline_components,t_project
from sqlalchemy import select,update,func
from fastapi import HTTPException
import json
from brave.api.schemas.analysis import AnalysisExecuterModal, QueryAnalysis
import  brave.api.service.pipeline as pipeline_service
import importlib
import hashlib
import os
from brave.api.enum.component_script import ScriptName
from brave.api.models.core import t_container
from sqlalchemy.orm import aliased
from brave.api.utils.file_utils import delete_all_in_dir
from brave.api.core.evenet_bus import EventBus

def get_parse_analysis_result_params(conn,analysis_id):
    stmt = select(t_analysis).where(t_analysis.c.analysis_id == analysis_id)
    result = conn.execute(stmt).mappings().first()
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
    component_id = result['component_id']
    component_ = pipeline_service.find_pipeline_by_id(conn, component_id)
    if not component_:
        raise HTTPException(status_code=404, detail=f"Component with id {component_id} not found")
  
    file_format_list = []
    if component_["component_type"] == "pipeline":
        component_ = pipeline_service.get_pipeline_v2(conn,component_id)
        softwareList = component_['software']
        component_file_list = [outputFile for item in softwareList if 'outputFile' in item for outputFile in item['outputFile']]
        file_format_list = [
            {"dir":item['dir'],"fileFormat":item['fileFormat'],"name":item['name'],"component_id":item['component_id']}
            for item in component_file_list if 'fileFormat' in item
        ]
        pass
    else:
     
        component_file_list = pipeline_service.find_component_by_parent_id(conn,component_id,"software_output_file")
        component_file_content_list = [{**json.loads(item.content),
                                        "file_type":item.get("file_type",""),
                                        "component_name":item["component_name"],
                                        "component_id":item['component_id']} for item in component_file_list]
        file_format_list = [
            {"dir":item['dir'], "file_type":item.get("file_type",""),"fileFormat":item['fileFormat'],"name":item['component_name'],"component_id":item['component_id']}
            for item in component_file_content_list if 'fileFormat' in item
        ]
        # component_file_list = []
    # component_file_list = pipeline_service.find_component_by_parent_id(conn,component_id,"software_output_file")
    component_ = {
            **{k:v for k,v in component_.items() if k != "content"},
            **json.loads(component_['content'])
        }
    # try:
    #     component_content = json.loads(component_.content)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to parse component content: {e}")
    # parse_analysis_result_module = component_content.get('parseAnalysisResultModule')
    
    
    
    # if len(component_file_list) == 0:
    #     return {"error":"组件没有添加输出文件,请检查!"}
        # raise HTTPException(status_code=500, detail=f"组件{component_id}没有添加输出文件,请检查!")
    
    # if not file_format_list:
    #     return {"error":"组件的输出文件没有配置fileFormat!请检查!"}
        # raise HTTPException(status_code=500, detail=f"组件{component_id}的输出文件没有配置fileFormat!请检查!")


    module_info = pipeline_service.find_component_module(component_, ScriptName.output_parse)
    if not module_info:
        raise HTTPException(status_code=500, detail=f"组件{component_id}的输出解析模块没有找到!")

    py_module = module_info['module']
    module = importlib.import_module(py_module)
    parse = getattr(module, "parse")

    return {
        "analysis":result,
        "file_format_list":file_format_list,
        "parse":parse
    }



def execute_parse(analysis,parse,file_format_list):
    analysis_params_path = analysis.get('params_path')
    if not analysis_params_path or not os.path.exists(analysis_params_path):
        raise HTTPException(status_code=500, detail=f"Analysis params_path {analysis_params_path} not found")
    sample_list = []
    with open(analysis_params_path,"r") as f:
        analysis_params = json.load(f)
        if "groups" in analysis_params:
            groups = analysis_params["groups"]
            analyis_result_list = [analysis_params[group] for group in groups]
            
            for item in analyis_result_list:
                if type(item) == list:
                    sample_list = sample_list + item
                elif type(item) == dict:
                    sample_list.append(item) 
   
          
            



    result_dict = {}
    result_list = []
    for item in file_format_list:     
        if    item['dir']!="":
            dir_path = f"{analysis['output_dir']}/output/{item['dir']}"
        else:
            dir_path = f"{analysis['output_dir']}/output"
        res = None    
        args = {
            "dir_path":dir_path,
            "file_type":item.get("file_type",""),
            # "analysis": dict(result),
            "file_format":item['fileFormat'],
            "sample_list":sample_list
            # "args":moduleArgs,
        
        }
        res = parse(**args)
       
        for sub_item in  res:
            sub_item.update({
                "component_id":item['component_id'],
                # "analysis_name":item['name'],
                # "analysis_method":item['name'],
                "project":analysis['project'],
                "analysis_id":analysis['analysis_id'],
                "analysis_type":"upstream_analysis",
                "analysis_result_hash":hashlib.md5(sub_item['content'].encode()).hexdigest()
                })
        result_dict.update({item['name']:res})
        result_list = result_list + res
    return result_list,result_dict

def add_run_id(item):
    item= dict(item)
    if item['job_status'] == "running":
        item['run_id'] = f"job-{item['analysis_id']}"
        item['run_type'] = "job"
    elif item['server_status'] == "running":
        item['run_id'] = f"server-{item['analysis_id']}"
        item['run_type'] = "server"
    return item

def find_running_analysis(conn):
    stmt = select(t_analysis).where(or_(t_analysis.c.job_status == "running",t_analysis.c.server_status == "running"))
    result = conn.execute(stmt).mappings().all()
    result = [add_run_id(item) for item in result]
    return result

def get_all_files_recursive(directory,dir_name,file_dict):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file).replace(directory,""))
    return file_dict.update({dir_name:file_list})

def get_file_dict(file_format_list,output_dir):
    file_dict={}
    for item in file_format_list:
        dir_path = f"{output_dir}/output/{item['dir']}"
        get_all_files_recursive(dir_path,item['dir'],file_dict)
    return file_dict

def find_analysis_by_id(conn,analysis_id):
    stmt = select(t_analysis).where(t_analysis.c.analysis_id == analysis_id)
    result = conn.execute(stmt).mappings().first()
    return result

async def finished_analysis(analysis_id,run_type,status):
    with get_engine().begin() as conn:  
        finished_analysis_(conn,analysis_id,run_type,status)

def finished_analysis_(conn,analysis_id,run_type,status):
    
    if run_type == "job":
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(job_status = status)
        )
    elif run_type == "server":
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(server_status = status)
        )
    else:
        raise ValueError(f"Invalid run_type: {run_type}")
    
    conn.execute(stmt)
    conn.commit()
    print(f"Analysis {analysis_id} {status}")

async def update_ports(analysis_id,ports):
    with get_engine().begin() as conn:  
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(ports = ports)
        )
        conn.execute(stmt)
    print(f"Analysis {analysis_id} {ports}")

def update_report(conn,analysis_id,is_report):
    stmt = (
        update(t_analysis)
        .where(t_analysis.c.analysis_id == analysis_id)
        .values(is_report = is_report)
    )
    conn.execute(stmt)

async def update_url(analysis_id,url):
    with get_engine().begin() as conn:  
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(url = url)
        )
        conn.execute(stmt)
    print(f"update Analysis {analysis_id} {url}")

def list_analysis_v1(conn,query:QueryAnalysis):
    conditions = []
    if query.analysis_id:
        conditions.append(t_analysis.c.analysis_id == query.analysis_id)
    if query.analysis_method:
        conditions.append(t_analysis.c.analysis_method == query.analysis_method)
    if query.component_id:
        conditions.append(t_analysis.c.component_id == query.component_id)
    if query.project:
        conditions.append(t_analysis.c.project == query.project)
    if query.component_ids:
        conditions.append(t_analysis.c.component_id.in_(query.component_ids))
    if query.is_report:
        conditions.append(t_analysis.c.is_report)
    # t_sub_container = aliased(t_container)

    stmt = select(
        t_analysis,
        t_pipeline_components.c.component_name.label("component_name"),
        t_pipeline_components.c.order_index.label("component_order_index"),
        # t_pipeline_components.c.label.label("component_label"),
        t_pipeline_components.c.component_type.label("component_type"),
        t_project.c.project_name.label("project_name"),
        t_container.c.name.label("container_name"),
        t_container.c.image.label("container_image"),
        t_container.c.container_id.label("container_id"),
        t_container.c.image_status.label("image_status"),
        t_container.c.image_id.label("image_id")
        # t_sub_container.c.name.label("sub_container_name"),
        # t_sub_container.c.image.label("sub_container_image")
    )

    stmt = stmt.select_from(
        t_analysis.outerjoin(t_pipeline_components,t_analysis.c.component_id==t_pipeline_components.c.component_id)
        .outerjoin(t_project,t_analysis.c.project==t_project.c.project_id)
        .outerjoin(t_container,t_pipeline_components.c.container_id==t_container.c.container_id)
        # .outerjoin(t_sub_container,t_pipeline_components.c.sub_container_id==t_sub_container.c.container_id)
        )
    if conditions:
        stmt = stmt.where(and_(*conditions) if len(conditions) > 1 else conditions[0])

    # stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    # stmt = stmt.order_by(t_analysis.c.id.desc())
    result = conn.execute(stmt).mappings().all()
    return result

def list_analysis(conn,query:QueryAnalysis):
    conditions = []
    if query.analysis_id:
        conditions.append(t_analysis.c.analysis_id == query.analysis_id)
    if query.analysis_method:
        conditions.append(t_analysis.c.analysis_method == query.analysis_method)
    if query.component_id:
        conditions.append(t_analysis.c.component_id == query.component_id)
    if query.project:
        conditions.append(t_analysis.c.project == query.project)
    if query.component_ids:
        conditions.append(t_analysis.c.component_id.in_(query.component_ids))
    if query.is_report:
        conditions.append(t_analysis.c.is_report)
    # t_sub_container = aliased(t_container)

    stmt = select(
        t_analysis,
        t_pipeline_components.c.component_name.label("component_name"),
        t_pipeline_components.c.order_index.label("component_order_index"),
        # t_pipeline_components.c.label.label("component_label"),
        t_pipeline_components.c.component_type.label("component_type"),
        t_project.c.project_name.label("project_name"),
        t_container.c.name.label("container_name"),
        t_container.c.image.label("container_image"),
        t_container.c.container_id.label("container_id"),
        t_container.c.image_status.label("image_status"),
        t_container.c.image_id.label("image_id")
        # t_sub_container.c.name.label("sub_container_name"),
        # t_sub_container.c.image.label("sub_container_image")
    )

    stmt = stmt.select_from(
        t_analysis.outerjoin(t_pipeline_components,t_analysis.c.component_id==t_pipeline_components.c.component_id)
        .outerjoin(t_project,t_analysis.c.project==t_project.c.project_id)
        .outerjoin(t_container,t_pipeline_components.c.container_id==t_container.c.container_id)
        # .outerjoin(t_sub_container,t_pipeline_components.c.sub_container_id==t_sub_container.c.container_id)
        )
    if conditions:
        stmt = stmt.where(and_(*conditions) if len(conditions) > 1 else conditions[0])

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    stmt = stmt.order_by(t_analysis.c.id.desc())
    result = conn.execute(stmt).mappings().all()
    count_stmt = select(func.count()).select_from(t_analysis).where(and_(*conditions) if len(conditions) > 1 else conditions[0])
    total = conn.execute(count_stmt).scalar()

    formatted_result = []
    for row in result:
        new_row = dict(row)  # 转成普通字典
        for field in ["created_at", "updated_at"]:
            if field in new_row and new_row[field]:
                new_row[field] = new_row[field].strftime("%Y-%m-%d %H:%M:%S")
        formatted_result.append(new_row)

    return {
        "items": formatted_result,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }


def update_extra_project(conn,analysis_id,project):
    stmt = (
        update(t_analysis)
        .where(t_analysis.c.analysis_id == analysis_id)
        .values(extra_project_ids = json.dumps(project))
    )
    conn.execute(stmt)


async def run_analysis(conn,analysis_,run_type):
    analysis_id = analysis_['analysis_id']
    pipeline_script = analysis_['pipeline_script']
    pipeline_dir = pipeline_service.get_pipeline_dir()
    pipeline_dir = str(pipeline_dir)
    if not pipeline_script.startswith(pipeline_dir):
        raise HTTPException(status_code=500, detail=f"Pipeline script {pipeline_script} is not in pipeline dir {pipeline_dir}")
    component = pipeline_service.find_component_by_id(conn,analysis_["component_id"])
    component_type = component['component_type']
    if run_type=="job" and component.get("script_type")!="nextflow":
        output_dir = f"{analysis_['output_dir']}/output"
        # if os.path.exists(output_dir):
        delete_all_in_dir(output_dir)

    if not component["container_id"]:
        raise HTTPException(status_code=500, detail=f"please config container id") 

    # find_container = container_service.find_container_by_id(conn,analysis_["container_id"])
    analysis_ = dict(analysis_)
    analysis_["run_id"] = f"{run_type}-{analysis_id}"

    if run_type == "job":
        analysis_["container_id"] =component["container_id"]
    else:
        # if component_type=="script":
        analysis_["container_id"] =component["container_id"]
        # else: 
        #     if not component["sub_container_id"]:
        #         raise HTTPException(status_code=500, detail=f"please config sub_container_id id") 
        #     analysis_["container_id"] = component["sub_container_id"]

    # analysis_["image"] = find_container["image"]
    analysis_ = AnalysisExecuterModal(**analysis_)
    # analysis_.image = find_container["image"]
    finished_analysis_(conn,analysis_id,run_type,"running")
    return analysis_
    # stmt = analysis.update().values({"analysis_status":"running","run_type":run_type}).where(analysis.c.analysis_id==analysis_id)
    # conn.execute(stmt)

def find_analysis_by_component_id(conn ,component_id):
    stmt = select(t_analysis.c.analysis_id,t_analysis.c.analysis_name).where(t_analysis.c.component_id == component_id)
    result = conn.execute(stmt).mappings().all()
    return result

def update_used(conn,analysis_id):
    analysis = find_analysis_by_id(conn,analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis with id {analysis_id} not found")
    if not analysis['used']:
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(used = True)
        )
        conn.execute(stmt)
    else:
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(used = False)
        )
        conn.execute(stmt)
    
    # analysis_list = find_analysis_by_component_id(conn ,analysis['component_id'])
    # analysis_ids = [item["analysis_id"] for item in analysis_list if item['analysis_id'] != analysis_id]
    # if analysis_ids:
    #     stmt = (
    #         update(t_analysis)
    #         .where(t_analysis.c.analysis_id.in_(analysis_ids))
    #         .values(used = False)
    #     )
    #     conn.execute(stmt)
