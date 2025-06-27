from typing import Optional
from pydantic import BaseModel

class SavePipeline(BaseModel):
    pipeline_id: Optional[str]=None
    parent_pipeline_id:Optional[str]=None
    pipeline_key: Optional[str]=None
    pipeline_order: Optional[int]=None
    pipeline_type: Optional[str]
    content: Optional[str]=None

class QueryPipeline(BaseModel):
    pipeline_id: Optional[str]=None
    parent_pipeline_id:Optional[str]=None
    pipeline_key: Optional[str]=None
    pipeline_order: Optional[int]=None
    pipeline_type: Optional[str]=None
    content: Optional[str]=None

class Pipeline(BaseModel):
    id:Optional[int]
    pipeline_id: Optional[str]
    parent_pipeline_id:Optional[str]
    pipeline_key: Optional[str]
    pipeline_order: Optional[int]
    pipeline_type: Optional[str]
    content: Optional[str]

class QueryModule(BaseModel):
    module_type: Optional[str]
    module_name: Optional[str]
    pipeline_key:Optional[str]
    module_dir: Optional[str]=None
