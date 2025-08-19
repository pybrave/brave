import glob
import os
from fastapi import APIRouter, HTTPException, Query
import asyncio
from fastapi.responses import FileResponse
from brave.api.schemas.file_operation import WriteFile
from collections import defaultdict
from pathlib import Path
from brave.api.config.config import get_settings
import pandas as pd
import json


def format_img_path(path):
    settings = get_settings()
    base_dir = settings.BASE_DIR
    file_name = path.replace(str(base_dir),"")
    # img_base64 = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
    return {
        "data":f"/brave-api/dir{file_name}",
        "type":"img",
        "url":f"/brave-api/dir{file_name}"
    }

def format_table_output(path):
    # pd.set_option("display.max_rows", 1000)     # 最多显示 1000 行
    # pd.set_option("display.max_columns", 500)   # 最多显示 500 列
    data = ""
    data_type="table"
    if path.endswith("xlsx"):
        df = pd.read_excel(path, nrows=100).iloc[:, :50]
        data = json.loads(df.to_json(orient="records")) 
        data_type="table"
    elif path.endswith("sh") :
        with open(path,"r") as f:
            data = f.read()
        data_type="text"
    elif path.endswith("tsv"):
        df = pd.read_csv(path,sep="\t", nrows=100).iloc[:, :50]
        # df = pd.read_csv(path,sep="\t")
        data = json.loads(df.to_json(orient="records")) 
        data_type="table"
    elif path.endswith("json"):
        with open(path,"r") as f:
            data = f.read()
        data_type="json"
    else:
        with open(path,"r") as f:
            data = f.read()
        data_type="string"
      

    settings = get_settings()
    base_dir = settings.BASE_DIR
    file_name = path.replace(str(base_dir),"")
    return  {
        "data":data ,
        "type":data_type,
        "url":f"/brave-api/dir{file_name}"
    }
# def format_table_output(path):
#     with open(path,"r") as f:
#         text = f.read()
#     settings = get_settings()
#     base_dir = settings.BASE_DIR
#     file_name = path.replace(str(base_dir),"")
#     return  {
#         "data":text ,
#         "type":"table",
#         "url":f"/brave-api/dir{file_name}"
#     }
def visualization_results(path):

    path = f"{path}/output"
    images = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        images.extend(glob.glob(os.path.join(path, ext)))
    images = [format_img_path(image) for image in images]
    tables = []
    for ext in ("*.csv", "*.tsv","*.txt", "*.xlsx"):
        tables.extend(glob.glob(os.path.join(path, ext)))
    tables = [format_table_output(table) for table in tables]

    # textList = []
    # for ext in ("*.txt"):
    #     textList.extend(glob.glob(os.path.join(path, ext)))

    # textList = [format_text_output(text) for text in textList]

    return {
        "images": images,
        "tables": tables
    }
