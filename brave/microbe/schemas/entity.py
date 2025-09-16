from typing import Optional,Any
from pydantic import BaseModel
from typing import Dict
class PageEntity(BaseModel):
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    parent_id: Optional[int]=None
    keywords: Optional[str]=None




class Entity(BaseModel):
    label: str                 # 节点标签，比如 "Taxonomy", "Study", "Disease"
    entity_id: str             # 唯一ID
    properties: Dict[str, Any] # 其他属性，可选

class RelationshipRequest(BaseModel):
    from_entity: Entity
    to_entity: Entity
    relation_type: str         # 关系类型，比如 "ASSOCIATED_WITH"

class GraphQuery(BaseModel):
    label: Optional[str] = None
    keyword: Optional[str] = None
    entity_id: Optional[str] = None
    nodes:Optional[list[str]] = None

class GraphQueryV2(BaseModel):
    entity_id: Optional[str]=None
    entity_type: Optional[str]=None  # taxonomy / disease / intervention / microbe / study
    keyword: Optional[str]=None
    depth: int = 1  # 关系深度，可控制查询范围
    relation_types: Optional[list[str]]=None  # 指定需要的关系类型
