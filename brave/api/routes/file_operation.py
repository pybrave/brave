import os
from fastapi import APIRouter, HTTPException, Query
import asyncio
from fastapi.responses import FileResponse
from brave.api.schemas.file_operation import WriteFile
from collections import defaultdict
from pathlib import Path
from brave.api.config.config import get_settings

file_locks = defaultdict(asyncio.Lock)

file_operation = APIRouter()


@file_operation.get("/file-operation/read-file")
async def read_file(file_path):
    if not os.path.exists(file_path):
        return {
            "content": [],
            "offset": 0
        }
    with open(file_path, 'r') as file:
        return file.read()

@file_operation.get("/file-operation/read-log-file")
async def read_log_file(file_path,offset:int=0):
    lock = file_locks[file_path]
    async with lock:
        if not os.path.exists(file_path):
            return {
                "content": [],
                "offset": 0
            }
        with open(file_path, 'r') as file:
            file.seek(offset)
            return {
                "content": file.readlines(),
                "offset": file.tell()
            }

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