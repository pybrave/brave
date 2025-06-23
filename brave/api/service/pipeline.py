import json
import os
import glob
from brave.api.config.config import get_settings
from pathlib import Path


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