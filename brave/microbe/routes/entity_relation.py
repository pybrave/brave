
from fastapi import APIRouter, HTTPException,Query
from brave.api.config.config import  get_graph
from py2neo import Graph, Node, Relationship

from brave.microbe.schemas.entity import GraphQuery, RelationshipRequest

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


@entity_relation_api.post("/graph-v2")
def get_graph_relations(graphQuery: GraphQuery):
    """
    获取图数据
    - label: 过滤节点类型，如 Study, Disease, Taxonomy
    - keyword: 过滤节点名称包含关键词
    """
    graph = get_graph()
    label = graphQuery.label
    keyword = graphQuery.keyword
    entity_id = graphQuery.entity_id

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
    # 按 entity_id 过滤
    if entity_id:
        query += "AND (a.entity_id = $entity_id OR b.entity_id = $entity_id) "
        params["entity_id"] = entity_id

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

@entity_relation_api.post("/graph")
def get_graph_relations(graphQuery: GraphQuery):
    """
    获取图数据，包括游离节点
    """
    graph = get_graph()
    label = graphQuery.label
    keyword = graphQuery.keyword
    entity_id = graphQuery.entity_id

    params = {}
    where_clauses = []

    if label:
        where_clauses.append("$label IN labels(n)")
        params["label"] = label
    if keyword:
        where_clauses.append("n.entity_name CONTAINS $keyword")
        params["keyword"] = keyword
    if entity_id:
        where_clauses.append("n.entity_id = $entity_id")
        params["entity_id"] = entity_id

    # 1️ 查询节点
    node_query = "MATCH (n) "
    if where_clauses:
        node_query += "WHERE " + " AND ".join(where_clauses) + " "
    node_query += "RETURN n.entity_id AS id, labels(n) AS labels, n.entity_name AS entity_name, id(n) AS node_id"

    node_results = graph.run(node_query, **params).data()

    nodes_dict = {}
    for node in node_results:
        nodes_dict[node["id"]] = {
            "id": node["id"],
            "node_id": node["node_id"],
            "label": node["labels"][0] if node["labels"] else "Unknown",
            "entity_name": node["entity_name"]
        }

    # 2️ 查询关系
    rel_query = "MATCH (a)-[r]->(b) WHERE 1=1 "
    if label:
        rel_query += "AND ($label IN labels(a) OR $label IN labels(b)) "
    if keyword:
        rel_query += "AND (a.entity_name CONTAINS $keyword OR b.entity_name CONTAINS $keyword) "
    if entity_id:
        rel_query += "AND (a.entity_id = $entity_id OR b.entity_id = $entity_id) "

    rel_query += """
    RETURN a.entity_id AS from_id, a.labels AS from_labels, a.entity_name AS from_name, id(a) AS from_node_id,
           b.entity_id AS to_id, b.labels AS to_labels, b.entity_name AS to_name, id(b) AS to_node_id,
           type(r) AS relation_type, id(r) AS relation_id
    """

    rel_results = graph.run(rel_query, **params).data()

    links = []
    for rel in rel_results:
        # 将关系两端节点加入 nodes_dict
        if rel["from_id"] not in nodes_dict:
            nodes_dict[rel["from_id"]] = {
                "id": rel["from_id"],
                "node_id": rel["from_node_id"],
                "label": rel["from_labels"][0] if rel["from_labels"] else "Unknown",
                "entity_name": rel["from_name"]
            }
        if rel["to_id"] not in nodes_dict:
            nodes_dict[rel["to_id"]] = {
                "id": rel["to_id"],
                "node_id": rel["to_node_id"],
                "label": rel["to_labels"][0] if rel["to_labels"] else "Unknown",
                "entity_name": rel["to_name"]
            }

        # 添加关系
        links.append({
            "relation_id": rel["relation_id"],
            "source": rel["from_id"],
            "target": rel["to_id"],
            "type": rel["relation_type"]
        })

    return {
        "nodes": list(nodes_dict.values()),
        "links": links
    }

@entity_relation_api.get("/relation/{relation_id}")
def get_relation_by_id(relation_id: int):
    graph = get_graph()

    query = """
    MATCH (a)-[r]->(b)
    WHERE id(r) = $rid
    RETURN id(r) AS rid, type(r) AS type,
           a.entity_id AS from_id, labels(a) AS from_labels, a.entity_name AS from_name,
           b.entity_id AS to_id, labels(b) AS to_labels, b.entity_name AS to_name,
           properties(r) AS props
    """
    params = {"rid": relation_id}
    record = graph.run(query, **params).data()

    if not record:
        raise HTTPException(status_code=404, detail=f"Relation {relation_id} not found")

    # 如果用 .evaluate 返回的是 dict，则直接返回
    return record[0] 


@entity_relation_api.delete("/relation/{relation_id}")
def delete_relation_by_id(relation_id: int):
    graph = get_graph()

    # # 先获取关系两端节点的 id
    # query_nodes = """
    # MATCH (a)-[r]->(b)
    # WHERE id(r) = $rid
    # RETURN id(a) AS from_id, id(b) AS to_id
    # """
    # record = graph.run(query_nodes, rid=relation_id).data()
    # if not record:
    #     raise HTTPException(status_code=404, detail=f"Relation {relation_id} not found")

    # from_id = record[0]["from_id"]
    # to_id = record[0]["to_id"]

    # 删除关系
    query_delete_relation = """
    MATCH ()-[r]->()
    WHERE id(r) = $rid
    DELETE r
    """
    graph.run(query_delete_relation, rid=relation_id)

    # # 删除孤立节点（没有任何关系的节点）
    # query_delete_isolated_nodes = """
    # MATCH (n)
    # WHERE id(n) IN [$from_id, $to_id] AND NOT (n)--()
    # DELETE n
    # """
    # graph.run(query_delete_isolated_nodes, from_id=from_id, to_id=to_id)

    # return {"message": f"Relation {relation_id} deleted successfully, isolated nodes removed if any."}
    return {"message": f"Relation {relation_id} deleted successfully."}


