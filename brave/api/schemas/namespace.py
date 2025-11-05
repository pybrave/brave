from pydantic import BaseModel
from typing import Optional

class SaveNamespace(BaseModel):
    name:Optional[str]=None
    namespace_id:Optional[str]=None
    volumes:Optional[str]=None
    resources:Optional[str]=None
    queue_size:Optional[int]=10