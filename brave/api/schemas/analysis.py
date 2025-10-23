from typing import Optional,Any
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
    component_ids: Optional[list[str]] =None
    is_report: Optional[bool] =None
    project: Optional[str]=None
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    keywords: Optional[str]=None

class Analysis(BaseModel):
    id: Optional[int]
    project: Optional[str]
    analysis_id:str
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
    # analysis_status: Optional[str]


class AnalysisExecuterModal(BaseModel):
    id: Optional[int]=None
    project: Optional[str]=None
    analysis_id: str
    run_id:str
    component_id: Optional[str]=None
    analysis_method: Optional[str]=None
    analysis_name: Optional[str]=None
    input_file: Optional[str]=None
    request_param: Optional[str]=None
    work_dir: Optional[str]=None
    output_dir: Optional[str]=None
    params_path: Optional[str]=None
    output_format: Optional[str]=None
    command_path: Optional[str]=None
    pipeline_script: Optional[str]=None
    parse_analysis_module: Optional[str]=None
    process_id: Optional[str]=None
    analysis_status: Optional[str]=None
    command_log_path: Optional[str]=None
    run_type:Optional[str]=None
    image: Optional[str]=None
    container_id: Optional[str]=None
    # change_uid: Optional[str]=None
    ports: Optional[Any]=None

class AnalysisId(BaseModel):
    run_id: str
    run_type:Optional[str]=None


class UpdateProject(BaseModel):
    project: Optional[list[str]] = None
    analysis_id: Optional[str]=None
