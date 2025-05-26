from typing import Optional
from pydantic import BaseModel

class AnalysisResultQuery(BaseModel):
    # id: Optional[int]
    analysis_method: list
    project:str