


import json
from brave.api.config.db import get_engine
from brave.api.schemas.pipeline import SavePipeline
import brave.api.routes.pipeline as pipeline_routes
from brave.app_container import AppContainer



async def update_analysis_script_from(arguments: dict):

   
    script_id = str(arguments.get("script_id", "")).strip()
    if not script_id:
        return "缺少 script_id 参数，无法更新表单json。"

    content = arguments.get("content")
    if not content:
        return "缺少 content 参数，无法更新表单json。"

    script_id = await pipeline_routes.update_or_save_components(SavePipeline(
        component_id=script_id,
        content=content,
        component_type="script",
    ))

    return f"分析脚本{script_id}表单更新成功"
