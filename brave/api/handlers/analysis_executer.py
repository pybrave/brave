
import asyncio
import json
from tkinter import E
from dependency_injector.wiring import inject
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
from dependency_injector.wiring import inject, Provide
from brave.api.core.routers_name import RoutersName
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.service import analysis_service
from brave.app_container import AppContainer
from brave.api.core.event import WorkflowEvent
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.executor.models import JobSpec, LocalJobSpec, DockerJobSpec
from brave.api.service.sse_service import SSESessionService
@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    router:AnalysisExecutorRouter  = Provide[AppContainer.analysis_executer_router],
    job_executor:JobExecutor = Provide[AppContainer.job_executor_selector],
    sse_service:SSESessionService = Provide[AppContainer.sse_service]):
    
    evenet_bus.register_router(RoutersName.ANALYSIS_EXECUTER_ROUTER,router)

    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED)
    async def on_analysis_submitted(payload:AnalysisExecuterModal):
        executer_type = "docker"
        print(f"🚀 [on_analysis_submitted] {payload.analysis_id}")
        if executer_type=="local":
            jsb_spec = JobSpec(
                job_id= payload.analysis_id,
                command=["bash", "run.sh"],
                output_dir= payload.output_dir,
                command_log_path= payload.command_log_path,

            )
        elif executer_type=="docker":
            jsb_spec = DockerJobSpec(
                job_id= payload.analysis_id,
                command_log_path= payload.command_log_path,
                command=["./run.sh"],
                output_dir= payload.output_dir,
                image=payload.image,
                env={},
                resources={}
            )
        await job_executor.submit_job(jsb_spec)

    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE)
    async def on_analysis_complete(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_complete] {payload.analysis_id}")
        asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,"finished"))
        await sse_service.push_message({"group": "default", "data": json.dumps({
            "analysis_id": payload.analysis_id,
            "event": "analysis_complete"
            })})

    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_FAILED)
    async def on_analysis_failed(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_failed] {payload.analysis_id}")
        asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,"failed"))
        await sse_service.push_message({"group": "default", "data": json.dumps({
            "analysis_id": payload.analysis_id,
            "event": "analysis_failed"
            })})
        # await sse_service.push_message({"group": "default", "data": json.dumps(msg)})
        # asyncio.create_task(analysis_service.finished_analysis(analysis.analysis_id))
        # result_parse_manage.remove(analysis.analysis_id)


