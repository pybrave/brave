
from fastapi import APIRouter

from brave.api.config.db import get_engine
from brave.api.schemas.analysis_task import PageAnalysisTaskQuery
from brave.api.service import analysis_task_service


analysis_task_api = APIRouter(prefix="/analysis-tasks")

@analysis_task_api.post("/page")
async def page_analysis_tasks(query:PageAnalysisTaskQuery):
    with get_engine().begin() as conn: 
        return analysis_task_service.page_analysis_tasks(conn, query)