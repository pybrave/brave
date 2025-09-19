
import json
from operator import and_, or_

import pandas as pd
from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_mesh,t_mesh_tree    
from sqlalchemy import select,func
from sqlalchemy.engine import Connection
from sqlalchemy import select,func,insert,case,exists

from brave.microbe.utils import import_ncbi_mesh



def page(conn: Connection, query: PageEntity):
    child = t_mesh_tree.alias("child")
    stmt =select(
        t_mesh,
        func.any_value(t_mesh_tree.c.parent_tree).label("parent_tree"),
        func.any_value(t_mesh_tree.c.tree_number).label("tree_number"),
        func.any_value(case(
                (exists().where(child.c.parent_tree == t_mesh_tree.c.tree_number), True),
                else_=False
        )).label("has_children"),
        # t_mesh_tree.c.parent_tree.label("parent_tree"),
        # t_mesh_tree.c.tree_number.label("tree_number"),
    )

    if query.parent_id and query.parent_id=="default":
        query.parent_id = query.category
        
    stmt = stmt.select_from(
        t_mesh.outerjoin(t_mesh_tree,t_mesh.c.entity_id==t_mesh_tree.c.entity_id)
            )

    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
             t_mesh.c.entity_name.ilike(keyword_pattern)
        )
    if query.category:
        conditions.append(
             t_mesh_tree.c.category == query.category
        )
    if query.major_category:
        conditions.append(
             t_mesh_tree.c.major_category == query.major_category
        )
    if query.parent_id:
        conditions.append(
             t_mesh_tree.c.parent_tree == query.parent_id
        )
    
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count( func.distinct(t_mesh.c.entity_id) )).select_from(t_mesh.outerjoin(t_mesh_tree,t_mesh.c.entity_id==t_mesh_tree.c.entity_id)).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_mesh)
    
    stmt = stmt.group_by(t_mesh.c.entity_id)

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

def find_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.select().where(t_mesh.c.entity_id ==entity_id)
    find_disease = conn.execute(stmt).mappings().first()
    return find_disease

def update(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_mesh.update().where(t_mesh.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_mesh.insert().values(data)
    conn.execute(stmt)

def find_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_mesh.select().where(t_mesh.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_disease = conn.execute(stmt).mappings().all()
    return find_disease

def details_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.select().where(t_mesh.c.entity_id == entity_id)
    details_disease = conn.execute(stmt).mappings().first()
    return details_disease

def imports(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        stmt = t_mesh.insert()
        conn.execute(stmt, batch)
        inserted += len(batch)
        print(f"Inserted {inserted} records...")

    return {"message imports mesh": f"导入完成，共导入 {inserted} 行"}

def delete_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.delete().where(t_mesh.c.entity_id == entity_id)
    conn.execute(stmt)


def get_parent(tree_number):
    if pd.isna(tree_number):
        return None
    parts = tree_number.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else None

def imports_tree(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        stmt = t_mesh_tree.insert()
        conn.execute(stmt, batch)
        inserted += len(batch)
        print(f"Inserted {inserted} records...")

    return {"message imports_tree": f"导入完成，共导入 {inserted} 行"}


def init(conn: Connection):
    json_data = import_ncbi_mesh.get_json("/ssd1/wy/workspace2/nextflow-fastapi/desc2025.xml")
    df = pd.DataFrame(json_data)
    df_exploded = df.explode(["TreeNumberList"], ignore_index=True)

    df_exploded["ParentTree"] = df_exploded["TreeNumberList"].apply(get_parent)
    df_exploded_rename = df_exploded[["DescriptorUI","DescriptorName","TreeNumberList","ParentTree"]].rename({
            "DescriptorUI":"entity_id",
            "DescriptorName":"entity_name",
            "TreeNumberList":"tree_number",
            "ParentTree":"parent_tree",
        },axis=1)
    df_exploded_rename["category"]  = df_exploded_rename["tree_number"].apply(lambda x: str(x).split(".")[0])
    df_exploded_rename["major_category"]  = df_exploded_rename["tree_number"].apply(lambda x: str(x).split(".")[0][0])
    df_exploded_rename_node = df_exploded_rename[["entity_id","entity_name"]].drop_duplicates( keep="first")
    # df_exploded_rename_node["entity_id"] = df_exploded_rename_node.apply(lambda x: uuid(),axis=1)
    data = json.loads(df_exploded_rename_node.to_json(orient="records"))
    imports(conn, data)
    df_exploded_rename_tree = df_exploded_rename[["entity_id","tree_number","parent_tree","category","major_category"]].drop_duplicates( keep="first")
    data_tree = json.loads(df_exploded_rename_tree.to_json(orient="records"))
    imports_tree(conn, data_tree)
    return "success"