import brave.api.routes.pipeline as pipeline_routes
from brave.api.schemas.pipeline import FileConetent


async def update_analysis_script(arguments: dict):
    script_id = arguments.get("script_id")
    if not script_id:
        return "缺少 script_id 参数"
    script = arguments.get("script")
    if not script:
        return "缺少 script 参数"


    await pipeline_routes.save_script_by_component_id(script_id, FileConetent(
        content=script
    ))
    return f"分析工具脚本更新成功, script_id: {script_id}"