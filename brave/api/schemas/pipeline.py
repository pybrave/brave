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
    namespace:Optional[str]=None
    name:Optional[str]=None
    description:Optional[str]=None
    tag:Optional[str]=None
    category:Optional[str]=None
    img:Optional[str]=None

class SavePipelineRelation(BaseModel):
    relation_id:Optional[str]=None
    component_id: Optional[str]=None
    # pipeline_id: Optional[str]=None
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
    namespace:Optional[str]=None


class PagePipelineQuery(BaseModel):
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    component_type: Optional[str]=None
    # component_id: Optional[str]=None


class Pipeline(BaseModel):
    id:Optional[int]
    component_id: Optional[str]
    # parent_pipeline_id:Optional[str]
    # pipeline_key: Optional[str]
    order_index: Optional[int]
    component_type: Optional[str]
    content: Optional[str]
    namespace:Optional[str]

class QueryModule(BaseModel):
    module_type: Optional[str]
    module_name: Optional[str]=None
    component_id:Optional[str]
    file_type:Optional[str]=None
    # module_dir: Optional[str]=None
