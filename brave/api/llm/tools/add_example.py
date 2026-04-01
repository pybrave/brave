


import os
import time

from brave.api.schemas.analysis_result import ImportData
from brave.api.routes.sample_result import import_data
from brave.api.config.config import get_settings

async def add_example(arguments: dict):
    settings = get_settings()

    file_id = "75087620-2ff8-4045-8694-a0c19aac12fc"

    project = "default"

    content = arguments.get("content")
    if not content:
        return "缺少 content 参数，无法添加示例数据。"

    dir_path = f"{settings.PIPELINE_DIR}/file/{file_id}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # 使用时间戳生成随机文件名后缀，确保每次添加示例数据时文件名不同，避免冲突
    
    timestamp = int(time.time())
    file_path = f"{dir_path}/example_{timestamp}.txt"
    with open(file_path, "w") as f:
        f.write(content)

    import_data_list =[
        ImportData(
            component_id= file_id,
            project= project,
            content= file_path,
            file_type="collected",
            file_name= "example",
            # sample_source= "source",
        )
    ]
    await import_data(import_data_list)
    return "示例添加成功"