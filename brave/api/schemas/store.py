from typing import Optional
from pydantic import BaseModel

class CreateStore(BaseModel):
    store_id: Optional[str]=None
    url: Optional[str]=None
    # path: Optional[str]=None
    name: Optional[str]=None
    # status: Optional[str]=None
    # path_name: Optional[str]=None
    # log : Optional[str]=None
    category: Optional[str]=None
    # publish_urls: Optional[dict]=None
    version: Optional[str]=None
    update_info: Optional[str]=None


class StoreQuery(BaseModel):
    store_id: Optional[str]=None
    url: Optional[str]=None
    name: Optional[str]=None
    status: Optional[str]=None
    path_name: Optional[str]=None
    category: Optional[str]=None