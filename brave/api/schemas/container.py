from typing import Optional
from pydantic import BaseModel

class PageContainerQuery(BaseModel):
    page_number: Optional[int]=1
    page_size: Optional[int]=10

class SaveContainer(BaseModel):
    name: Optional[str]
    image: Optional[str]
    container_id: Optional[str]=None
    description: Optional[str]=None
    envionment:Optional[str]=None
    command: Optional[str]=None
    port: Optional[str]=None
    labels: Optional[str]=None
    change_uid:Optional[bool]=True
    container_key:Optional[str]=None
    img: Optional[str]=None
    

class ListContainerQuery(BaseModel):
    container_key: Optional[list]=None

