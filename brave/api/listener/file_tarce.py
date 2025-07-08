import os
# from brave.api.routes.sse import global_queue
import asyncio
# from fastapi import Depends, FastAPI

import json

# def get_sse_service(app: FastAPI = Depends()):
#     return app.state.sse_service



async def file_change(change,file_path,sse_service):
    # sse_service = app.state.sse_service
    if "trace" in file_path:
        analysis_id = os.path.basename(file_path).replace(".trace.log","")
        # await asyncio.sleep(2)
        data = json.dumps({
            "analysis_id":analysis_id,
            "msgType":"trace"
        })
        msg = {"group": "default", "data": data}
        await sse_service.push_message(msg)
    elif "workflow" in file_path:
        analysis_id = os.path.basename(file_path).replace(".workflow.log","")
        # await asyncio.sleep(2)
        data = json.dumps({
            "analysis_id":analysis_id,
            "msgType":"workflow_log"
        })
        msg = {"group": "default", "data": data}
        await sse_service.push_message(msg)
    pass

async def process_end(analysis,sse_service):
    # sse_service = app.state.sse_service
    data = json.dumps({
        "analysis_id":analysis.get("analysis_id"),
        "msgType":"process_end",
        "analysis":analysis
    })
    msg = {"group": "default", "data": data}
    await sse_service.push_message(msg)