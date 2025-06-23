from typing import Optional
from pydantic import BaseModel

class Literature(BaseModel):
    id: Optional[int]
    title: Optional[str]
    url: Optional[str]
    content: Optional[str]
    relation_id: Optional[int]=None
    translate: Optional[str]=None
    interpretation: Optional[str]=None
    img: Optional[str]=None
    journal: Optional[str]=None
    publish_date: Optional[str]=None
    keywords: Optional[str]=None
    literature_key: Optional[str]=None
    literature_type: Optional[str]=None


  

class LiteratureQuery(BaseModel):
    title: Optional[str]=None
    url: Optional[str]=None
    content: Optional[str]=None
    obj_key: Optional[str]=None
    obj_type: Optional[str]=None
    page_number: Optional[int] = 1
    page_size: Optional[int] = 10
    literature_key: Optional[str]=None