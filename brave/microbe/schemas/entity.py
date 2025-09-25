from typing import Optional,Any
from pydantic import BaseModel
from typing import Dict
class PageEntity(BaseModel):
    page_number: Optional[int]=1
    page_size: Optional[int]=10
    parent_id: Optional[str]=None
    category: Optional[Any]=None
    # major_category: Optional[str]=None
    keywords: Optional[str]=None
    is_research: Optional[bool]=None
    locale:Optional[str]="en_US"
    registry_join: Optional[str]=None




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
    nodes_dict: Optional[Dict[str, list[str]]] = None
    nodes_dict_condition: Optional[str] = "OR"  # "AND" 或 "OR"
    order_by: Optional[str] = "taxonomy"  # 排序字段
    order_metric: Optional[str] = "study"  # study
    collect_association_study: Optional[bool]= False
    locale:Optional[str]="en_US"


class GraphQueryV2(BaseModel):
    entity_id: Optional[str]=None
    entity_type: Optional[str]=None  # taxonomy / disease / intervention / microbe / study
    keyword: Optional[str]=None
    depth: int = 1  # 关系深度，可控制查询范围
    relation_types: Optional[list[str]]=None  # 指定需要的关系类型


class NodeQuery(BaseModel):
    label: str                       # 节点 label
    keyword: Optional[str] = None    # 可选关键字
    page: int = 1                    # 页码，从 1 开始
    page_size: int = 20              # 每页数量


class DetailsNodeQuery(BaseModel):
    nodes: Optional[list[str]] = []  # 需要查询的关联节点类型，如 taxonomy, disease, diet_and_food, study


class AddMeshNode(BaseModel):
    category: Optional[str]  
    entity_name: str
    entity_name_zh: Optional[str] = None
    entity_type: Optional[str] = None
    tags: Optional[str] = None
    short_name: Optional[str] = None    
    describe: Optional[str] = None

    parent_tree: Optional[str] = None  # 可以为 None


