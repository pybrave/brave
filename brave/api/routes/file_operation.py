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
import brave.api.service.file_operation as file_operation_service
import aiofiles

file_locks = defaultdict(asyncio.Lock)

file_operation = APIRouter()


@file_operation.get("/file-operation/read-file")
async def read_file(file_path):
    if not os.path.exists(file_path):
        return f"{file_path}文件不存在"
    try:
        # if file_path.endswith(".xlsx"):
        #     return pd.read_excel(file_path).to_json(orient="records")

        # with open(file_path, 'r') as file:
        #     return file.read()
        return file_operation_service.format_table_output(file_path,300)
    except Exception as e:
        return f"{file_path}文件读取失败: {e}"

# @file_operation.get("/file-operation/read-log-file")
# async def read_log_file(file_path,offset:int=0):
#     lock = file_locks[file_path]
#     async with lock:
#         if not os.path.exists(file_path):
#             return {
#                 "content": [],
#                 "offset": 0
#             }
#         with open(file_path, 'r') as file:
#             file.seek(offset)
#             return {
#                 "content": file.readlines(),
#                 "offset": file.tell()
#             }

@file_operation.get("/file-operation/read-log-file")
async def read_log_file(file_path: str, offset: int = 0):
    lock = file_locks[file_path]
    async with lock:
        if not os.path.exists(file_path):
            return {"content": [], "offset": 0}
        
        async with aiofiles.open(file_path, 'r') as file:
            await file.seek(offset)   # aiofiles 支持
            content = await file.readlines()
            offset = await file.tell()
        
        return {"content": content, "offset": offset}

# @app.get("/logs/delta")
# def get_incremental_logs(offset: int):
#     with open(LOG_FILE, "r") as f:
#         f.seek(offset)
#         new_data = f.read()
#         new_offset = f.tell()
#     return {
#         "logs": new_data,
#         "offset": new_offset
#     }


@file_operation.post("/file-operation/write-file")
async def write_file(writeFile:WriteFile):
    with open(writeFile.file_path, 'w') as file:
        file.write(writeFile.content)


@file_operation.get("/file-operation/file-list-recursive")
async def get_all_files_recursive(directory):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file).replace(directory,""))
    return file_list


@file_operation.get("/file-operation/list-dir")
def list_dir(path: str = ""):
    full_path = Path( path).resolve()
    get_setting = get_settings()
    if not full_path.exists() or not full_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid path")
    
    items = []
    for item in full_path.iterdir():
        items.append({
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else None,
            "modified": item.stat().st_mtime
        })
    return items


@file_operation.get("/file-operation/download")
def download_file(path: str):
    file_path = Path(path).resolve()
    get_setting = get_settings()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=file_path.name)



@file_operation.get("/file-operation/list-dir-v2")
def list_dir_v2(
    path: str = "",
    keyword: str = Query("", description="模糊搜索关键字"),
    page: int = 1,
    limit: int = 20,
):
    full_path = Path(  path).resolve()
    if not full_path.exists() or not full_path.is_dir() :
        raise HTTPException(status_code=400, detail="Invalid path")

    items = []
    for item in full_path.iterdir():
        if keyword.lower() in item.name.lower():
            items.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime,
            })

    # 分页处理
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    paged_items = items[start:end]

    return {
        "items": paged_items,
        "total": total,
        "page": page,
        "limit": limit,
    }




# def format_img_path(path):
#     settings = get_settings()
#     base_dir = settings.BASE_DIR
#     file_name = path.replace(str(base_dir),"")
#     # img_base64 = base64.b64encode(open(path, 'rb').read()).decode('utf-8')
#     return {
#         "data":f"/brave-api/dir{file_name}",
#         "type":"img",
#         "url":f"/brave-api/dir{file_name}"
#     }

# def format_table_output(path):
#     # pd.set_option("display.max_rows", 1000)     # 最多显示 1000 行
#     # pd.set_option("display.max_columns", 500)   # 最多显示 500 列
#     data = ""
#     data_type="table"
#     if path.endswith("xlsx"):
#         df = pd.read_excel(path, nrows=100).iloc[:, :50]
#         data = json.loads(df.to_json(orient="records")) 
#         data_type="table"
#     elif path.endswith("txt"):
#         with open(path,"r") as f:
#             data = f.read()
#         data_type="string"
#     else:
#         df = pd.read_csv(path,sep="\t", nrows=100).iloc[:, :50]
#         # df = pd.read_csv(path,sep="\t")
#         data = json.loads(df.to_json(orient="records")) 
#         data_type="table"

#     settings = get_settings()
#     base_dir = settings.BASE_DIR
#     file_name = path.replace(str(base_dir),"")
#     return  {
#         "data":data ,
#         "type":data_type,
#         "url":f"/brave-api/dir{file_name}"
#     }
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
@file_operation.get("/file-operation/visualization-results")
async def visualization_results(path):
    return await file_operation_service.visualization_results(path)
    # path = f"{path}/output"
    # images = []
    # for ext in ("*.png", "*.jpg", "*.jpeg"):
    #     images.extend(glob.glob(os.path.join(path, ext)))
    # images = [format_img_path(image) for image in images]
    # tables = []
    # for ext in ("*.csv", "*.tsv","*.txt", "*.xlsx"):
    #     tables.extend(glob.glob(os.path.join(path, ext)))
    # tables = [format_table_output(table) for table in tables]

    # # textList = []
    # # for ext in ("*.txt"):
    # #     textList.extend(glob.glob(os.path.join(path, ext)))

    # # textList = [format_text_output(text) for text in textList]

    # return {
    #     "images": images,
    #     "tables": tables
    # }
