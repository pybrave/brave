from __future__ import annotations

import asyncio
from datetime import datetime
import glob
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from brave.api.config.config import get_settings
from brave.api.config.db import get_engine
from brave.api.service import analysis_edge_service, analysis_node_service


# Runtime 状态约定：
# - TERMINAL_STATUS: 节点进入这些状态后，调度器视为“已结束”
# - SUCCESS_STATUS: 会触发输出传播到下游输入

TERMINAL_STATUS = {"done", "failed", "cached", "skipped"}
SUCCESS_STATUS = {"done", "cached"}
SIMULATED_MIN_SLEEP_SECONDS = 0.5
SIMULATED_MAX_SLEEP_SECONDS = 2.0


def _as_dict(value: Any) -> Dict[str, Any]:
    """保证返回 dict，避免 JSON 字段为空或类型异常时出现 KeyError。"""
    if isinstance(value, dict):
        return value
    return {}


def _render_pattern(pattern: str, node: Dict[str, Any]) -> str:
    """将输出 pattern 中的 {sample} 替换为节点样本标识。"""
    sample_token = str(node.get("sample_id") or node.get("node_id") or "sample")
    return pattern.replace("{sample}", sample_token)


def _build_simulated_outputs(node: Dict[str, Any]) -> Dict[str, Any]:
    """为模拟执行生成输出。

    优先级：
    1) output_patterns 中声明的 pattern
    2) params 中同名 handle 的值
    3) 已存在的 resolved_outputs（兜底）
    """
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


def _resolve_node_output_dir(node: Dict[str, Any]) -> Optional[Path]:
    """返回节点输出目录（优先 output_dir，回退 workspace_dir/output）。"""
    output_dir = str(node.get("output_dir") or "").strip()
    if output_dir:
        return Path(output_dir)

    workspace_dir = str(node.get("workspace_dir") or "").strip()
    if workspace_dir:
        return Path(workspace_dir) / "output"

    return None


def _glob_files(output_dir: Path, pattern: str) -> List[str]:
    """在 output_dir 下按 pattern 匹配真实文件，支持通配符。"""
    pattern_path = Path(pattern)
    if pattern_path.is_absolute():
        search_pattern = pattern
    else:
        search_pattern = str(output_dir / pattern)

    matches = []
    for item in glob.glob(search_pattern):
        p = Path(item)
        if p.exists() and p.is_file():
            matches.append(str(p.resolve()))
    return sorted(list(dict.fromkeys(matches)))


def _resolve_verified_outputs(
    node: Dict[str, Any],
    candidate_outputs: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """根据 output_patterns 校验真实输出文件，仅返回已落盘的输出值。"""
    output_patterns = _as_dict(node.get("output_patterns"))
    output_dir = _resolve_node_output_dir(node)
    verified: Dict[str, Any] = {}
    errors: List[str] = []

    for handle, cfg in output_patterns.items():
        if not isinstance(cfg, dict):
            if handle in candidate_outputs:
                verified[handle] = candidate_outputs[handle]
            continue

        out_type = str(cfg.get("type") or "").strip().lower()
        pattern = cfg.get("pattern")
        multiple = bool(cfg.get("multiple"))
        required = bool(cfg.get("required", True))

        if out_type != "file":
            if handle in candidate_outputs:
                verified[handle] = candidate_outputs[handle]
            continue

        if not isinstance(pattern, str) or not pattern.strip():
            if handle in candidate_outputs:
                verified[handle] = candidate_outputs[handle]
            elif required:
                errors.append(f"missing output pattern: {handle}")
            continue

        rendered_pattern = _render_pattern(pattern.strip(), node)
        if output_dir is None:
            errors.append(f"missing output_dir for handle: {handle}")
            continue

        if not output_dir.exists():
            errors.append(f"output_dir not found: {output_dir}")
            continue

        matches = _glob_files(output_dir, rendered_pattern)
        if not matches:
            if required:
                errors.append(f"missing output file: {handle} pattern={rendered_pattern}")
            continue

        if multiple:
            verified[handle] = matches
        else:
            verified[handle] = matches[0]

    # 保留未声明在 output_patterns 的回传值（例如脚本主动上报的指标）。
    for handle, value in candidate_outputs.items():
        if handle not in verified and handle not in output_patterns:
            verified[handle] = value

    return verified, errors


def _propagate_outputs(conn, analysis_id: str, source_node_id: str, outputs: Dict[str, Any]) -> None:
    """将上游节点输出按边映射写入下游节点的 params/resolved_inputs。"""
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
        current = params.get(target_handle)
        resolved_current = resolved_inputs.get(target_handle)

        # 若目标侧当前值已经是 list（例如 gather 聚合输入），持续追加。
        should_append_list = is_multiple or isinstance(current, list) or isinstance(resolved_current, list)

        if should_append_list:
            # multiple=true 时，下游输入聚合为列表。
            if not isinstance(current, list):
                current = [] if current is None else [current]
            current.append(value)
            params[target_handle] = current

            if not isinstance(resolved_current, list):
                resolved_current = [] if resolved_current is None else [resolved_current]
            resolved_current.append(value)
            resolved_inputs[target_handle] = resolved_current
        else:
            # 非 multiple 输入：覆盖同名 handle。
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
    """返回运行时快照：节点状态分布、ready 列表和流程是否结束。"""
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
    """领取一个可执行节点（ready -> running）。"""

    return analysis_node_service.claim_next_ready_node(conn, analysis_id)

def _build_workspace_dir(project_id: str, analysis_id: str, node_id: str) -> Path:
    """构造模拟执行工作目录。"""
    settings = get_settings()
    return Path(settings.ANALYSIS_DIR) / project_id / analysis_id / node_id


async def  run_simulated_executor(
    analysis_node_id: str,
    sleep_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    """模拟节点执行。

    行为：
    1) 创建工作目录并写回 workspace_dir
    2) 随机 sleep（模拟执行耗时）
    3) 若节点仍处于 running，则自动 complete 为 done
    4) 执行异常时，自动标记 failed
    """
    delay = float(
        sleep_seconds
        if sleep_seconds is not None
        else random.uniform(SIMULATED_MIN_SLEEP_SECONDS, SIMULATED_MAX_SLEEP_SECONDS)
    )
    with get_engine().begin() as conn:
        analsyis_node = analysis_node_service.find_by_analysis_node_id(conn, analysis_node_id)
    workspace_dir = Path(analsyis_node["workspace_dir"]) #_build_workspace_dir(project_id=project_id, analysis_id=analysis_id, node_id=node_id)
    output_dir = workspace_dir / "output"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_id = str(analsyis_node.get("analysis_id") or "")
    node_id = str(analsyis_node.get("node_id") or "")

    # with get_engine().begin() as conn:
    #     analysis_node_service.update_node(
    #         conn,
    #         analysis_id=analysis_id,
    #         node_id=node_id,
    #         values={
    #             "workspace_dir": str(workspace_dir),
    #             "output_dir": str(output_dir),
    #         },
    #     )

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
                # 避免重复完成：如果节点已被外部上报成 done/failed，则忽略本次模拟回写。
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
        # 保底失败回写：若异常发生且节点仍在 running，则转 failed 防止卡死。
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
    
async def complete_node_conn(analysis_node_id, status):
    with get_engine().begin() as conn:  
        analysis_node = analysis_node_service.find_by_analysis_node_id(conn, analysis_node_id)
        analysis_id = str(analysis_node.get("analysis_id") or "")
        node_id = str(analysis_node.get("node_id") or "")
        complete_node(conn,analysis_id=analysis_id,node_id=node_id,status=status)


def complete_node(
    conn,
    analysis_id: str,
    node_id: str,
    status: str = "done",
    resolved_outputs: Optional[Dict[str, Any]] = None,
    exit_code: Optional[int] = 0,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
    """节点完结入口。

    - done/cached: 写输出并传播到下游
    - failed: 按 retry/max_retry 自动回退到 pending 或最终 failed
    - 其他状态：直接写状态
    """
    node = analysis_node_service.find_node(conn, analysis_id, node_id)
    if not node:
        raise ValueError(f"node not found: analysis_id={analysis_id}, node_id={node_id}")

    current_retry = int(node.get("retry") or 0)
    max_retry = int(node.get("max_retry") or 0)
    force_terminal_failed = False
    output_errors: List[str] = []
    if status =="failed":
        error_message = error_message or "node execution failed"

    if status in SUCCESS_STATUS:
        candidate_outputs = resolved_outputs or _build_simulated_outputs(node)
        final_outputs, output_errors = _resolve_verified_outputs(node, _as_dict(candidate_outputs))

        if output_errors:
            # 仅当真实文件存在时才允许 done/cached；否则按失败处理。
            status = "failed"
            force_terminal_failed = True
            if exit_code in (None, 0):
                exit_code = 1
            # merged_error = "; ".join(output_errors)
            # error_message = f"output validation failed: {merged_error}"
        else:
            analysis_node_service.update_node(
                conn,
                analysis_id=analysis_id,
                node_id=node_id,
                values={
                    "status": status,
                    "resolved_outputs": final_outputs,
                    "output_validation_errors": [],
                    "exit_code": exit_code,
                    "error_message": None,
                    "finished_at": datetime.now(),
                },
            )
            _propagate_outputs(conn, analysis_id=analysis_id, source_node_id=node_id, outputs=final_outputs)
    if status == "failed":
        # 失败自动重试：未超限则重置为 pending，等待再次调度。
        should_retry = (not force_terminal_failed) and current_retry < max_retry
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
                    "output_validation_errors": output_errors if force_terminal_failed else [],
                    "finished_at": datetime.now(),
                },
            )
    elif status not in SUCCESS_STATUS:
        analysis_node_service.update_node(
            conn,
            analysis_id=analysis_id,
            node_id=node_id,
            values={
                "status": status,
                "exit_code": exit_code,
                "error_message": None,
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
    """同步自动跑完整个 DAG（测试/调试用途，不模拟耗时）。"""
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
