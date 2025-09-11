from typing import Optional,Any
from pydantic import BaseModel
from typing import Dict
class PageEntity(BaseModel):
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    keywords: Optional[str]=None




class Entity(BaseModel):
    label: str                 # 节点标签，比如 "Taxonomy", "Study", "Disease"
    entity_id: str             # 唯一ID
    properties: Dict[str, Any] # 其他属性，可选

class RelationshipRequest(BaseModel):
    from_entity: Entity
    to_entity: Entity
    relation_type: str         # 关系类型，比如 "ASSOCIATED_WITH"