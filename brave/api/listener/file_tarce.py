import os
# from brave.api.routes.sse import global_queue
import asyncio
# from fastapi import Depends, FastAPI

import json
from turtle import update

from brave.api.service.analysis_result_parse import AnalysisResultParse
from brave.api.service.sse_service import SSESessionService
# def get_sse_service(app: FastAPI = Depends()):
#     return app.state.sse_service
from brave.api.config.db import get_engine
from brave.api.models.core import analysis as t_analysis
from sqlalchemy import select, update


async def file_change(change,file_path,sse_service:SSESessionService,analysis_result_parse_service:AnalysisResultParse):
    # sse_service = app.state.sse_service
    if "trace" in file_path:
        analysis_id = os.path.basename(file_path).replace(".trace.log","")
        # await asyncio.sleep(2)
        data = json.dumps({
            "analysis_id":analysis_id,
            "msgType":"trace",
            "msg":f"监控分析{analysis_id}文件{file_path}发生变化!"
        })
        print(f"监控分析{analysis_id}文件{file_path}发生变化!")

        msg = {"group": "default", "data": data}
        await sse_service.push_message(msg)
        await analysis_result_parse_service.add_change_analysis_id(analysis_id)
        # await analysis_result_parse_service.auto_save_analysis_result(analysis_id)
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

async def process_end(analysis,sse_service,analysis_result_parse_service:AnalysisResultParse):
    analysis_id = analysis.get("analysis_id")
    with get_engine().begin() as conn:  
        stmt = (
            update(t_analysis)
            .where(t_analysis.c.analysis_id == analysis_id)
            .values(process_id=None,analysis_status = "finished")
        )
        conn.execute(stmt)
        conn.commit()

    # sse_service = app.state.sse_service
    data = json.dumps({
        "analysis_id":analysis.get("analysis_id"),
        "msgType":"process_end",
        "analysis":analysis
    })
    msg = {"group": "default", "data": data}
    await analysis_result_parse_service.add_remove_analysis_id(analysis.get("analysis_id"))
    await sse_service.push_message(msg)



async def analysis_result_add(analysis,analysis_result,sse_service):
    data = json.dumps({
        "msg":f"分析{analysis['analysis_id']}，文件{analysis_result['file_name']}保存成功!",
        "msgType":"analysis_result",
        "component_id":analysis_result['component_id']
    })
    msg = {"group": "default", "data": data}
    await sse_service.push_message(msg)

async def analysis_result_update(analysis,analysis_result,sse_service):
    data = json.dumps({
        "msg":f"分析{analysis['analysis_id']}，文件{analysis_result['file_name']}更新成功!",
        "msgType":"analysis_result",
        "component_id":analysis_result['component_id']
    })
    msg = {"group": "default", "data": data}
    await sse_service.push_message(msg)