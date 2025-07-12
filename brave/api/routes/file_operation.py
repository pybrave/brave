import os
from fastapi import APIRouter
import asyncio

from brave.api.schemas.file_operation import WriteFile
from collections import defaultdict

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
