from tkinter import N
from typing import Optional
from pydantic import BaseModel

class SavePipeline(BaseModel):
    component_id: Optional[str]=None
    parent_component_id:Optional[str]=None
    pipeline_id: Optional[str]=None
    relation_type: Optional[str]=None
    component_type: Optional[str]
    content: Optional[str]=None

class SavePipelineRelation(BaseModel):
    relation_id:Optional[int]=None
    component_id: Optional[str]=None
    pipeline_id: Optional[str]=None
    parent_component_id:Optional[str]=None
    # pipeline_key: Optional[str]=None
    relation_type: Optional[str]=None


class QueryPipeline(BaseModel):
    component_id: Optional[str]=None
    # parent_pipeline_id:Optional[str]=None
    # pipeline_key: Optional[str]=None
    order_index: Optional[int]=None
    component_type: Optional[str]=None
    content: Optional[str]=None

class Pipeline(BaseModel):
    id:Optional[int]
    component_id: Optional[str]
    # parent_pipeline_id:Optional[str]
    # pipeline_key: Optional[str]
    order_index: Optional[int]
    component_type: Optional[str]
    content: Optional[str]

class QueryModule(BaseModel):
    module_type: Optional[str]
    module_name: Optional[str]=None
    component_id:Optional[str]
    file_type:Optional[str]=None
    # module_dir: Optional[str]=None
