from typing import Optional
from pydantic import BaseModel

class CreateStore(BaseModel):
    store_id: Optional[str]
    url: Optional[str]
    name: Optional[str]
    status: Optional[str]
    log : Optional[str]
