
import uuid

from brave.api.schemas.analysis_task import AnalysisTask, PageAnalysisTaskQuery
from brave.api.models.core import analyis_task
from brave.api.dag.dag import build_runtime_tasks
from brave.api.service import analysis_node_service, analysis_edge_service
from sqlalchemy import and_, desc, select,case,or_,func


def create_or_update_analysis_task(conn,analysis_task: AnalysisTask):
    if isinstance(analysis_task, AnalysisTask):
        analysis_task_dict = analysis_task.dict()
    else:
        analysis_task_dict = dict(analysis_task)

    if analysis_task_dict.get("task_id"):
        # Update existing record
        stmt = analyis_task.update().where(analyis_task.c.task_id == analysis_task_dict["task_id"]).values(**analysis_task_dict)
    else:
        # Insert new record
        str_uuid = str(uuid.uuid4())
        analysis_task_dict["task_id"] = str_uuid

        stmt = analyis_task.insert().values(**analysis_task_dict)
    conn.execute(stmt)

    return {
        "task_id": analysis_task_dict["task_id"]
    }

def delete_analysis_task(conn, task_id: str):
    stmt = analyis_task.delete().where(analyis_task.c.task_id == task_id)
    conn.execute(stmt)


def find_analysis_task_by_id(conn, task_id: str):
    stmt = analyis_task.select().where(analyis_task.c.task_id == task_id)
    result = conn.execute(stmt).mappings().first()

    return result

def find_analysis_tasks_by_analysis_id(conn, analysis_id: str):
    stmt = analyis_task.select().where(analyis_task.c.analysis_id == analysis_id)
    result = conn.execute(stmt).mappings().all()

    return result

def page_analysis_tasks(conn, query:PageAnalysisTaskQuery):
    if not query.page_number or query.page_number < 1:
        query.page_number = 1
    stmt = select(analyis_task)
    conditions = []
    if query.analysis_id:
        conditions.append(analyis_task.c.analysis_id == query.analysis_id)
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    total = conn.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    stmt = stmt.order_by(desc(analyis_task.c.created_at)).offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    result = conn.execute(stmt).mappings().all()
    result_dict = [dict(row) for row in result]

    return {
        "items": result_dict,
        "total": total,
        "page_number": query.page_number,
        "page_size": query.page_size
    }



