
from brave.api.config.config import  get_graph
from brave.microbe.schemas.entity import GraphQuery, NodeQuery
from py2neo import Graph, Node, Relationship

def find_entity( entity_type, entity_id: str):
    graph = get_graph()
    node = graph.nodes.match(entity_type, entity_id=entity_id).first()
    return node 





def check_nodes_exist_batch(entity_ids: list[str], label: str = None):
    graph = get_graph()
    query = f"""
    MATCH (n{':' + label if label else ''})
    WHERE n.entity_id IN $entity_ids
    RETURN n.entity_id AS entity_id
    """
    result = graph.run(query, entity_ids=entity_ids).data()
    found_ids = {r["entity_id"] for r in result}
    return {eid: eid in found_ids for eid in entity_ids}


def delete_node_by_entity_id(label: str , entity_id: str):
    graph = get_graph()
    """
    根据 entity_id 删除节点及其所有关系
    """
    query = f"""
    MATCH (n{':' + label if label else ''} {{entity_id: $entity_id}})
    OPTIONAL MATCH (n)-[r]-()
    DELETE r, n
    """
    graph.run(query, entity_id=entity_id)
    print(f"Node {entity_id} and its relationships deleted successfully")


def delete_by_node_id(node_id: int):
    graph = get_graph()
    """
    根据节点的内部 ID 删除节点及其所有关系
    """
    query = """
    MATCH (n)
    WHERE id(n) = $node_id
    DETACH DELETE n
    """
    graph.run(query, node_id=node_id)
    print(f"Node with ID {node_id} and its relationships deleted successfully")


def  get_association_details(association_id: str):
    graph = get_graph()
    query = """
    MATCH (s:study)<-[:EVIDENCED_BY]-(a:association)
    MATCH (a)-[:OBSERVED_IN]->(d:disease)
    MATCH (a)-[:SUBJECT]->(i:diet_and_food)
    MATCH (a)-[:OBJECT]->(t:taxonomy)
    WHERE a.entity_id = $association_id
    RETURN a.entity_id AS association_id, a.effect AS effect,
            collect(DISTINCT {id: s.entity_id, name: s.entity_name}) AS studies,
            collect(DISTINCT  {id: d.entity_id, name: d.entity_name})  as  diseases,
            collect(DISTINCT  {id: i.entity_id, name: i.entity_name}) as  diet_and_foods,
            collect(DISTINCT  {id: t.entity_id, name: t.entity_name}) as taxonomies

    """
    result = graph.run(query, association_id=association_id).data()
    if result:
        return result[0]
    raise ValueError(f"Association {association_id} not found")

def get_nodes_by_label(label: str, page: int = 1, page_size: int = 20):
    graph = get_graph()
    """
    分页查询指定 label 的节点
    :param label: 节点 label，例如 'taxonomy'
    :param page: 页码，从 1 开始
    :param page_size: 每页条数
    :return: 节点列表
    """
    skip = (page - 1) * page_size
    query = f"""
    MATCH (n:{label})
    RETURN n
    SKIP $skip
    LIMIT $limit
    """
    result = graph.run(query, skip=skip, limit=page_size)
    return [record["n"] for record in result]


def query_nodes(query: NodeQuery):
    graph = get_graph()
    skip = (query.page - 1) * query.page_size
    # keyword 过滤条件
    if query.keyword:
        cypher = f"""
        MATCH (n:{query.label})
        WHERE n.entity_name CONTAINS $keyword
        RETURN n
        SKIP $skip
        LIMIT $limit
        """
        params = {"keyword": query.keyword, "skip": skip, "limit": query.page_size}
    else:
        cypher = f"""
        MATCH (n:{query.label})
        RETURN n
        SKIP $skip
        LIMIT $limit
        """
        params = {"skip": skip, "limit": query.page_size}

    result = graph.run(cypher, **params)
    return [record["n"] for record in result]


def build_cypher(graphQuery:GraphQuery):
    label = graphQuery.label
    keyword = graphQuery.keyword
    entity_id = graphQuery.entity_id

  
    node_var_map = {
        "association": "a",
        "study": "s",
        "taxonomy": "t",
        "disease": "d",
        "diet_and_food": "i"
    }
 

    query = """
    MATCH (s:study)<-[:EVIDENCED_BY]-(a:association)
    """
    if "disease" in graphQuery.nodes:
        query += " MATCH (a)-[:OBSERVED_IN]->(d:disease)"
    if "diet_and_food" in graphQuery.nodes:
        query += " MATCH (a)-[:SUBJECT]->(i:diet_and_food)"
    if "taxonomy" in graphQuery.nodes:
        query += " MATCH (a)-[:OBJECT]->(t:taxonomy)"

    params = {}
    # query +=" WHERE 1=1"
   
    where_clauses = []
    if keyword:
        params["keyword"] = keyword
        keyword_filters = []
        if "taxonomy" in graphQuery.nodes:
            keyword_filters.append("t.entity_name CONTAINS $keyword")
        if "disease" in graphQuery.nodes:
            keyword_filters.append("d.entity_name CONTAINS $keyword")
        if "diet_and_food" in graphQuery.nodes:
            keyword_filters.append("i.entity_name CONTAINS $keyword")
        if "study" in graphQuery.nodes:
            keyword_filters.append("s.entity_name CONTAINS $keyword")
        if keyword_filters:
            where_clauses.append("(" + " OR ".join(keyword_filters) + ")")

    if entity_id:
        params["entity_id"] = entity_id
        # 统一 entity_id 匹配，不管节点多少
        entity_filters = []
        entity_filters.append("a.entity_id = $entity_id")
        if "taxonomy" in graphQuery.nodes:
            entity_filters.append("t.entity_id = $entity_id")
        if "disease" in graphQuery.nodes:
            entity_filters.append("d.entity_id = $entity_id")
        if "diet_and_food" in graphQuery.nodes:
            entity_filters.append("i.entity_id = $entity_id")
        
        if entity_filters:
            where_clauses.append("(" + " OR ".join(entity_filters) + ")")

    nodes_dict_where_clauses = []
    if graphQuery.nodes_dict and len(graphQuery.nodes_dict)>0:
        for node_label, ids in graphQuery.nodes_dict.items():
            if not ids and len(ids)==0:
                continue
            params[f"{node_label}_ids"] = ids
            # 节点 label 映射到变量
            
            var = node_var_map.get(node_label)
            if var:
                nodes_dict_where_clauses.append(f"{var}.entity_id IN ${node_label}_ids")
        if len(nodes_dict_where_clauses) >0:
            if graphQuery.nodes_dict_condition =='OR':
                where_clauses.append("(" + " OR ".join(nodes_dict_where_clauses) + ")")
            else:
                where_clauses.append("(" + " AND ".join(nodes_dict_where_clauses) + ")")

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)


    # with_nodes = ["a","s"] + [node_var_map[n] for n in graphQuery.nodes if n != "association"]
    # with_clause = "WITH " + ", ".join(with_nodes)
    # query += "\n" + with_clause

    # query += """
    # RETURN a.entity_id AS association_id, a.effect AS effect,
           

    # """   
  

#   t.entity_id AS taxonomy_id, t.entity_name AS taxonomy_name,
#             d.entity_id AS disease_id, d.entity_name AS disease_name,
#            i.entity_id AS intervention_id, i.entity_name AS intervention_name,
  
    # if "disease" in graphQuery.nodes:
    #     query += ", d.entity_id AS disease_id, d.entity_name AS disease_name"
    # if "diet_and_food" in graphQuery.nodes:
    #     query += ", i.entity_id AS diet_and_food_id, i.entity_name AS diet_and_food_name"
    # if "taxonomy" in graphQuery.nodes:
    #     query += """
    #     , t.entity_id AS taxonomy_id, t.entity_name AS taxonomy_name, 
    #         SIZE([ (t)<-[:OBJECT]-(:association) | 1 ]) AS taxonomy_links
    #     """
    # if "study" in graphQuery.nodes:
    #     query += ", s.entity_id AS study_id, s.entity_name AS study_name"
 
    return query, params,node_var_map

def build_return_cypher(query:str,graphQuery:GraphQuery):
    return_fields_map = {
        "association": ["a.entity_id AS association_id", "a.effect AS effect"],
        "study": ["s.entity_id AS study_id", "s.entity_name AS study_name"],
        "taxonomy": [
            "t.entity_id AS taxonomy_id",
            "t.entity_name AS taxonomy_name"
        ],
        "disease": ["d.entity_id AS disease_id", "d.entity_name AS disease_name"],
        "diet_and_food": ["i.entity_id AS diet_and_food_id", "i.entity_name AS diet_and_food_name"]
    }
    if graphQuery.collect_association_study:
        return_fields_map.get("association").append(
            "collect(DISTINCT {id: s.entity_id, name: s.entity_name}) AS studies"
        )
        # "collect(DISTINCT {id: s.entity_id, name: s.entity_name}) AS studies "
    if graphQuery.order_by and graphQuery.order_by in return_fields_map:
        order_by = graphQuery.order_by
        field = return_fields_map.get(order_by)
        if graphQuery.order_metric == "study":
            field.append(f"SIZE([ (t)<-[]-(:association)-[:EVIDENCED_BY]->(:study) | 1 ]) AS {order_by}_links")
        elif graphQuery.order_metric=="link":
            field.append(
                f"SIZE([ (t)<-[]-(:association) | 1 ]) AS {order_by}_links"
            )
        else:
            field.append(
                f" COUNT(DISTINCT s) AS {order_by}_links"
            )
            

    return_fields = []
    return_fields.extend(return_fields_map.get("association", []))
    for n in graphQuery.nodes:
        return_fields.extend(return_fields_map.get(n, []))
    
    query += "\nRETURN " + ", ".join(return_fields)
    return query

def build_order_cypher(query:str,graphQuery:GraphQuery):
    if graphQuery.order_by in graphQuery.nodes:
        query += f"\nORDER BY {graphQuery.order_by}_links DESC"
    return query


def build_collect_return_cypher(query:str,entity_type:str,graphQuery:GraphQuery,node_var_map:dict):
    study_var =  ["id: s.entity_id", "name: s.entity_name","effect:a.effect"]
    for n in graphQuery.nodes:
        if n == "study":
            continue
        var = node_var_map.get(n)
        if var:
            study_var.append(f"{n}_id: {var}.entity_id")
            study_var.append(f"{n}_name: {var}.entity_name")
    study_var_str = " , ".join(study_var)
    return_collect_fields_map = {
        # "association": ["collect(DISTINCT {id: a.entity_id, name: a.entity_name}) AS associations"],
        "study": ["collect(DISTINCT { "+ study_var_str +" }) AS studies"],
        "taxonomy": ["collect(DISTINCT {id: t.entity_id, name: t.entity_name}) AS taxonomys"],
        "disease": ["collect(DISTINCT {id: t.entity_id, name: t.entity_name}) AS diseases"],
        "diet_and_food": ["collect(DISTINCT {id: t.entity_id, name: t.entity_name}) AS diet_and_foods"]
    }
    return_fields_map = {
        "association": ["a.entity_id AS association_id", "a.effect AS effect"],
        "study": ["s.entity_id AS study_id", "s.entity_name AS study_name"],
        "taxonomy": [
            "t.entity_id AS taxonomy_id",
            "t.entity_name AS taxonomy_name"
        ],
        "disease": ["d.entity_id AS disease_id", "d.entity_name AS disease_name"],
        "diet_and_food": ["i.entity_id AS diet_and_food_id", "i.entity_name AS diet_and_food_name"]
    }

    return_fields = []
    # return_fields.extend(return_collect_fields_map.get("association", []))
    for n in graphQuery.nodes:
        if n != entity_type:
            return_fields.extend(return_collect_fields_map.get(n, []))

    return_fields.extend(return_fields_map.get(entity_type, []))

    query += "\nRETURN " + ", ".join(return_fields)
    return query
def find_associations_by_entity_id(entity_type:str,entity_id: str,nodes :list[str]):
    graphQuery = GraphQuery(
        entity_id=entity_id,
        nodes=nodes,
        order_by=None
    )
    query,params,node_var_map =build_cypher(graphQuery)
    query = build_collect_return_cypher(query,entity_type,graphQuery,node_var_map)
    graph = get_graph()
    result = graph.run(query, **params)
    
    # print(find_cypher)
    return result.data()

def update_entity(node, entity_dict: dict):
    graph = get_graph()
    update_fields = ["entity_name","entity_name_zh"]
    entity_dict = {k: v for k, v in entity_dict.items() if k in update_fields}
    if not node:
        return False  # 或者 raise Exception("Entity not found")
    
    # 更新属性
    for k, v in entity_dict.items():
        node[k] = v
    
    # 保存更新
    graph.push(node)
    return True



def create_node_relation(entity,relationship):
    entity_dict = {}
    graph = get_graph()
    for k, v in entity.items():
    
        props = {prop: val for prop, val in {
            "entity_id": v.get("entity_id"),
            "entity_name": v.get("entity_name"),
            "entity_name_zh": v.get("entity_name_zh")
        }.items() if val not in (None, "")}

        if props.get("entity_id") is None:
            raise ValueError("entity_id is required")
        
        node = Node(v["entity_type"], **props)
        graph.merge(node, v["entity_type"], "entity_id")
        entity_dict[k] = node

    # query = """
    # MATCH (a:Disease {entity_id:$a_id}), (b:Gene {entity_id:$b_id})
    # MERGE (a)-[r:EVIDENCED_BY {association_id:$assoc_id}]->(b)
    # ON CREATE SET r += $props
    # ON MATCH SET  r += $props
    # """
    # graph.run(query, a_id="D0001", b_id="G0001", assoc_id="R1", props={"source":"PMID1"})
    association_id = relationship.get("association_id")
    predicate = relationship.get("predicate")
    # rel = Relationship(entity_dict["subject"],predicate, entity_dict["object"],**relationship,identity=association_id)

    # graph.create(rel)
    query = """
    MATCH (a {{entity_id:$a_id}}), (b {{entity_id:$b_id}})
    MERGE (a)-[r:{predicate} {{association_id:$assoc_id}}]->(b)
    ON CREATE SET r += $props
    ON MATCH SET r += $props
    RETURN r
    """.format(predicate=predicate)
    props = {k:v for k,v in relationship.items() if k != "association_id" and k != "predicate"}

    graph.run(query, a_id=entity_dict["subject"]["entity_id"],
                b_id=entity_dict["object"]["entity_id"],
                assoc_id=association_id,
                props=props)
    # relationship = {k: v for k, v in relationship.items() if k not in ["association_id"]}

    # # 赋值给关系对象
    # for k, v in relationship.items():
    #     rel[k] = v

    # # 再写入数据库
    # graph.push(rel)  # push 会更新已存在节点/关系的属性
    return entity_dict