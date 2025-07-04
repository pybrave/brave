from typing import Optional
from pydantic import BaseModel

class AnalysisResultQuery(BaseModel):
    # id: Optional[int]
    analysis_method:Optional[list]=None
    component_ids:Optional[list]=None
    project:Optional[str]=None
    querySample:Optional[bool]=True
    analysis_type:Optional[str]=None
    ids:Optional[list]=None
    

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
    analysis_id: Optional[str]
    sample_group: Optional[str]
    sample_group_name: Optional[str]
    analysis_type: Optional[str]
    create_date: Optional[str]
    sample_source: Optional[str]
    host_disease: Optional[str]
    component_id: Optional[str]
    

class ParseImportData(BaseModel):
    content: str
    
    # suffix: str
    
# stmt =  select(analysis_result, samples).select_from(analysis_result.outerjoin(samples,samples.c.sample_key==analysis_result.c.analysis_key))

class ImportData(BaseModel):
    component_id:str
    project: str
    content: str
    analysis_key: str
    # content_type:Optional[str]="json"
    # analysis_type:Optional[str]="import_data"
