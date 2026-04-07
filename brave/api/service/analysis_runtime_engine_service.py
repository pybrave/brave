from __future__ import annotations

import asyncio
from datetime import datetime
import random
from pathlib import Path
from typing import Any, Dict, Optional

from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from brave.api.service import analysis_edge_service, analysis_node_service


TERMINAL_STATUS = {"done", "failed", "cached", "skipped"}
SUCCESS_STATUS = {"done", "cached"}
SIMULATED_MIN_SLEEP_SECONDS = 0.5
SIMULATED_MAX_SLEEP_SECONDS = 2.0


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _render_pattern(pattern: str, node: Dict[str, Any]) -> str:
    sample_token = str(node.get("sample_id") or node.get("node_id") or "sample")
    return pattern.replace("{sample}", sample_token)


def _build_simulated_outputs(node: Dict[str, Any]) -> Dict[str, Any]:
    output_patterns = _as_dict(node.get("output_patterns"))
    outputs: Dict[str, Any] = {}

    for handle, cfg in output_patterns.items():
        if isinstance(cfg, dict):
            pattern = cfg.get("pattern")
            if isinstance(pattern, str) and pattern:
                outputs[handle] = _render_pattern(pattern, node)
                continue

        params = _as_dict(node.get("params"))
        if handle in params:
            outputs[handle] = params[handle]

    if not outputs:
        outputs = _as_dict(node.get("resolved_outputs"))

    return outputs


def _propagate_outputs(conn, analysis_id: str, source_node_id: str, outputs: Dict[str, Any]) -> None:
    edges = analysis_edge_service.find_by_analysis_id(conn, analysis_id)

    for edge in edges:
        if str(edge.get("source_node") or "") != source_node_id:
            continue

        source_handle = str(edge.get("source_handle") or "")
        target_handle = str(edge.get("target_handle") or "")
        target_node_id = str(edge.get("target_node") or "")

        if not source_handle or not target_handle or not target_node_id:
            continue

        if source_handle not in outputs:
            continue

        value = outputs[source_handle]
        target_node = analysis_node_service.find_node(conn, analysis_id, target_node_id)
        if not target_node:
            continue

        params = dict(_as_dict(target_node.get("params")))
        resolved_inputs = dict(_as_dict(target_node.get("resolved_inputs")))
        target_inputs_patterns = _as_dict(target_node.get("inputs_patterns"))
        target_input_cfg = _as_dict(target_inputs_patterns.get(target_handle))
        is_multiple = bool(target_input_cfg.get("multiple"))

        if is_multiple:
            current = params.get(target_handle)
            if not isinstance(current, list):
                current = [] if current is None else [current]
            current.append(value)
            params[target_handle] = current

            resolved_current = resolved_inputs.get(target_handle)
            if not isinstance(resolved_current, list):
                resolved_current = [] if resolved_current is None else [resolved_current]
            resolved_current.append(value)
            resolved_inputs[target_handle] = resolved_current
        else:
            params[target_handle] = value
            resolved_inputs[target_handle] = value

        analysis_node_service.update_node(
            conn,
            analysis_id=analysis_id,
            node_id=target_node_id,
            values={
                "params": params,
                "resolved_inputs": resolved_inputs,
            },
        )


def get_runtime_snapshot(conn, analysis_id: str) -> Dict[str, Any]:
    analysis_node_service.refresh_ready_status(conn, analysis_id)
    nodes = [dict(row) for row in analysis_node_service.find_by_analysis_id(conn, analysis_id)]
    ready_nodes = [n for n in nodes if str(n.get("status") or "") == "ready"]

    status_count: Dict[str, int] = {}
    for node in nodes:
        status = str(node.get("status") or "pending")
        status_count[status] = status_count.get(status, 0) + 1

    is_finished = all(str(node.get("status") or "pending") in TERMINAL_STATUS for node in nodes) if nodes else True

    return {
        "analysis_id": analysis_id,
        "total_nodes": len(nodes),
        "status_count": status_count,
        "ready_count": len(ready_nodes),
        "ready_nodes": ready_nodes,
        "is_finished": is_finished,
    }


def schedule_next(conn, analysis_id: str) -> Optional[Dict[str, Any]]:

    return analysis_node_service.claim_next_ready_node(conn, analysis_id)

def _build_workspace_dir(analysis_id: str, node_id: str) -> Path:
    settings = get_settings()
    return Path(settings.WORK_DIR) / "analysis-runtime" / analysis_id / node_id


async def run_simulated_executor(
    analysis_id: str,
    node_id: str,
    sleep_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    delay = float(
        sleep_seconds
        if sleep_seconds is not None
        else random.uniform(SIMULATED_MIN_SLEEP_SECONDS, SIMULATED_MAX_SLEEP_SECONDS)
    )
    workspace_dir = _build_workspace_dir(analysis_id=analysis_id, node_id=node_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    with get_engine().begin() as conn:
        analysis_node_service.update_node(
            conn,
            analysis_id=analysis_id,
            node_id=node_id,
            values={
                "workspace_dir": str(workspace_dir),
            },
        )

    await asyncio.sleep(max(delay, 0.0))

    try:
        with get_engine().begin() as conn:
            latest_node = analysis_node_service.find_node(conn, analysis_id, node_id)
            if not latest_node:
                return {
                    "analysis_id": analysis_id,
                    "node_id": node_id,
                    "status": "not_found",
                    "sleep_seconds": delay,
                    "workspace_dir": str(workspace_dir),
                }

            latest_status = str(latest_node.get("status") or "")
            if latest_status != "running":
                return {
                    "analysis_id": analysis_id,
                    "node_id": node_id,
                    "status": "ignored",
                    "node_status": latest_status,
                    "sleep_seconds": delay,
                    "workspace_dir": str(workspace_dir),
                }

            complete_result = complete_node(
                conn,
                analysis_id=analysis_id,
                node_id=node_id,
                status="done",
            )
            return {
                "analysis_id": analysis_id,
                "node_id": node_id,
                "status": "done",
                "sleep_seconds": delay,
                "workspace_dir": str(workspace_dir),
                "result": complete_result,
            }
    except Exception as exc:
        with get_engine().begin() as conn:
            latest_node = analysis_node_service.find_node(conn, analysis_id, node_id)
            if latest_node and str(latest_node.get("status") or "") == "running":
                complete_node(
                    conn,
                    analysis_id=analysis_id,
                    node_id=node_id,
                    status="failed",
                    exit_code=1,
                    error_message=str(exc),
                )
        return {
            "analysis_id": analysis_id,
            "node_id": node_id,
            "status": "failed",
            "sleep_seconds": delay,
            "workspace_dir": str(workspace_dir),
            "error": str(exc),
        }


def complete_node(
    conn,
    analysis_id: str,
    node_id: str,
    status: str = "done",
    resolved_outputs: Optional[Dict[str, Any]] = None,
    exit_code: Optional[int] = 0,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
    node = analysis_node_service.find_node(conn, analysis_id, node_id)
    if not node:
        raise ValueError(f"node not found: analysis_id={analysis_id}, node_id={node_id}")

    current_retry = int(node.get("retry") or 0)
    max_retry = int(node.get("max_retry") or 0)

    if status in SUCCESS_STATUS:
        final_outputs = resolved_outputs or _build_simulated_outputs(node)
        analysis_node_service.update_node(
            conn,
            analysis_id=analysis_id,
            node_id=node_id,
            values={
                "status": status,
                "resolved_outputs": final_outputs,
                "exit_code": exit_code,
                "error_message": None,
                "finished_at": datetime.now(),
            },
        )
        _propagate_outputs(conn, analysis_id=analysis_id, source_node_id=node_id, outputs=final_outputs)
    elif status == "failed":
        should_retry = current_retry < max_retry
        if should_retry:
            analysis_node_service.update_node(
                conn,
                analysis_id=analysis_id,
                node_id=node_id,
                values={
                    "status": "pending",
                    "retry": current_retry + 1,
                    "exit_code": exit_code,
                    "error_message": error_message,
                },
            )
        else:
            analysis_node_service.update_node(
                conn,
                analysis_id=analysis_id,
                node_id=node_id,
                values={
                    "status": "failed",
                    "exit_code": exit_code,
                    "error_message": error_message,
                    "finished_at": datetime.now(),
                },
            )
    else:
        analysis_node_service.update_node(
            conn,
            analysis_id=analysis_id,
            node_id=node_id,
            values={
                "status": status,
                "exit_code": exit_code,
                "error_message": error_message,
                "finished_at": datetime.now() if status in TERMINAL_STATUS else None,
            },
        )

    analysis_node_service.refresh_ready_status(conn, analysis_id)

    return {
        "node": analysis_node_service.find_node(conn, analysis_id, node_id),
        "ready_nodes": [
            n
            for n in [dict(row) for row in analysis_node_service.find_by_analysis_id(conn, analysis_id)]
            if str(n.get("status") or "") == "ready"
        ],
        "snapshot": get_runtime_snapshot(conn, analysis_id),
    }


def auto_run(conn, analysis_id: str, max_steps: int = 10000) -> Dict[str, Any]:
    analysis_node_service.refresh_ready_status(conn, analysis_id)
    executed = []
    for _ in range(max_steps):
        node = schedule_next(conn, analysis_id)
        if not node:
            break

        node_id = str(node.get("node_id") or "")
        result = complete_node(conn, analysis_id=analysis_id, node_id=node_id, status="done")
        executed.append(result["node"])

    snapshot = get_runtime_snapshot(conn, analysis_id)
    return {
        "analysis_id": analysis_id,
        "executed_count": len(executed),
        "executed_nodes": executed,
        "snapshot": snapshot,
    }
