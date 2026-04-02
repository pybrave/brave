
from pydantic import BaseModel
from typing import Optional

class AnalysisTask(BaseModel):
    task_id: Optional[str]
    analysis_id: Optional[str]
    task_name: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
