
from fastapi import APIRouter,Query
from brave.api.config.config import  get_graph
from py2neo import Graph, Node, Relationship

from brave.microbe.schemas.entity import RelationshipRequest

entity_relation_api = APIRouter(prefix="/entity-relation")

@entity_relation_api.get("/test")
async def test_entity_relation():
    graph = get_graph()
    return {"message": "Entity relation endpoint is working"}



@entity_relation_api.post("/relationships")
def create_relationship(req: RelationshipRequest):
    graph = get_graph()
    # MERGE 节点 A
    query = f"""
    MERGE (a:{req.from_entity.label} {{entity_id: $from_id}})
    ON CREATE SET a += $from_props
    ON MATCH SET a += $from_props

    MERGE (b:{req.to_entity.label} {{entity_id: $to_id}})
    ON CREATE SET b += $to_props
    ON MATCH SET b += $to_props

    MERGE (a)-[r:{req.relation_type}]->(b)
    RETURN a, r, b
    """
    params = {
        "from_id": req.from_entity.entity_id,
        "from_props": req.from_entity.properties,
        "to_id": req.to_entity.entity_id,
        "to_props": req.to_entity.properties,
    }
    result = graph.run(query, **params).data()
    return {"result": result}


@entity_relation_api.get("/graph")
def get_graph_relations(label: str = Query(None), keyword: str = Query(None)):
    """
    获取图数据
    - label: 过滤节点类型，如 Study, Disease, Taxonomy
    - keyword: 过滤节点名称包含关键词
    """
    graph = get_graph()

    # 基础查询
    query = "MATCH (a)-[r]->(b) WHERE 1=1 "
    params = {}

    # 按标签过滤
    if label:
        query += "AND ($label IN labels(a) OR $label IN labels(b)) "
        params["label"] = label

    # 按关键词过滤
    if keyword:
        query += "AND (a.entity_name CONTAINS $keyword OR b.entity_name CONTAINS $keyword) "
        params["keyword"] = keyword

    query += """
    RETURN a.entity_id AS from_id, labels(a) AS from_label, a.entity_name AS from_name,
           b.entity_id AS to_id, labels(b) AS to_label, b.entity_name AS to_name,
           type(r) AS relation_type
    """

    result = graph.run(query, **params).data()

    nodes_dict = {}
    links = []

    for record in result:
        # 添加节点（去重）
        if record["from_id"] not in nodes_dict:
            nodes_dict[record["from_id"]] = {
                "id": record["from_id"],
                "label": record["from_label"][0] if record["from_label"] else "Unknown",
                "entity_name": record["from_name"]
            }
        if record["to_id"] not in nodes_dict:
            nodes_dict[record["to_id"]] = {
                "id": record["to_id"],
                "label": record["to_label"][0] if record["to_label"] else "Unknown",
                "entity_name": record["to_name"]
            }

        # 添加关系
        links.append({
            "source": record["from_id"],
            "target": record["to_id"],
            "type": record["relation_type"]
        })

    return {
        "nodes": list(nodes_dict.values()),
        "links": links
    }