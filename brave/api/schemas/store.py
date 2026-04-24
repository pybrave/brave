from typing import Optional
from pydantic import BaseModel

class CreateStore(BaseModel):
    url: Optional[str]
    path: Optional[str]=None
    name: Optional[str]=None
    status: Optional[str]=None
    path_name: Optional[str]=None
    log : Optional[str]=None
