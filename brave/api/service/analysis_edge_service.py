from brave.api.models.core import analysis_edges
from brave.api.schemas.analysis_task import PageAnalysisEdgeQuery
from sqlalchemy import and_, desc, select, or_, func
import uuid


def delete_by_analysis_id(conn, analysis_id: str):
    stmt = analysis_edges.delete().where(analysis_edges.c.analysis_id == analysis_id)
    conn.execute(stmt)


def create_many(conn, rows: list[dict]):
    if not rows:
        return

    normalized_rows = []
    for row in rows:
        normalized_rows.append(
            {
                "analysis_edge_id": row.get("analysis_edge_id") or str(uuid.uuid4()),
                "analysis_id": row.get("analysis_id"),
                "source_node": row.get("source_node"),
                "target_node": row.get("target_node"),
                "source_handle": row.get("source_handle", row.get("sourceHandle")),
                "target_handle": row.get("target_handle", row.get("targetHandle")),
            }
        )

    stmt = analysis_edges.insert()
    conn.execute(stmt, normalized_rows)


def replace_by_analysis_id(conn, analysis_id: str, rows: list[dict]):
    delete_by_analysis_id(conn, analysis_id)
    create_many(conn, rows)


def find_by_analysis_id(conn, analysis_id: str):
    stmt = analysis_edges.select().where(analysis_edges.c.analysis_id == analysis_id)
    return conn.execute(stmt).mappings().all()


def page_analysis_edges(conn, query: PageAnalysisEdgeQuery):
    if not query.page_number or query.page_number < 1:
        query.page_number = 1

    stmt = select(analysis_edges)
    conditions = []

    if query.analysis_id:
        conditions.append(analysis_edges.c.analysis_id == query.analysis_id)

    if query.keywords:
        like_keywords = f"%{query.keywords}%"
        conditions.append(
            or_(
                analysis_edges.c.source_node.like(like_keywords),
                analysis_edges.c.target_node.like(like_keywords),
                analysis_edges.c.source_handle.like(like_keywords),
                analysis_edges.c.target_handle.like(like_keywords),
            )
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    total = conn.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    stmt = stmt.order_by(desc(analysis_edges.c.created_at)).offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    result = conn.execute(stmt).mappings().all()

    return {
        "items": [dict(row) for row in result],
        "total": total,
        "page_number": query.page_number,
        "page_size": query.page_size,
    }
