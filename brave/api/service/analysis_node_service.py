from brave.api.models.core import analysis_nodes
from brave.api.schemas.analysis_task import PageAnalysisNodeQuery
from sqlalchemy import and_, desc, select, or_, func
from collections import defaultdict
from datetime import datetime
import uuid


def _as_dict(value):
    if isinstance(value, dict):
        return value
    return {}


def _is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _schema_type(schema: dict) -> str:
    return str(schema.get("type") or "").strip().lower()


def _required_property_names(schema: dict) -> list[str]:
    return [
        str(name)
        for name, cfg in _as_dict(schema.get("properties")).items()
        if bool(_as_dict(cfg).get("required"))
    ]


def _collect_required_errors_for_value(input_key: str, cfg_dict: dict, value):
    errors: list[str] = []
    schema_type = _schema_type(cfg_dict)

    if schema_type == "object":
        for prop in _required_property_names(cfg_dict):
            if not isinstance(value, dict) or value.get(prop) is None:
                errors.append(f"missing required input: {input_key}.{prop}")
        return errors

    if schema_type == "list":
        item_schema = _as_dict(cfg_dict.get("items"))
        if _schema_type(item_schema) == "object":
            for prop in _required_property_names(item_schema):
                if not isinstance(value, dict) or value.get(prop) is None:
                    errors.append(f"missing required input: {input_key}.{prop}")
        return errors

    return errors


def _inputs_satisfied(node: dict) -> bool:
    return len(_input_validation_errors(node)) == 0


def _input_validation_errors(node: dict) -> list[str]:
    inputs_patterns = _as_dict(node.get("inputs_patterns"))
    if not inputs_patterns:
        return []

    params = _as_dict(node.get("params"))
    resolved_inputs = _as_dict(node.get("resolved_inputs"))
    # Recompute validation errors from current inputs every time.
    # Reusing stored errors can keep stale messages (for example, old upstream-not-finished errors).
    errors: list[str] = []

    for input_key, cfg in inputs_patterns.items():
        cfg_dict = _as_dict(cfg)
        required = bool(cfg_dict.get("required"))
        multiple = bool(cfg_dict.get("multiple"))

        key_in_params = input_key in params
        key_in_resolved = input_key in resolved_inputs

        if required and not (key_in_params or key_in_resolved):
            errors.append(f"missing required input key: {input_key}")
            continue

        value = resolved_inputs.get(input_key) if key_in_resolved else params.get(input_key)
        if required and _is_empty(value):
            errors.append(f"required input is empty: {input_key}")

        if multiple and value is not None and not isinstance(value, list):
            errors.append(f"input expects list (multiple=true): {input_key}")

        errors.extend(_collect_required_errors_for_value(input_key, cfg_dict, value))

    deduped: list[str] = []
    seen = set()
    for err in errors:
        if err in seen:
            continue
        seen.add(err)
        deduped.append(err)
    return deduped


def delete_by_analysis_id(conn, analysis_id: str):
    stmt = analysis_nodes.delete().where(analysis_nodes.c.analysis_id == analysis_id)
    conn.execute(stmt)


def create_many(conn, rows: list[dict]):
    if not rows:
        return

    normalized_rows = []
    for row in rows:
        normalized_rows.append(
            {
                "analysis_node_id": row.get("analysis_node_id") or str(uuid.uuid4()),
                "analysis_id": row.get("analysis_id"),
                "node_id": row.get("node_id"),
                "sample_id": row.get("sample_id"),
                "script_id": row.get("script_id"),
                "inputs_patterns": row.get("inputs_patterns"),
                "resolved_inputs": row.get("resolved_inputs"),
                "output_patterns": row.get("output_patterns"),
                "resolved_outputs": row.get("resolved_outputs"),
                "params": row.get("params"),
                "cpu": row.get("cpu"),
                "memory": row.get("memory"),
                "disk": row.get("disk"),
                "gpu": row.get("gpu"),
                "status": row.get("status") or "pending",
                "pid": row.get("pid"),
                "job_id": row.get("job_id"),
                "executor": row.get("executor"),
                "retry": row.get("retry", 0),
                "max_retry": row.get("max_retry", 3),
                "exit_code": row.get("exit_code"),
                "error_message": row.get("error_message"),
                "input_hash": row.get("input_hash"),
                "cache_hit": row.get("cache_hit", False),
                "upstream_ids": row.get("upstream_ids") or [],
                "downstream_ids": row.get("downstream_ids") or [],
                "input_validation_errors": row.get("input_validation_errors") or [],
                "log_path": row.get("log_path"),
                "workspace_dir": row.get("workspace_dir"),
                "started_at": row.get("started_at"),
                "finished_at": row.get("finished_at"),
            }
        )

    stmt = analysis_nodes.insert()
    conn.execute(stmt, normalized_rows)


def replace_by_analysis_id(conn, analysis_id: str, rows: list[dict]):
    delete_by_analysis_id(conn, analysis_id)
    create_many(conn, rows)


def find_by_analysis_id(conn, analysis_id: str):
    stmt = analysis_nodes.select().where(analysis_nodes.c.analysis_id == analysis_id)
    return conn.execute(stmt).mappings().all()


def find_node(conn, analysis_id: str, node_id: str):
    stmt = analysis_nodes.select().where(
        and_(
            analysis_nodes.c.analysis_id == analysis_id,
            analysis_nodes.c.node_id == node_id,
        )
    )
    return conn.execute(stmt).mappings().first()


def update_node(conn, analysis_id: str, node_id: str, values: dict):
    if not values:
        return 0

    payload = dict(values)
    payload["updated_at"] = datetime.now()

    stmt = (
        analysis_nodes.update()
        .where(
            and_(
                analysis_nodes.c.analysis_id == analysis_id,
                analysis_nodes.c.node_id == node_id,
            )
        )
        .values(**payload)
    )
    result = conn.execute(stmt)
    return result.rowcount


def list_ready_nodes(conn, analysis_id: str, limit: int = 100):
    from brave.api.service import analysis_edge_service

    nodes = [dict(n) for n in find_by_analysis_id(conn, analysis_id)]
    edges = analysis_edge_service.find_by_analysis_id(conn, analysis_id)
    node_map = {str(n.get("node_id")): n for n in nodes}

    incoming = defaultdict(list)
    for edge in edges:
        source_node = str(edge.get("source_node") or "")
        target_node = str(edge.get("target_node") or "")
        if source_node and target_node:
            incoming[target_node].append(source_node)

    ready = []
    for node in nodes:
        node_id = str(node.get("node_id") or "")
        status = str(node.get("status") or "pending")
        if status not in {"pending", "ready"}:
            continue

        parents = incoming.get(node_id, [])
        parent_done = True
        for parent_id in parents:
            parent = node_map.get(parent_id)
            parent_status = str((parent or {}).get("status") or "pending")
            if parent_status not in {"done", "cached"}:
                parent_done = False
                break

        if parent_done and _inputs_satisfied(node):
            ready.append(node)

    ready.sort(key=lambda x: (str(x.get("created_at") or ""), str(x.get("node_id") or "")))
    return ready[: max(limit, 1)]


def refresh_ready_status(conn, analysis_id: str):
    nodes = [dict(n) for n in find_by_analysis_id(conn, analysis_id)]
    node_map = {str(n.get("node_id") or ""): n for n in nodes}

    from brave.api.service import analysis_edge_service
    edges = analysis_edge_service.find_by_analysis_id(conn, analysis_id)

    incoming = defaultdict(list)
    for edge in edges:
        source_node = str(edge.get("source_node") or "")
        target_node = str(edge.get("target_node") or "")
        if source_node and target_node:
            incoming[target_node].append(source_node)

    now = datetime.now()
    for node in nodes:
        node_id = str(node.get("node_id") or "")
        status = str(node.get("status") or "pending")
        if status in {"running", "done", "failed", "cached", "skipped"}:
            continue

        errors = _input_validation_errors(node)
        parents = incoming.get(node_id, [])
        for parent_id in parents:
            parent = node_map.get(parent_id)
            parent_status = str((parent or {}).get("status") or "pending")
            if parent_status not in {"done", "cached"}:
                errors.append(f"upstream not finished: {parent_id}")

        target_status = "ready" if not errors else "pending"
        update_payload = {
            "status": target_status,
            "input_validation_errors": errors,
            "updated_at": now,
        }
        conn.execute(
            analysis_nodes.update()
            .where(
                and_(
                    analysis_nodes.c.analysis_id == analysis_id,
                    analysis_nodes.c.node_id == node_id,
                )
            )
            .values(**update_payload)
        )

    return [dict(n) for n in find_by_analysis_id(conn, analysis_id)]


def claim_next_ready_node(conn, analysis_id: str):
    refresh_ready_status(conn, analysis_id=analysis_id)

    stmt = (
        analysis_nodes.select()
        .where(
            and_(
                analysis_nodes.c.analysis_id == analysis_id,
                analysis_nodes.c.status == "ready",
            )
        )
        .order_by(analysis_nodes.c.created_at.asc(), analysis_nodes.c.node_id.asc())
        .limit(1)
    )
    row = conn.execute(stmt).mappings().first()
    ready_nodes = [row] if row else []
    if not ready_nodes:
        return None

    node = ready_nodes[0]
    node_id = str(node.get("node_id") or "")
    updated = update_node(
        conn,
        analysis_id=analysis_id,
        node_id=node_id,
        values={
            "status": "running",
            "started_at": node.get("started_at") or datetime.now(),
            "error_message": None,
        },
    )
    if not updated:
        return None

    return find_node(conn, analysis_id=analysis_id, node_id=node_id)


def page_analysis_nodes(conn, query: PageAnalysisNodeQuery):
    if not query.page_number or query.page_number < 1:
        query.page_number = 1

    stmt = select(analysis_nodes)
    conditions = []

    if query.analysis_id:
        conditions.append(analysis_nodes.c.analysis_id == query.analysis_id)

    if query.keywords:
        like_keywords = f"%{query.keywords}%"
        conditions.append(
            or_(
                analysis_nodes.c.node_id.like(like_keywords),
                analysis_nodes.c.script_id.like(like_keywords),
            )
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    total = conn.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    stmt = stmt.order_by(desc(analysis_nodes.c.created_at)).offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    result = conn.execute(stmt).mappings().all()

    return {
        "items": [dict(row) for row in result],
        "total": total,
        "page_number": query.page_number,
        "page_size": query.page_size,
    }
