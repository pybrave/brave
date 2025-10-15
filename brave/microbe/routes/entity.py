from fastapi import APIRouter, HTTPException, Query
from brave.api.config.db import get_engine
from brave.microbe.models.core import t_taxonomy
from brave.microbe.service import study_service
from brave.microbe.service import  disease_service
from brave.microbe.service import  chemicals_and_drugs_service
from brave.microbe.service import  diet_and_food_service
from brave.microbe.service import  association_service
from brave.microbe.service import  mesh_service

from sqlalchemy import insert
import brave.microbe.service.taxonomy_service as taxonomy_service
from brave.microbe.schemas.entity import AddMeshNode, DetailsNodeQuery, NodeQuery, PageEntity
from brave.microbe.service import graph_service
from brave.api.config.config import  get_graph
import json
entity_api = APIRouter(prefix="/entity")


@entity_api.get("/init/{entity}")
def import_taxonomy(entity,category=None):
    with get_engine().begin() as conn:
        if entity == "taxonomy":
            return  taxonomy_service.init(conn)
        elif entity == "disease":
            return disease_service.init(conn)
        elif entity == "mesh":
            return mesh_service.init(conn,category)
        else:
            raise ValueError("Unsupported entity type")
        # 读取三张表并合并

def formt_items_json(item):
    if "tags" in item and item["tags"]:
        try:
            item["tags"] = json.loads(item["tags"])
        except:
            pass
    if "short_name" in item and item["short_name"]:
        try:
            item["short_name"] = json.loads(item["short_name"])
        except:
            pass
    return item
def formt_items(item):
    item = dict(item)
    return formt_items_json(item)
    

@entity_api.post("/page/{entity}")
async def page_entity(entity: str, query: PageEntity):
    with get_engine().begin() as conn:
        if entity == "taxonomy":    
            result = taxonomy_service.page_taxonomy_v3(conn, query)
        elif entity == "study":
            result = study_service.page_study(conn, query)  
        elif entity == "disease":
            result = disease_service.page_disease(conn, query)
        elif entity == "chemicals_and_drugs":
            result = chemicals_and_drugs_service.page(conn, query)
        elif entity == "diet_and_food":
            result = diet_and_food_service.page(conn, query)
        elif entity == "association":
            result = association_service.page(conn, query)
        elif entity =="mesh":
            result = mesh_service.page(conn,query)
        else:
            raise ValueError("Unsupported entity type")
    
    entity_ids = [item["entity_id"] for item in result["items"]]
    # entity_ids_map = graph_service.check_nodes_exist_batch(entity_ids,entity)
    # result["items"] = [{"is_exist_graph":entity_ids_map[item["entity_id"]],**formt_items(item)} for item in result["items"]]
    return result

@entity_api.get("/get/{entity}/{entity_id}")
async def get_entity(entity: str, entity_id: str):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.find_taxonomy_by_id(conn, entity_id)
        elif entity == "study":
            result = study_service.find_study_by_id(conn, entity_id)
        elif entity == "disease":
            result = disease_service.find_disease_by_id(conn, entity_id)
        elif entity == "chemicals_and_drugs":
            result = chemicals_and_drugs_service.find_by_id(conn, entity_id)
        elif entity == "diet_and_food":
            result = diet_and_food_service.find_by_id(conn, entity_id)
        elif entity =="association":
            result = association_service.find_by_id(conn, entity_id)
        elif entity =="mesh":
            result = mesh_service.find_by_id(conn,entity_id)
        else:
            raise ValueError("Unsupported entity type")
    result = dict(result)
    # result["entity_type"] = entity
    result = formt_items_json(result)
    return result

@entity_api.put("/update/{entity}/{entity_id}")
async def update_entity(entity: str, entity_id: str, updateData: dict):
    if "tags" in updateData and isinstance(updateData["tags"], list):
        updateData["tags"] = json.dumps(updateData["tags"], ensure_ascii=False)
    if "short_name" in updateData and isinstance(updateData["short_name"], list):
        updateData["short_name"] = json.dumps(updateData["short_name"], ensure_ascii=False)
    with get_engine().begin() as conn:
        if entity == "taxonomy":
            taxonomy_service.update_taxonomy(conn, entity_id, updateData)
        elif entity == "study":
            study_service.update_study(conn, entity_id, updateData) 
        elif entity == "disease":
            disease_service.update_disease(conn, entity_id, updateData)  
        elif entity == "chemicals_and_drugs":
            chemicals_and_drugs_service.update(conn, entity_id, updateData)
        elif entity == "diet_and_food":
            diet_and_food_service.update(conn, entity_id, updateData)
        elif entity == "association":
            association_service.update(conn, entity_id, updateData)
            find_data = association_service.find_by_id(conn, entity_id)
            find_association= dict(find_data)
            entity_,relationship = association_service.get_entity(conn,find_association)
            graph_service.create_node_relation(entity_,relationship)
        elif entity =="mesh":
            mesh_service.update(conn, entity_id, updateData)
        else:
            raise ValueError("Unsupported entity type")
    if entity != "association": 
        find_node = graph_service.find_entity( entity, entity_id=entity_id)  # 同步更新图数据库中的节点信息
        if find_node:
            graph_service.update_entity(find_node, updateData)
    return {"message": "Entity updated successfully"}

@entity_api.post("/add/{entity}")
async def add_entity(entity: str, data: dict):
    if "tags" in data and isinstance(data["tags"], list):
        data["tags"] = json.dumps(data["tags"], ensure_ascii=False)
    if "short_name" in data and isinstance(data["short_name"], list):
        data["short_name"] = json.dumps(data["short_name"], ensure_ascii=False)
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            taxonomy_service.add_taxonomy(conn, data)
        elif entity == "study":
            study_service.add_study(conn, data)     
        elif entity == "disease":   
            disease_service.add_disease(conn, data)
        elif entity == "chemicals_and_drugs":
            chemicals_and_drugs_service.add(conn, data)
        elif entity == "diet_and_food":
            diet_and_food_service.add(conn, data)
        elif entity == "association":
            entity_id = association_service.add(conn, data)
            find_data = association_service.find_by_id(conn, entity_id)
            find_association= dict(find_data)
            entity,relationship = association_service.get_entity(conn,find_association)
            graph_service.create_node_relation(entity,relationship)
            pass
        elif entity =="mesh":
            mesh_service.add_mesh_node(conn, AddMeshNode(**data))
        else:
            raise ValueError("Unsupported entity type")
    return {"message": "Entity added successfully"}



@entity_api.get("/find-by-name/{entity}/{keywords}")
async def get_entity(entity: str, keywords: str):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.find_taxonomy_by_keywords(conn, keywords)
        elif entity == "study":
            result = study_service.find_study_by_keywords(conn, keywords)
        elif entity == "disease":
            result = disease_service.find_disease_by_keywords(conn, keywords)
        elif entity == "chemicals_and_drugs":
            result = chemicals_and_drugs_service.find_by_keywords(conn, keywords)
        elif entity == "diet_and_food":
            result = diet_and_food_service.find_by_keywords(conn, keywords)
        elif entity =="association":
            result = association_service.find_by_keywords(conn, keywords)
        elif entity =="mesh":
            result = mesh_service.find_by_keywords(conn,keywords)
        else:
            raise ValueError("Unsupported entity type")
    return result



@entity_api.post("/details/{entity}/{entity_id}")
async def get_entity(entity: str, entity_id: str,
                     detailsNodeQuery: DetailsNodeQuery):
    with get_engine().begin() as conn:
        if entity=="taxonomy":  
            result = taxonomy_service.details_taxonomy_by_id(conn, entity_id)
        elif entity == "study":
            result = study_service.details_study_by_id(conn, entity_id)
        elif entity == "disease":
            result = disease_service.details_disease_by_id(conn, entity_id)
        elif entity == "chemicals_and_drugs":
            result = chemicals_and_drugs_service.details_by_id(conn, entity_id)
        elif entity == "diet_and_food": 
            result = diet_and_food_service.details_by_id(conn, entity_id)
        elif entity =="association":
            result = graph_service.get_association_details(entity_id)
        elif entity =="mesh":
            result = mesh_service.details_by_id(conn,entity_id)
        else:
            raise ValueError("Unsupported entity type")
    if type(result) != dict:
        # raise HTTPException(status_code=404, detail=f"{entity} with id {entity_id} not found")
        result = dict(result)
    # result["entity_type"] = entity
    nodes = detailsNodeQuery.nodes
    if entity not in nodes:
        nodes.append(entity)
    if "study" not in nodes:
        nodes.append("study")
    graph_table = graph_service.find_associations_by_entity_id(entity_type=entity,entity_id=entity_id,nodes=detailsNodeQuery.nodes)
    if len(graph_table)==1:
        result["graph_table"] = graph_table[0]
    else:
        raise HTTPException(status_code=404, detail=f"Graph data for {entity} with id {entity_id} not found or many records found") 

    return result

@entity_api.post("/import/{entity}")
async def import_entitys(entity: str, entity_list: list[dict]):
    with get_engine().begin() as conn:
        if entity == "taxonomy":
            result = taxonomy_service.import_taxonomy(conn, entity_list)
        elif entity == "study":
            result = study_service.import_studies(conn, entity_list)
        elif entity == "disease":
            result = disease_service.import_diseases(conn, entity_list)
        elif entity == "chemicals_and_drugs":
            result = chemicals_and_drugs_service.imports(conn, entity_list)
        elif entity == "diet_and_food":
            result = diet_and_food_service.imports(conn, entity_list)
        elif entity == "association":
            result = association_service.imports(conn, entity_list)
        elif entity =="mesh":
            result = mesh_service.imports(conn,entity_list)
        else:
            raise ValueError("Unsupported entity type")
    return result


@entity_api.delete("/delete/{entity}/{entity_id}")
async def delete_entity(entity: str, entity_id: str,force: bool=False):
   
    find_entity = graph_service.find_entity( entity, entity_id)
    if find_entity:
        raise HTTPException(status_code=400, detail=f"Cannot delete {entity}({entity_id}) that exists in graph database")
        # return {"message": "Cannot delete entity that exists in graph database"}
    else: 
        with get_engine().begin() as conn:
            if entity == "taxonomy":
                taxonomy_service.delete_taxonomy_by_id(conn, entity_id)
            elif entity == "study":
                study_service.delete_study_by_id(conn, entity_id)
            elif entity == "disease":
                disease_service.delete_disease_by_id(conn, entity_id)
            elif entity == "chemicals_and_drugs":
                chemicals_and_drugs_service.delete_by_id(conn, entity_id)
            elif entity == "diet_and_food":
                diet_and_food_service.delete_by_id(conn, entity_id)
            # elif entity == "association":
            #     association_service.delete_by_id(conn, entity_id)
            elif entity =="mesh":
                mesh_service.delete_by_id(conn,entity_id)
            else:
                raise ValueError("Unsupported entity type")
        return {"message": "Entity deleted successfully"}

@entity_api.delete("/delete-node/{entity}/{entity_id}")
async def delete_entity_node(entity: str, entity_id: str):
    graph_service.delete_node_by_entity_id(entity, entity_id)
    return {"message": "Entity node and its relationships deleted successfully"}


@entity_api.get("/nodes")
async def get_all_nodes():
    graph = get_graph()
    
    # 查询所有节点
    query = """
    MATCH (n)
    RETURN id(n) AS id, labels(n) AS labels, n.entity_id AS entity_id, n.entity_name AS entity_name, properties(n) AS props
    """
    results = graph.run(query).data()
    
    return {
        "total": len(results),
        "nodes": results
    }

@entity_api.delete("/node-id/{node_id}")
def delete_node_by_id(node_id: int):
    graph_service.delete_by_node_id(node_id)
    return {"message": f"Node {node_id} and its relationships deleted successfully"}


@entity_api.post("/query-nodes")
def query_nodes(query: NodeQuery):
    return graph_service.query_nodes(query)