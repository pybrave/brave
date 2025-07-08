from fastapi import APIRouter

from brave.api.schemas.file_operation import WriteFile

file_operation = APIRouter()


@file_operation.get("/file-operation/read-file")
async def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


@file_operation.post("/file-operation/write-file")
async def write_file(writeFile:WriteFile):
    with open(writeFile.file_path, 'w') as file:
        file.write(writeFile.content)

