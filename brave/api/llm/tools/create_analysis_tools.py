


import json
from brave.api.config.db import get_engine
from brave.api.schemas.pipeline import SavePipelineRelation
import brave.api.routes.pipeline as pipeline_routes
from brave.app_container import AppContainer

    
async def create_analysis_tools(arguments: dict):
    
    sse_service = AppContainer.sse_service()
    # {
    #     "name": "test",
    #     "component_id": "5c87d12e-9bf5-4c10-9e54-ef44c1328dd9",
    #     "input_component_ids": [
    #         "75087620-2ff8-4045-8694-a0c19aac12fc"
    #     ],
    #     "order_index": 0,
    #     "relation_type": "tools"
    # }
  
    name = arguments.get("name", "test")
    await pipeline_routes.save_pipeline_relation_controller(SavePipelineRelation(
        name=name,
        component_id="5c87d12e-9bf5-4c10-9e54-ef44c1328dd9",
        input_component_ids=["75087620-2ff8-4045-8694-a0c19aac12fc"],
        order_index=0,
        relation_type="tools"
    ))
    await sse_service.push_message({"group":"default","data":json.dumps({"msgType":"test222","msg":"hello"})})

    await sse_service.push_message({"group": "default", "data": json.dumps({
        "action": "create_analysis_tools",
        "status": "success",
    })})    
    return f"分析工具{name}创建成功"