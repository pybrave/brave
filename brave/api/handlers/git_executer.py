
import asyncio
import json
from dependency_injector.wiring import inject
from fastapi import HTTPException
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
from dependency_injector.wiring import inject, Provide
from brave.api.core.routers.git_executer_router import GitExecuterRouter
from brave.api.core.routers_name import RoutersName
from brave.api.dag.runtime_dag_queue_scheduler import RuntimeDagQueueScheduler
from brave.api.dag.running_dag_registry import running_dag_registry
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.service import analysis_node_service, analysis_runtime_engine_service, analysis_service
from brave.app_container import AppContainer
from brave.api.core.event import GitExecutorEvent, WorkflowEvent
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.executor.models import JobSpec, LocalJobSpec, DockerJobSpec
from brave.api.service.realtime_service import RealtimeService
from brave.api.service.result_parse.analysis_manage import AnalysisManage
from brave.api.executor.local_executor import LocalExecutor
from  brave.api.service import store_service 


@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    router:GitExecuterRouter  = Provide[AppContainer.git_executer_router],
    # job_executor:JobExecutor = Provide[AppContainer.job_executor_selector],
    sse_service:RealtimeService = Provide[AppContainer.sse_service]):
    
    evenet_bus.register_router(RoutersName.GIT_EXECUTER_ROUTER,router)


    @router.on_event(GitExecutorEvent.ON_GIT_CLONE)
    async def on_git_clone(payload:dict):
        print(f"🚀 [on_git_clone] ")
        store_id = payload.get("store_id")

        ##
        # 执行 git clone 的逻辑
        ###
        

        store_service.update_store_status(store_id,"done")
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "store",
                "id":  store_id,
                "method": "clone",
                "args": {
                    "status": "done",
                    "id": store_id
                }
            }
        }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})
    
    @router.on_event(GitExecutorEvent.ON_GIT_PULL)
    async def on_git_pull(payload:dict):
        print(f"🚀 [on_git_pull] ")
    
    @router.on_event(GitExecutorEvent.ON_GIT_PUSH)
    async def on_git_push(payload:dict):
        print(f"🚀 [on_git_push] ")
    
    @router.on_event(GitExecutorEvent.ON_GIT_STOP)
    async def on_git_stop(payload:dict):
        print(f"🚀 [on_git_stop] ")

