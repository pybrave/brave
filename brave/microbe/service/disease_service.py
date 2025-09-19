

from operator import and_, or_
from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_disease
from sqlalchemy import select,func
from sqlalchemy.engine import Connection
import pandas as pd
from sqlalchemy import select,func,insert,case,exists

from brave.microbe.utils import import_ncbi_mesh
import json
def page_disease(conn: Connection, query: PageEntity):
    if query.parent_id and query.parent_id=="default":
        query.parent_id = "F03"
    # stmt =select(
    #     t_disease,
    # ) 
    child = t_disease.alias("child")
    stmt = (
        select(
            t_disease,
            case(
                (exists().where(child.c.parent_entity_id == t_disease.c.entity_id), True),
                else_=False
            ).label("has_children")
        )
    )
    
    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
             t_disease.c.entity_name.ilike(keyword_pattern)
        )
        
    if query.parent_id:
        conditions.append(
            t_disease.c.parent_entity_id == query.parent_id
        )
    
    
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_disease).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_disease)
    if query.page_size != -1:
        stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_disease = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_disease,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def find_disease_by_id(conn: Connection, entity_id: str):
    stmt = t_disease.select().where(t_disease.c.entity_id ==entity_id)
    find_disease = conn.execute(stmt).mappings().first()
    return find_disease

def update_disease(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_disease.update().where(t_disease.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add_disease(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_disease.insert().values(data)
    conn.execute(stmt)

def find_disease_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_disease.select().where(t_disease.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_disease = conn.execute(stmt).mappings().all()
    return find_disease

def details_disease_by_id(conn: Connection, entity_id: str):
    stmt = t_disease.select().where(t_disease.c.entity_id == entity_id)
    details_disease = conn.execute(stmt).mappings().first()
    return details_disease

def import_diseases(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
   
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        stmt = t_disease.insert()
        conn.execute(stmt, batch)
        inserted += len(batch)
        print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}

def delete_disease_by_id(conn: Connection, entity_id: str):
    stmt = t_disease.delete().where(t_disease.c.entity_id == entity_id)
    conn.execute(stmt)


def get_parent(tree_number):
    if pd.isna(tree_number):
        return None
    parts = tree_number.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else None

def init(conn: Connection):
    json_data = import_ncbi_mesh.get_json("/ssd1/wy/workspace2/nextflow-fastapi/desc2025.xml")
    df = pd.DataFrame(json_data)
    df_exploded = df.explode(["TreeNumberList"], ignore_index=True)

    df_exploded["ParentTree"] = df_exploded["TreeNumberList"].apply(get_parent)
    df_exploded = df_exploded[pd.notna(df_exploded["TreeNumberList"])]

    df_f03 = df_exploded[df_exploded["TreeNumberList"].str.startswith("F03")]
    df_f03 = df_f03.drop_duplicates(subset=["DescriptorUI"], keep="first")
    df_f03_rename = df_f03[["DescriptorUI","DescriptorName","TreeNumberList","ParentTree"]].rename({
        "DescriptorUI":"mesh_id",
        "DescriptorName":"entity_name",
        "TreeNumberList":"entity_id",
        "ParentTree":"parent_entity_id",
    },axis=1)
    data = json.loads(df_f03_rename.to_json(orient="records"))
    return import_diseases(conn, data)