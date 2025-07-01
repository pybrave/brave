import json
import os
import glob
from brave.api.config.config import get_settings
from pathlib import Path
import shutil
from fastapi import HTTPException
from brave.api.schemas.pipeline import SavePipeline,Pipeline,QueryPipeline,QueryModule
from brave.api.config.db import get_engine
from brave.api.models.core import t_pipeline_components
import importlib.resources as resources
from sqlalchemy import select, and_, join, func,insert,update


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

def find_module(module_type,module_dir,module_name):

    all_module = get_all_module(module_type)

    if module_dir not in all_module:
        raise HTTPException(status_code=500, detail=f"目录{module_type}: {module_dir}/{module_type}/{module_name}没有找到!")
    py_module_dir = all_module[module_dir]
    if module_name not in py_module_dir:
        raise HTTPException(status_code=500, detail=f"文件{module_type}:  {module_dir}/{module_type}/{module_name}没有找到!!")
    py_module = py_module_dir[module_name]
    return py_module

def get_all_module(module_type):
    suffix = ""
    if module_type.startswith("py_"):
        suffix = "py"
    else:
        suffix = "nf"
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/*/{module_type}/*.{suffix}")
    result = {}
    for item in nextflow_list:
        
        parts = item.split(os.sep)
        dir_name = parts[-3]
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

def create_file(component_id,content,component_type):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{component_id}"
    if component_type == "pipeline":
        analysisPipline = f"{pipeline_dir}/nextflow/{content['analysisPipline']}.nf"
        if not os.path.exists(analysisPipline):
            with open(analysisPipline,"w") as f:
                f.write("")
        if not os.path.exists(parseAnalysisModule):
            with open(parseAnalysisModule,"w") as f:
                f.write("")

    if component_type == "software":
        parseAnalysisModule = f"{pipeline_dir}/py_parse_analysis/{content['parseAnalysisModule']}.py"
        analysisPipline = f"{pipeline_dir}/nextflow/{content['analysisPipline']}.nf"
        dir_list = [parseAnalysisModule,analysisPipline]
        for item in dir_list:
            dir_ = os.path.dirname(item)
            if not os.path.exists(dir_):
                os.makedirs(dir_) 
        
        if not os.path.exists(analysisPipline):
            with resources.files("brave.templete").joinpath("nextflow.nf").open("r") as f:
                content_text = f.read()
            with open(analysisPipline,"w") as f:
                f.write(content_text)
        if not os.path.exists(parseAnalysisModule):
            with resources.files("brave.templete").joinpath("py_parse_analysis.py").open("r") as f:
                content_text = f.read()
            with open(parseAnalysisModule,"w") as f:
                f.write(content_text)
        
        if "parseAnalysisResultModule" in  content:
            parseAnalysisResultModule = content['parseAnalysisResultModule']
            for item in parseAnalysisResultModule:
                item_file = f"{pipeline_dir}/py_parse_analysis_result/{item['module']}.py"
                dir_ = os.path.dirname(item_file)
                if not os.path.exists(dir_):
                    os.makedirs(dir_) 
                if not os.path.exists(item_file):
                    with resources.files("brave.templete").joinpath("py_parse_analysis_result.py").open("r") as f:
                        content_text = f.read()
                    with open(item_file,"w") as f:
                        f.write(content_text)

    if component_type == "downstream":
        py_plot = f"{pipeline_dir}/py_plot/{content['moduleName']}.py"
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
    find_pipeine = conn.execute(stmt).fetchone()
    return find_pipeine

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