from pydantic import BaseModel
from typing import Optional

class SaveContext(BaseModel):
    name:Optional[str]=None
    type:Optional[str]=None
    context_id:Optional[str]=None