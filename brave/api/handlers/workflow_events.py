# workflow_event_system/handlers/workflow_events.py

from dependency_injector.wiring import inject
from brave.api.core.routers.workflow_event_router import WorkflowEventRouter
from dependency_injector.wiring import inject, Provide
from brave.api.schemas.analysis import Analysis
from brave.api.service.result_parse.analysis_manage import AnalysisManage
from brave.app_container import AppContainer
from brave.api.core.event import WorkflowEvent
from brave.api.core.evenet_bus import EventBus
import brave.api.service.analysis_service as analysis_service
import asyncio
from brave.api.service.sse_service import SSESessionService
import json
@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    router: WorkflowEventRouter = Provide[AppContainer.workflow_event_router],
    sse_service:SSESessionService = Provide[AppContainer.sse_service],
    result_parse_manage:AnalysisManage = Provide[AppContainer.result_parse_manage]
    ):


            
    @router.on_event(WorkflowEvent.ON_FLOW_BEGIN)
    async def on_flow_begin(analysis:Analysis,msg: dict):
        print(f"🚀 [on_flow_begin] {msg['analysis_id']}")
        await sse_service.push_message({"group": "default", "data": json.dumps(msg)})
        # result_parse_manage.create(analysis.analysis_id)

    @router.on_event(WorkflowEvent.ON_FILE_PUBLISH)
    async def on_file_publish(analysis:Analysis,msg: dict):
        print(f"✅ [on_file_publish] {msg['analysis_id']}")
        await sse_service.push_message({"group": "default", "data": json.dumps(msg)})
        # await result_parse_manage.parse(analysis.analysis_id)




    @router.on_event(WorkflowEvent.ON_PROCESS_COMPLETE)
    async def on_process_complete(analysis:Analysis,msg: dict):
        print(f"🚀 [on_process_complete] {msg['analysis_id']}")
        await sse_service.push_message({"group": "default", "data": json.dumps(msg)})
        # await result_parse_manage.parse(analysis.analysis_id)


    @router.on_event(WorkflowEvent.ON_FLOW_COMPLETE)
    async def on_flow_complete(analysis:Analysis,msg: dict):
        print(f"🚀 [on_flow_complete] {msg['analysis_id']}")
        await sse_service.push_message({"group": "default", "data": json.dumps(msg)})
        # await result_parse_manage.parse(analysis.analysis_id)

        # result_parse_manage.remove(analysis.analysis_id)
        


    # @router.on_event(WorkflowEvent.ON_JOB_SUBMITTED)
    # async def on_job_submitted(analysis:Analysis,msg: dict):
    #     print(f"🚀 [on_job_submitted] {msg['job_id']}")

