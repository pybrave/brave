

from operator import and_, or_
from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_taxonomy
from sqlalchemy import select,func,insert,case,exists
from brave.microbe.utils.import_ncbi_taxonomy import merge_all

from sqlalchemy.engine import Connection

def page_taxonomy(conn: Connection, query: PageEntity):
    stmt =select(
        t_taxonomy,
    ) 
    
    # Left join with t_namespace to get namespace name
    # stmt = stmt.select_from(
    #    t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    # )

    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
            # or_(
               
            # )
             t_taxonomy.c.scientific_name.ilike(keyword_pattern)
        )
    
    if query.parent_id:
        conditions.append(
            t_taxonomy.c.parent_tax_id == query.parent_id
        )
    

    # stmt = stmt.where(and_(*conditions))
    # count_stmt = select(func.count()).select_from(t_taxonomy).where(and_(*conditions))
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_taxonomy).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_taxonomy)

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_taxonomy = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_taxonomy,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def page_taxonomy_v2(conn: Connection, query: PageEntity):
    child = t_taxonomy.alias("child")

    stmt = (
        select(
            t_taxonomy,
            func.count(child.c.tax_id).label("child_count")
        )
        .select_from(
            t_taxonomy.outerjoin(child, t_taxonomy.c.tax_id == child.c.parent_tax_id)
        )
        .group_by(t_taxonomy.c.tax_id)
    )
    # Left join with t_namespace to get namespace name
    # stmt = stmt.select_from(
    #    t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    # )

    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
            # or_(
               
            # )
             t_taxonomy.c.scientific_name.ilike(keyword_pattern)
        )
    
    if query.parent_id:
        conditions.append(
            t_taxonomy.c.parent_tax_id == query.parent_id
        )
    

    # stmt = stmt.where(and_(*conditions))
    # count_stmt = select(func.count()).select_from(t_taxonomy).where(and_(*conditions))
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_taxonomy).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_taxonomy)

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_taxonomy = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_taxonomy,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def page_taxonomy_v3(conn: Connection, query: PageEntity):
    child = t_taxonomy.alias("child")
    if query.parent_id and query.parent_id=="default":
        query.parent_id = 1
    stmt = (
        select(
            t_taxonomy,
            case(
                (exists().where(child.c.parent_tax_id == t_taxonomy.c.tax_id), True),
                else_=False
            ).label("has_children")
        )
    )
    # Left join with t_namespace to get namespace name
    # stmt = stmt.select_from(
    #    t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    # )

    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
            # or_(
               
            # )
             t_taxonomy.c.scientific_name.ilike(keyword_pattern)
        )
    
    if query.parent_id:
        conditions.append(
            t_taxonomy.c.parent_tax_id == query.parent_id
        )
    

    # stmt = stmt.where(and_(*conditions))
    # count_stmt = select(func.count()).select_from(t_taxonomy).where(and_(*conditions))
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_taxonomy).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_taxonomy)
    if query.page_size != -1:
        stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_taxonomy = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_taxonomy,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }



def find_taxonomy_by_id(conn: Connection, entity_id: str):
    stmt = t_taxonomy.select().where(t_taxonomy.c.entity_id ==entity_id)
    find_taxonomy = conn.execute(stmt).mappings().first()
    return find_taxonomy

def update_taxonomy(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_taxonomy.update().where(t_taxonomy.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add_taxonomy(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_taxonomy.insert().values(data)
    conn.execute(stmt)

def find_taxonomy_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_taxonomy.select().where(t_taxonomy.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_taxonomy = conn.execute(stmt).mappings().all()
    return find_taxonomy


def details_taxonomy_by_id(conn: Connection, entity_id: str):
    stmt = t_taxonomy.select().where(t_taxonomy.c.entity_id ==entity_id)
    find_taxonomy = conn.execute(stmt).mappings().first()
    lineage = get_lineage(find_taxonomy.tax_id, conn)
    find_taxonomy = dict(find_taxonomy)
    find_taxonomy['lineage'] = build_lineage_chain(lineage, find_taxonomy['tax_id'])
    
    return find_taxonomy


def build_lineage_chain(result, target_tax_id):
    # 1. 建立 tax_id -> node 映射
    tax_map = {row.tax_id: row for row in result}

    # 2. 从目标 tax_id 开始向上查
    lineage = []
    current_id = target_tax_id

    while current_id in tax_map:
        node = tax_map[current_id]
        lineage.append({
            "tax_id": node.tax_id,
            "parent_tax_id": node.parent_tax_id,
            "entity_name": node.entity_name,
            "rank": node.rank
        })
        # parent_tax_id = 1 停止
        if node.parent_tax_id == 1:
            break
        current_id = node.parent_tax_id

    # 3. 反转顺序：root -> 当前节点
    lineage.reverse()
    return lineage

def get_lineage(tax_id: int, conn):
    taxonomy = t_taxonomy.alias()

    # 递归 CTE
    lineage = (
        select(
            taxonomy.c.tax_id,
            taxonomy.c.parent_tax_id,
            taxonomy.c.entity_name,
            taxonomy.c.rank
        )
        .where(taxonomy.c.tax_id == tax_id)
        .cte(name="lineage", recursive=True)
    )

    parent = taxonomy.alias("parent")
    lineage = lineage.union_all(
        select(
            parent.c.tax_id,
            parent.c.parent_tax_id,
            parent.c.entity_name,
            parent.c.rank
        ).where(
            (parent.c.tax_id == lineage.c.parent_tax_id) &
            (lineage.c.parent_tax_id != 1)  # parent_tax_id = 1 停止递归
        )
    )

    stmt = select(lineage).order_by(lineage.c.tax_id)
    result = conn.execute(stmt).fetchall()
    return result


def import_taxonomy(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        stmt = insert(t_taxonomy)
        conn.execute(stmt, batch)
        inserted += len(batch)
        print(f"Inserted {inserted} records...")
    return inserted

def delete_taxonomy_by_id(conn: Connection, entity_id: str):
    stmt = t_taxonomy.delete().where(t_taxonomy.c.entity_id == entity_id)
    conn.execute(stmt)


def  init(conn: Connection):
    with open("brave/microbe/data/taxonomy.sql", "r") as f:
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
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            stmt = insert(t_taxonomy)
            conn.execute(stmt, batch)
            inserted += len(batch)
            print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}
