
from litellm import uuid

import uuid

from brave.api.schemas.analysis_task import AnalysisTask
from brave.api.models.core import analyis_task
def create_or_update_analysis_task(conn,analysis_task: AnalysisTask):
    analysis_task_dict = analysis_task.dict()
    if analysis_task["task_id"]:
        # Update existing record
        stmt = analyis_task.update().where(analyis_task.c.task_id == analysis_task["task_id"]).values(**analysis_task_dict)
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

def task_generation(conn, analysis_id,params, dag_definition):
    find_analysis_task = find_analysis_tasks_by_analysis_id(conn, analysis_id)
    analysis_task_map = {item["task_id"]:item for item in find_analysis_task}
    pass