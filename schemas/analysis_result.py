from typing import Optional
from pydantic import BaseModel

class AnalysisResultQuery(BaseModel):
    # id: Optional[int]
    analysis_method: list
    project:str
    querySample:Optional[bool]=True

class AnalysisResult(BaseModel):
    id: Optional[int]
    sample_name: Optional[str]
    sample_key: Optional[str]
    analysis_name: Optional[str]
    analysis_key: Optional[str]
    analysis_method: Optional[str]
    software: Optional[str]
    content: Optional[str]
    analysis_version: Optional[str]
    content_type: Optional[str]
    project: Optional[str]
    request_param: Optional[str]
    analysis_id: Optional[int]
    sample_group: Optional[str]
    