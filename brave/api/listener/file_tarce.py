import os
from brave.api.routes.sse import global_queue
import asyncio
import json

async def file_change(change,file_path):
    if "trace" in file_path:
        analysis_id = os.path.basename(file_path).replace(".trace.log","")
        # await asyncio.sleep(2)
        await global_queue.put(json.dumps({
            "analysis_id":analysis_id,
            "msgType":"trace"
        }))
    elif "workflow" in file_path:
        analysis_id = os.path.basename(file_path).replace(".workflow.log","")
        # await asyncio.sleep(2)
        await global_queue.put(json.dumps({
            "analysis_id":analysis_id,
            "msgType":"workflow_log"
        }))
    pass

async def process_end(analysis_id):
    await global_queue.put(json.dumps({
        "analysis_id":analysis_id,
        "msgType":"process_end"
    }))