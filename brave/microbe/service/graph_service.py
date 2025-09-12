
from brave.api.config.config import  get_graph

def find_entity( entity_type, entity_id: str):
    graph = get_graph()
    node = graph.nodes.match(entity_type, entity_id=entity_id).first()
    return node 


def update_entity(node, update_fields: dict):
    graph = get_graph()
 
    if not node:
        return False  # 或者 raise Exception("Entity not found")
    
    # 更新属性
    for k, v in update_fields.items():
        node[k] = v
    
    # 保存更新
    graph.push(node)
    return True



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