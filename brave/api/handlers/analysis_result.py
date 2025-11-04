
import json
from dependency_injector.wiring import inject
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
from dependency_injector.wiring import inject, Provide
from brave.api.core.routers.analysis_result_router import AnalysisResultRouter
from brave.api.core.routers_name import RoutersName
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import Analysis, AnalysisExecuterModal
from brave.api.schemas.analysis_result import AnalysisResult, AnalysisResultParseModal
from brave.app_container import AppContainer
from brave.api.core.event import AnalysisResultEvent, WorkflowEvent
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.executor.models import JobSpec, LocalJobSpec
from brave.api.service.sse_service import SSESessionService

@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    sse_service:SSESessionService = Provide[AppContainer.sse_service],
    router:AnalysisResultRouter  = Provide[AppContainer.analysis_result_router]):
    
    evenet_bus.register_router(RoutersName.ANALYSIS_RESULT_ROUTER,router)

    @router.on_event(AnalysisResultEvent.ON_ANALYSIS_RESULT_ADD)
    async def on_analysis_result_add(analysis:Analysis,analysis_result:AnalysisResultParseModal):
        print(f"🚀 [on_analysis_result_add] {analysis.analysis_id}")
        data = json.dumps({
            "msg":f"分析{analysis.analysis_id}，文件{analysis_result.file_name}保存成功!", 
            "component_ids":analysis_result.component_ids,
            "msgType":"analysis_result"
        })
        msg = {"group": "default", "data": data}
        await sse_service.push_message(msg)
  

    @router.on_event(AnalysisResultEvent.ON_ANALYSIS_RESULT_UPDATE)
    async def on_analysis_result_update(analysis:Analysis,analysis_result:AnalysisResultParseModal):
        print(f"🚀 [on_analysis_result_update] {analysis.analysis_id}")
        data = json.dumps({
            "msg":f"{analysis.analysis_id}更新成功!", 
            "add_num":analysis_result.add_num,
            "update_num":analysis_result.update_num,
            "complete_num":analysis_result.complete_num,
            "analysis_name":analysis.analysis_name,
            "component_ids":analysis_result.component_ids,
            "project":analysis.project,
            "msgType":"analysis_result"
        })
        msg = {"group": "default", "data": data}
        await sse_service.push_message(msg)
