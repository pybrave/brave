from operator import and_
from brave.api.config.db import get_engine
from brave.api.models.core import analysis as t_analysis, t_pipeline_components,t_project
from sqlalchemy import select,update
from fastapi import HTTPException
import json
from brave.api.schemas.analysis import QueryAnalysis
import  brave.api.service.pipeline as pipeline_service
import importlib
import hashlib
import os
from brave.api.enum.component_script import ScriptName

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
    if component_.component_type == "pipeline":
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
        component_file_content_list = [{**json.loads(item.content),"component_id":item['component_id']} for item in component_file_list]
        file_format_list = [
            {"dir":item['dir'],"fileFormat":item['fileFormat'],"name":item['name'],"component_id":item['component_id']}
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


    # py_module = pipeline_service.find_module(component_.namespace,"py_parse_analysis_result",component_id,parse_analysis_result_module,'py')['module']
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
    result_dict = {}
    result_list = []
    for item in file_format_list:        
        dir_path = f"{analysis['output_dir']}/output/{item['dir']}"
        res = None    
        args = {
            "dir_path":dir_path,
            # "analysis": dict(result),
            "file_format":item['fileFormat']
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


def find_running_analysis(conn):
    stmt = select(t_analysis).where(t_analysis.c.analysis_status=="running")
    result = conn.execute(stmt).mappings().all()
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


async def finished_analysis(analysis_id,status):
    with get_engine().begin() as conn:  
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(process_id=None,analysis_status = status)
        )
        conn.execute(stmt)
        conn.commit()
    print(f"Analysis {analysis_id} {status}")




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

    stmt = select(
        t_analysis,
        t_pipeline_components.c.component_name.label("component_name"),
        # t_pipeline_components.c.label.label("component_label"),
        t_pipeline_components.c.component_type.label("component_type"),
        t_project.c.project_name.label("project_name")
    )
    stmt = stmt.select_from(
        t_analysis.outerjoin(t_pipeline_components,t_analysis.c.component_id==t_pipeline_components.c.component_id)
        .outerjoin(t_project,t_analysis.c.project==t_project.c.project_id)
        )
    if conditions:
        stmt = stmt.where(and_(*conditions))
    return conn.execute(stmt).mappings().all()