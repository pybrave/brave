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
from brave.api.dag.running_dag_registry import running_dag_registry
from brave.api.schemas.analysis_task import (
    PageAnalysisNodeQuery,
    PageAnalysisEdgeQuery,
    RuntimeScheduleQuery,
    RuntimeNodeReport,
    RuntimeAutoRunQuery,
)
from brave.api.schemas.analysis import AnalysisExecuterModal
from brave.api.service import analysis_node_service, analysis_edge_service, analysis_runtime_engine_service, analysis_service
from brave.api.core.routers_name import RoutersName
from brave.app_container import AppContainer
from dependency_injector.wiring import Provide, inject


analysis_runtime_api = APIRouter(prefix="/analysis-runtime")


async def _watch_dag_run(analysis_id: str, dag_task: asyncio.Task):
    try:
        result = await dag_task
        if isinstance(result, dict):
            await running_dag_registry.mark_finished(analysis_id, result=result)
        else:
            await running_dag_registry.mark_finished(analysis_id, result={"result": str(result)})
    except asyncio.CancelledError:
        await running_dag_registry.mark_failed(analysis_id, error="dag scheduler task was cancelled")
        return
    except Exception as exc:
        await running_dag_registry.mark_failed(analysis_id, error=str(exc))


async def _stop_running_dag_background(analysis_id: str, evenet_bus: EventBus):
    # Stop all currently running node containers under this DAG.
    running_nodes = []
    with get_engine().begin() as conn:
        node_items = analysis_node_service.find_running_analysis_node(conn)
        running_nodes = [item for item in node_items if item.get("analysis_id") == analysis_id]

    stop_node_errors = []
    for node in running_nodes:
        run_id = str(node.get("run_id") or "")
        if not run_id:
            continue
        try:
            payload = AnalysisExecuterModal(
                analysis_id=str(node.get("analysis_node_id") or ""),
                run_id=run_id,
                run_type=str(node.get("run_type") or "node"),
            )
            await evenet_bus.dispatch(
                RoutersName.ANALYSIS_EXECUTER_ROUTER,
                AnalysisExecutorEvent.ON_ANALYSIS_STOPED,
                payload,
            )
        except Exception as exc:
            stop_node_errors.append({"run_id": run_id, "error": str(exc)})

    # Wait until no running nodes remain.
    wait_timeout_seconds = 60
    wait_interval_seconds = 1
    elapsed = 0
    final_snapshot = None
    while elapsed < wait_timeout_seconds:
        with get_engine().begin() as conn:
            final_snapshot = analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=analysis_id)
        running_count = int(final_snapshot.get("status_count", {}).get("running", 0))
        if running_count == 0:
            break
        await asyncio.sleep(wait_interval_seconds)
        elapsed += wait_interval_seconds

    running_count = int((final_snapshot or {}).get("status_count", {}).get("running", 0))

    scheduler_stop_result = await running_dag_registry.stop_running(
        analysis_id,
        wait_for_completion=True,
        timeout_seconds=10.0,
        cancel_on_timeout=True,
    )

    if running_count == 0:
        await analysis_service.finished_analysis(analysis_id, "job", "stopped")

    if stop_node_errors:
        print(f"[analysis_runtime] stop DAG node stop errors: analysis_id={analysis_id} errors={stop_node_errors}")
    if running_count != 0:
        print(
            f"[analysis_runtime] stop DAG timed out waiting for nodes: analysis_id={analysis_id} "
            f"running_count={running_count} scheduler_stop_result={scheduler_stop_result}"
        )


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
        find_analysis = analysis_service.find_analysis_by_id(conn, query.analysis_id)  # check analysis existence
        snapshot = analysis_runtime_engine_service.get_runtime_snapshot(conn, analysis_id=query.analysis_id)
    running_item = await running_dag_registry.get_running(query.analysis_id)
    snapshot["running_info"] = running_item
    snapshot["status"] = find_analysis.get("job_status") if find_analysis else None
    snapshot["is_cache"] = find_analysis.get("is_cache") if find_analysis else None
    snapshot["server_status"] = find_analysis.get("server_status") if find_analysis else None
    return  snapshot


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
    max_steps = query.max_steps or 10000
    max_concurrency = query.max_concurrency or 4
    queue_size = query.queue_size or 64
    poll_interval_seconds = (query.poll_interval_ms or 500) / 1000.0
    timeout_seconds = query.timeout_seconds

    scheduler = RuntimeDagQueueScheduler(
        analysis_id=query.analysis_id,
        event_bus=evenet_bus,
        max_steps=max_steps,
        max_concurrency=max_concurrency,
        queue_size=queue_size,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=timeout_seconds,
    )
    # submit to background task and return immediately use asyncio.create_task, so that client can receive the response without waiting for the whole run to complete.
    dag_task = asyncio.create_task(scheduler.run(), name=f"dag-run-{query.analysis_id}")
    await running_dag_registry.register(
        analysis_id=query.analysis_id,
        task_name=dag_task.get_name(),
        source="api.analysis_runtime.auto_run",
        max_concurrency=max_concurrency,
        queue_size=queue_size,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=timeout_seconds,
        task=dag_task,
        stop_callback=scheduler.request_stop,
    )
    asyncio.create_task(_watch_dag_run(query.analysis_id, dag_task))
    # scheduler.run()
    
    return {
        "message": "Auto-run started",
    }


@analysis_runtime_api.get("/running-dags")
async def get_running_dags():
    items = await running_dag_registry.list_running()
    for item in items:
        with get_engine().begin() as conn:
            item["snapshot"] = analysis_runtime_engine_service.get_runtime_snapshot(
                conn,
                analysis_id=item["analysis_id"],
            )
    return {
        "total": len(items),
        "items": items,
    }


@analysis_runtime_api.get("/running-dags/{analysis_id}")
async def get_running_dag(analysis_id: str):
    running_item = await running_dag_registry.get_running(analysis_id)
    if running_item:
        with get_engine().begin() as conn:
            running_item["snapshot"] = analysis_runtime_engine_service.get_runtime_snapshot(
                conn,
                analysis_id=analysis_id,
            )
        return {
            "state": "running",
            "item": running_item,
        }

    recent_item = await running_dag_registry.get_recent(analysis_id)
    if recent_item:
        return {
            "state": "finished",
            "item": recent_item,
        }

    raise HTTPException(status_code=404, detail=f"No DAG run found for analysis_id={analysis_id}")

# /analysis-runtime/running-dags/c139499a-84b4-42ab-bdea-85a7b6ce9bd8/stop
@analysis_runtime_api.post("/running-dags/{analysis_id}/stop")
@inject
async def stop_running_dag(
    analysis_id: str,
    evenet_bus: EventBus = Depends(Provide[AppContainer.event_bus]),
):
    await analysis_service.finished_analysis(analysis_id, "job", "stopping")

    stop_result = await running_dag_registry.stop_running(
        analysis_id,
        wait_for_completion=False,
        cancel_on_timeout=False,
    )
    if not stop_result.get("found"):
        raise HTTPException(status_code=404, detail=f"No running DAG found for analysis_id={analysis_id}")
    asyncio.create_task(
        _stop_running_dag_background(analysis_id, evenet_bus),
        name=f"dag-stop-{analysis_id}",
    )

    return {
        "message": "DAG stop requested",
        "analysis_status": "stopping",
        "request_stop_result": stop_result,
    }





# 取消缓存
@analysis_runtime_api.post("/invalidate-cache/{analysis_id}")
async def invalidate_cache(analysis_id: str):
    with get_engine().begin() as conn:
        analysis_node_service.invalidate_cache(conn, analysis_id)
    return {"message": f"Cache invalidated for node {analysis_id}"}
   