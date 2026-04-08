import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from brave.api.core.evenet_bus import EventBus
from brave.api.core.event import AnalysisExecutorEvent
from brave.api.config.db import get_engine
from brave.api.dag.runtime_dag_queue_scheduler import RuntimeDagQueueScheduler
from brave.api.schemas.analysis_task import (
    PageAnalysisNodeQuery,
    PageAnalysisEdgeQuery,
    RuntimeScheduleQuery,
    RuntimeNodeReport,
    RuntimeAutoRunQuery,
)
from brave.api.service import analysis_node_service, analysis_edge_service, analysis_runtime_engine_service, analysis_service
from brave.api.core.routers_name import RoutersName
from brave.app_container import AppContainer
from dependency_injector.wiring import Provide, inject


analysis_runtime_api = APIRouter(prefix="/analysis-runtime")


@analysis_runtime_api.post("/nodes/page")
async def page_analysis_nodes(query: PageAnalysisNodeQuery):
    with get_engine().begin() as conn:
        return analysis_node_service.page_analysis_nodes(conn, query)


@analysis_runtime_api.post("/edges/page")
async def page_analysis_edges(query: PageAnalysisEdgeQuery):
    with get_engine().begin() as conn:
        return analysis_edge_service.page_analysis_edges(conn, query)


@analysis_runtime_api.post("/snapshot")
async def get_runtime_snapshot(query: RuntimeScheduleQuery):
    with get_engine().begin() as conn:
        return analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=query.analysis_id)


@analysis_runtime_api.post("/schedule-next")
@inject
async def schedule_next_runtime_node(query: RuntimeScheduleQuery,
                                     evenet_bus:EventBus = Depends(Provide[AppContainer.event_bus]) ):
    with get_engine().begin() as conn:
        # analysis = analysis_service.find_analysis_by_id(conn, query.analysis_id)  # check analysis existence
        node = analysis_runtime_engine_service.schedule_next(conn, analysis_id=query.analysis_id)
        snapshot = analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=query.analysis_id)

        if node:
            analysis_node_id = str(node.get("analysis_node_id") or "")
            if analysis_node_id:
                # asyncio.create_task(
                #     analysis_runtime_engine_service.run_simulated_executor(
                #         analysis_node_id=analysis_node_id,
                #     )
                # )
                analysis_executer_modal = await analysis_service.run_analysis_node(conn,node,"node")
                await evenet_bus.dispatch(RoutersName.ANALYSIS_EXECUTER_ROUTER,AnalysisExecutorEvent.ON_ANALYSIS_NODE_SUBMITTED,analysis_executer_modal)


    return {
        "scheduled": node,
        "snapshot": snapshot,
    }


@analysis_runtime_api.post("/report-node")
async def report_runtime_node(report: RuntimeNodeReport):
    with get_engine().begin() as conn:
        try:
            return analysis_runtime_engine_service.complete_node(
                conn,
                analysis_id=report.analysis_id,
                node_id=report.node_id,
                status=report.status,
                resolved_outputs=report.resolved_outputs,
                exit_code=report.exit_code,
                error_message=report.error_message,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@analysis_runtime_api.post("/auto-run")
@inject
async def auto_run_runtime(
    query: RuntimeAutoRunQuery,
    evenet_bus: EventBus = Depends(Provide[AppContainer.event_bus]),
):
    
    scheduler = RuntimeDagQueueScheduler(
        analysis_id=query.analysis_id,
        event_bus=evenet_bus,
        max_steps=query.max_steps or 10000,
        max_concurrency=query.max_concurrency or 4,
        queue_size=query.queue_size or 64,
        poll_interval_seconds=(query.poll_interval_ms or 500) / 1000.0,
        timeout_seconds=query.timeout_seconds,
    )
    # submit to background task and return immediately use asyncio.create_task, so that client can receive the response without waiting for the whole run to complete.
    asyncio.create_task(scheduler.run())
    # scheduler.run()
    
    return {
        "message": "Auto-run started",
    }





# 取消缓存
@analysis_runtime_api.post("/invalidate-cache/{analysis_id}")
async def invalidate_cache(analysis_id: str):
    with get_engine().begin() as conn:
        analysis_node_service.invalidate_cache(conn, analysis_id)
    return {"message": f"Cache invalidated for node {analysis_id}"}
   