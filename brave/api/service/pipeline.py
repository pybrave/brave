import json
import os
import glob
from brave.api.config.config import get_settings
from pathlib import Path
import shutil


def get_pipeline_dir():
    settings = get_settings()
    return settings.PIPELINE_DIR

def get_pipeline_list():
    pipeline_dir =  get_pipeline_dir()
    pipeline_files = glob.glob(f"{pipeline_dir}/*/main.json")
    return pipeline_files
def get_module_name(item):
    pipeline_dir =  get_pipeline_dir()
    item = item.replace(f"{pipeline_dir}/","").replace("/",".")
    item = Path(item).stem 
    return item 
    # f'reads-alignment-based-abundance-analysis.py_plot.{module_name}'

def get_all_module(type):
    pipeline_dir =  get_pipeline_dir()
    nextflow_list = glob.glob(f"{pipeline_dir}/*/{type}/*.py")
    nextflow_dict = {os.path.basename(item).replace(".py",""):get_module_name(item) for item in nextflow_list}
    return nextflow_dict

def delete_wrap_pipeline_dir(pipeline_key):
    pipeline_dir =  get_pipeline_dir()
    src  =f"{pipeline_dir}/{pipeline_key}"
    dst  =f"{pipeline_dir}/bin"
    if not os.path.exists(dst):
        os.makedirs(dst)
    if os.path.exists(src):
        shutil.move(src,dst)

def create_wrap_pipeline_dir(pipeline_key):
    pipeline_dir = get_pipeline_dir()
    img = f"{pipeline_dir}/{pipeline_key}/img"
    nextflow = f"{pipeline_dir}/{pipeline_key}/nextflow"
    py_parse_analysis = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis"
    py_parse_analysis_result = f"{pipeline_dir}/{pipeline_key}/py_parse_analysis_result"
    py_plot = f"{pipeline_dir}/{pipeline_key}/py_plot"
    dir_list = [img, nextflow,py_parse_analysis,py_parse_analysis_result,py_plot]
    for item in dir_list:
        if not os.path.exists(item):
            os.makedirs(item) 

def create_file(pipeline_key,pipeline_type,content):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{pipeline_key}"
    if pipeline_type == "wrap_pipeline":
        analysisPipline = f"{pipeline_dir}/nextflow/{content['analysisPipline']}.nf"
        parseAnalysisModule = f"{pipeline_dir}/py_parse_analysis/{content['parseAnalysisModule']}.py"
        if not os.path.exists(analysisPipline):
            with open(analysisPipline,"w") as f:
                f.write("")
        if not os.path.exists(parseAnalysisModule):
            with open(parseAnalysisModule,"w") as f:
                f.write("")

    