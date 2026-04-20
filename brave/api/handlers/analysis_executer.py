
import asyncio
import json
from dependency_injector.wiring import inject
from fastapi import HTTPException
from brave.api.config.db import get_engine
from brave.api.core.evenet_bus import EventBus
from brave.api.core.routers.analysis_executer_router import AnalysisExecutorRouter
from dependency_injector.wiring import inject, Provide
from brave.api.core.routers_name import RoutersName
from brave.api.dag.runtime_dag_queue_scheduler import RuntimeDagQueueScheduler
from brave.api.executor.base import JobExecutor
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.service import analysis_node_service, analysis_runtime_engine_service, analysis_service
from brave.app_container import AppContainer
from brave.api.core.event import WorkflowEvent
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.executor.models import JobSpec, LocalJobSpec, DockerJobSpec
from brave.api.service.realtime_service import RealtimeService
from brave.api.service.result_parse.analysis_manage import AnalysisManage
from brave.api.executor.local_executor import LocalExecutor

@inject
def setup_handlers(
    evenet_bus:EventBus  = Provide[AppContainer.event_bus],
    router:AnalysisExecutorRouter  = Provide[AppContainer.analysis_executer_router],
    job_executor:JobExecutor = Provide[AppContainer.job_executor_selector],
    sse_service:RealtimeService = Provide[AppContainer.sse_service],
    result_parse_manage:AnalysisManage = Provide[AppContainer.result_parse_manage]):
    
    evenet_bus.register_router(RoutersName.ANALYSIS_EXECUTER_ROUTER,router)

    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_SUBMITTED)
    async def on_analysis_submitted(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_submitted] {payload.analysis_id}")
        await job_executor.submit_job(payload)

    @router.on_event(AnalysisExecutorEvent.ON_DAG_SUBMITTED)
    async def on_dag_submitted(payload:AnalysisExecuterModal):
        print(f"🚀 [on_dag_submitted] {payload.analysis_id}")
        # await job_executor.submit_job(payload)
        analsyis_id =payload.analysis_id
        scheduler = RuntimeDagQueueScheduler(
            analysis_id=analsyis_id,
            event_bus=evenet_bus,
            max_steps=10000,
            max_concurrency=1,
            queue_size= 64,
            poll_interval_seconds= 500 / 1000.0,
            timeout_seconds=None,
        )
        # submit to background task and return immediately use asyncio.create_task, so that client can receive the response without waiting for the whole run to complete.
        asyncio.create_task(scheduler.run())
        asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,"job","running"))
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  payload.analysis_id,
                "method": "analysisStarted",
                "args": {
                    "status": "running",
                    "id": payload.analysis_id
                }
            }
        }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})

    @router.on_event(AnalysisExecutorEvent.ON_DAG_COMPLETE)
    async def on_dag_complete(payload:dict):
        analysis_id = payload.get('analysis_id')
        print(f"🚀 [on_dag_complete] {analysis_id}")
        asyncio.create_task(analysis_service.finished_analysis(analysis_id,"job","done"))
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  analysis_id,
                "method": "analysisDone",
                "args": {
                    "status": "done",
                    "id": analysis_id
                }
            }
        }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})


        
    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_NODE_SUBMITTED)
    async def on_analysis_node_submitted(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_node_submitted] {payload.analysis_id}")
        analysis_id = None
        if  payload.run_type =="node":
            asyncio.create_task(analysis_node_service.finished_analysis_node_conn(payload.analysis_id,payload.run_type,"submitted"))
            analysis_node = await analysis_node_service.find_by_analysis_node_id_conn(payload.analysis_id)
            analysis_id = analysis_node.get("analysis_id") 

        await job_executor.submit_job(payload)

        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  payload.analysis_id,
                "parentId": analysis_id,
                "method": "analysisSubmitted",
                "args": {
                    "status": "submitted",
                    "id": payload.analysis_id
                }
            }
        }
     
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})
  

    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_STARTED)
    async def on_analysis_started(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_started] {payload.analysis_id} {payload.run_type}")
        analysis_id = None
        if  payload.run_type =="node":
            asyncio.create_task(analysis_node_service.finished_analysis_node_conn(payload.analysis_id,payload.run_type,"running"))
            analysis_node = await analysis_node_service.find_by_analysis_node_id_conn(payload.analysis_id)
            analysis_id = analysis_node.get("analysis_id") 
        elif payload.run_type =="nserver":
            asyncio.create_task(analysis_node_service.finished_analysis_node_conn(payload.analysis_id,payload.run_type,"running"))

        # if payload.run_type =="server":
        #     await analysis_service.update_url(payload.analysis_id,f"http://10.110.1.11:5003/container/{payload.analysis_id}")

                 
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  payload.analysis_id,
                "parentId": analysis_id,
                "method": "analysisStarted",
                "args": {
                    "status": "running",
                    "id": payload.analysis_id
                }
            }
        }
        # {
        #     "analysis_id": payload.analysis_id,
        #     "event": "analysis_started",
        #      "run_id": payload.run_id,
        #     "run_type":payload.run_type
        #     }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})
  




    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_STOPED)
    async def on_analysis_stoped(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_stoped] {payload.analysis_id}")
        await job_executor.remove_job(payload.run_id)
        # if payload.run_type =="job":
        #     asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,payload.run_type,"failed"))
        # else:
        #     asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,payload.run_type,"stoped"))

    
    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_COMPLETE)
    async def on_analysis_complete(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_complete] {payload.analysis_id} {payload.run_type}")
        analysis_id = None
        if payload.run_type =="job":
            asyncio.create_task(result_parse_manage.parse(payload.analysis_id))
            
            asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,payload.run_type,"finished"))
        elif payload.run_type =="server":
            asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,payload.run_type,"stopped"))
        elif payload.run_type =="nserver":
             asyncio.create_task(analysis_node_service.finished_analysis_node_conn(payload.analysis_id,payload.run_type,"stopped"))
        elif payload.run_type =="node":
            analysis_node = await analysis_node_service.find_by_analysis_node_id_conn(payload.analysis_id)
            analysis_id = analysis_node.get("analysis_id") 
            asyncio.create_task(analysis_runtime_engine_service.complete_node_conn(payload.analysis_id,"done"))

        # if payload.run_type !="retry":
        #     if payload.run_type =="job":
        #         asyncio.create_task(result_parse_manage.parse(payload.analysis_id))
        #         # await result_parse_manage.parse(payload.analysis_id)
            
        #     elif payload.run_type =="server":
        #         await analysis_service.update_ports(payload.analysis_id,None )
                
        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  payload.analysis_id,
                "parentId": analysis_id,
                "method": "analysisDone",
                "args": {
                    "status": "done",
                     "id": payload.analysis_id
                }
            }
        }

        # {
        #     "analysis_id": payload.analysis_id,
        #     "event": "analysis_complete",
        #      "run_id": payload.run_id,
        #     "run_type":payload.run_type
            
        #     }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})


    @router.on_event(AnalysisExecutorEvent.ON_ANALYSIS_FAILED)
    async def on_analysis_failed(payload:AnalysisExecuterModal):
        print(f"🚀 [on_analysis_failed] {payload.analysis_id}")
        analysis_id = None
        if payload.run_type =="server":
            await analysis_service.update_url(payload.analysis_id,None )
        elif payload.run_type =="nserver":
            asyncio.create_task(analysis_node_service.finished_analysis_node_conn(payload.analysis_id,payload.run_type,"stopped"))
        elif payload.run_type =="node":
            analysis_node = await analysis_node_service.find_by_analysis_node_id_conn(payload.analysis_id)
            analysis_id = analysis_node.get("analysis_id") 
            asyncio.create_task(analysis_runtime_engine_service.complete_node_conn(payload.analysis_id,"failed"))
        elif payload.run_type !="retry":
            asyncio.create_task(analysis_service.finished_analysis(payload.analysis_id,payload.run_type,"failed"))

        data = {
            "action": "component.invoke",
            "payload": {
                "category": "analysis",
                "id":  payload.analysis_id,
                "parentId": analysis_id,
                "method": "analysisDone",
                "args": {
                    "status": "done",
                     "id": payload.analysis_id
                }
            }
        }
        # {
        #     "analysis_id": payload.analysis_id,
        #     "event": "analysis_failed",
        #      "run_id": payload.run_id,
        #     "run_type":payload.run_type
        #     }
        await sse_service.push_message({"group": "default", "data": json.dumps(data)})
 

    @router.on_event(AnalysisExecutorEvent.ON_CONTAINER_PULLED)
    async def on_container_pulled(payload:AnalysisExecuterModal):
        await sse_service.push_message({"group": "default", "data": json.dumps({
            "analysis_id": payload.analysis_id,
            "run_id": payload.run_id,
            "event": "container_pulled",
            "run_type":payload.run_type
        })})