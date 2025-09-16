from fastapi import APIRouter, HTTPException
from brave.api.config.db import get_engine
from brave.microbe.models.core import t_taxonomy
from brave.microbe.service import study_service
from brave.microbe.service import  disease_service
from brave.microbe.service import  chemicals_and_drugs_service
from brave.microbe.service import  diet_and_food_service


from brave.microbe.utils.import_ncbi_taxonomy import merge_all
from sqlalchemy import insert
import brave.microbe.service.taxonomy_service as taxonomy_service
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.service import graph_service
from brave.api.config.config import  get_graph

entity_api = APIRouter(prefix="/entity")


@entity_api.get("/import")
def import_taxonomy():
    with get_engine().begin() as conn:
        # 读取三张表并合并
        taxonomy = merge_all(
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/nodes.dmp",
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/names.dmp",
            "/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/division.dmp"
        )
        # taxonomy["taxonomy_id"] = f"TAX{taxonomy['tax_id']}"
        taxonomy["taxonomy_id"] = "TAX" + taxonomy["tax_id"].astype(str)
        records = taxonomy.to_dict(orient="records")
        batch_size = 20000  # 每次 1w 行，自己调节

        inserted = 0
        with get_engine().begin() as conn:  # type: Connection
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(t_taxonomy)
                conn.execute(stmt, batch)
                inserted += len(batch)
                print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}


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
        else:
            raise ValueError("Unsupported entity type")
    
    entity_ids = [item.entity_id for item in result["items"]]
    entity_ids_map = graph_service.check_nodes_exist_batch(entity_ids,entity)
    result["items"] = [{"is_exist_graph":entity_ids_map[item.entity_id],**item} for item in result["items"]]
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
        else:
            raise ValueError("Unsupported entity type")
    result = dict(result)
    result["entity_type"] = entity
    return result

@entity_api.put("/update/{entity}/{entity_id}")
async def update_entity(entity: str, entity_id: str, updateData: dict):
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
        else:
            raise ValueError("Unsupported entity type")
    find_node = graph_service.find_entity( entity, entity_id=entity_id)  # 同步更新图数据库中的节点信息
    if find_node:
        graph_service.update_entity(find_node, updateData)
    return {"message": "Entity updated successfully"}

@entity_api.post("/add/{entity}")
async def add_entity(entity: str, data: dict):
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
        else:
            raise ValueError("Unsupported entity type")
    return result



@entity_api.get("/details/{entity}/{entity_id}")
async def get_entity(entity: str, entity_id: str):
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
        else:
            raise ValueError("Unsupported entity type")
    if type(result) != dict:
        # raise HTTPException(status_code=404, detail=f"{entity} with id {entity_id} not found")
        result = dict(result)
    result["entity_type"] = entity
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