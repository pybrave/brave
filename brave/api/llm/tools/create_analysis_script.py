


import json
from brave.api.config.db import get_engine
from brave.api.schemas.pipeline import SavePipeline
import brave.api.routes.pipeline as pipeline_routes
from brave.app_container import AppContainer


# {
#     "component_name": "PCA",
#     "container_id": "af90160b-f9d3-493f-b1ad-aa59ca60bc59",
#     "script_type": "r",
#     "content": "{\n  \"formJson\": [\n    {\n      \"name\": \"x_input\",\n      \"label\": \"x input\",\n      \"component_id\": \"75087620-2ff8-4045-8694-a0c19aac12fc\",\n      \"db\": true,\n      \"group\": \"group_field\",\n      \"type\": \"CollectedSampleSelect\",\n      \"columns\": [\n        \"sample_vars\",\n        \"feature_var\"\n      ],\n      \"modes\": [\n        1,\n        0\n      ],\n      \"columns_rules\": [\n        1,\n        1\n      ],\n      \"rules\": [\n        {\n          \"required\": true,\n          \"message\": \"This field cannot be empty!\"\n        }\n      ]\n    }\n  ]\n}",
#     "component_type": "script"
# } 
async def create_analysis_script(arguments: dict):
    name = str(arguments.get("name", "")).strip()

    if not name:
        return "为工具创建脚本，根据工具名称自动生成脚本名称，例如：箱线图工具对应的脚本名称可以是“箱线图脚本”。"
    tools_id = str(arguments.get("tools_id", "")).strip()
    if not tools_id:
        return "缺少 tools_id 参数，无法关联到工具。"


    content ="{\n  \"formJson\": [\n    {\n      \"name\": \"x_input\",\n      \"label\": \"x input\",\n      \"component_id\": \"75087620-2ff8-4045-8694-a0c19aac12fc\",\n      \"db\": true,\n      \"group\": \"group_field\",\n      \"type\": \"CollectedSampleSelect\",\n      \"columns\": [\n        \"sample_vars\",\n        \"feature_var\"\n      ],\n      \"modes\": [\n        1,\n        0\n      ],\n      \"columns_rules\": [\n        1,\n        1\n      ],\n      \"rules\": [\n        {\n          \"required\": true,\n          \"message\": \"This field cannot be empty!\"\n        }\n      ]\n    }\n  ]\n}"
    await pipeline_routes.save_pipeline(SavePipeline(
        component_name=name,
        relation_id=tools_id,
        container_id="af90160b-f9d3-493f-b1ad-aa59ca60bc59",
        script_type="r",
        content=content,
        component_type="script"
    ))

    return f"分析脚本{name}创建成功"
