from typing import Optional
from pydantic import BaseModel

class ComponentStore(BaseModel):
    store_name:Optional[str] = None
    component_type:str
    address:str
    store_path:Optional[str] = "pybrave"
    remote_force:Optional[bool] = False
    branch:Optional[str] = "master"
    token:Optional[str] = None