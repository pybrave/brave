import os
from brave.api.routes.sse import global_queue
import asyncio
import json

async def run(change,path):
    if "trace" in path:
        analysis_id = os.path.basename(path).replace(".trace.log","")
        # await asyncio.sleep(2)
        await global_queue.put(json.dumps({
            "analysis_id":analysis_id,
            "msgType":"trace"
        }))
    pass