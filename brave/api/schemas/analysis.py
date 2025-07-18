from typing import Optional
from pydantic import BaseModel

class AnalysisInput(BaseModel):
    id: Optional[int]= None
    project: Optional[str]
    samples: list
    analysis_method:str
    analysis_name:str
    
    # analysis_name: Optional[str]
    # work_dir: Optional[str]
    # output_dir: Optional[str]
class QueryAnalysis(BaseModel):
    analysis_id: Optional[str]=None
    analysis_method: Optional[str]=None
    component_id: Optional[str]=None
    project: Optional[str]=None

class Analysis(BaseModel):
    id: Optional[int]
    project: Optional[str]
    analysis_id: Optional[str]
    component_id: Optional[str]
    analysis_method: Optional[str]
    analysis_name: Optional[str]
    input_file: Optional[str]
    request_param: Optional[str]
    work_dir: Optional[str]
    output_dir: Optional[str]
    params_path: Optional[str]
    output_format: Optional[str]
    command_path: Optional[str]
    pipeline_script: Optional[str]
    parse_analysis_module: Optional[str]
    process_id: Optional[str]
    analysis_status: Optional[str]