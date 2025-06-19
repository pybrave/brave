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

class Analysis(BaseModel):
    id: Optional[int]
    project: Optional[str]
    analysis_key: Optional[str]
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