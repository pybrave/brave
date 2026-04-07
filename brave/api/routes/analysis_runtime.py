import asyncio

from fastapi import APIRouter
from fastapi import HTTPException

from brave.api.config.db import get_engine
from brave.api.schemas.analysis_task import (
    PageAnalysisNodeQuery,
    PageAnalysisEdgeQuery,
    RuntimeScheduleQuery,
    RuntimeNodeReport,
    RuntimeAutoRunQuery,
)
from brave.api.service import analysis_node_service, analysis_edge_service, analysis_runtime_engine_service


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
async def schedule_next_runtime_node(query: RuntimeScheduleQuery):
    with get_engine().begin() as conn:
        node = analysis_runtime_engine_service.schedule_next(conn, analysis_id=query.analysis_id)
        snapshot = analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=query.analysis_id)

    if node:
        node_id = str(node.get("node_id") or "")
        if node_id:
            asyncio.create_task(
                analysis_runtime_engine_service.run_simulated_executor(
                    analysis_id=query.analysis_id,
                    node_id=node_id,
                )
            )

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
async def auto_run_runtime(query: RuntimeAutoRunQuery):
    with get_engine().begin() as conn:
        return analysis_runtime_engine_service.auto_run(
            conn,
            analysis_id=query.analysis_id,
            max_steps=query.max_steps or 10000,
        )
