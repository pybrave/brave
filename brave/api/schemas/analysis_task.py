
from pydantic import BaseModel
from typing import Optional, Any

class AnalysisTask(BaseModel):
    task_id: Optional[str]
    analysis_id: Optional[str]
    task_name: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class PageAnalysisTaskQuery(BaseModel):
    analysis_id: Optional[str]
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    keywords: Optional[str]=None


class PageAnalysisNodeQuery(BaseModel):
    analysis_id: Optional[str]
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    keywords: Optional[str]=None


class PageAnalysisEdgeQuery(BaseModel):
    analysis_id: Optional[str]
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    keywords: Optional[str]=None


class RuntimeScheduleQuery(BaseModel):
    analysis_id: str
    


class RuntimeNodeReport(BaseModel):
    analysis_id: str
    node_id: str
    status: str = "done"
    resolved_outputs: Optional[dict[str, Any]] = None
    exit_code: Optional[int] = 0
    error_message: Optional[str] = None


class RuntimeAutoRunQuery(BaseModel):
    analysis_id: str
    max_steps: Optional[int] = 10000
