
from operator import and_, or_

from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_diet_and_food
from sqlalchemy import select,func
from sqlalchemy.engine import Connection



def page(conn: Connection, query: PageEntity):
    stmt =select(
        t_diet_and_food,
    ) 
    
    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
             t_diet_and_food.c.entity_name.ilike(keyword_pattern)
        )
    
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_diet_and_food).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_diet_and_food)
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
    stmt = t_diet_and_food.select().where(t_diet_and_food.c.entity_id ==entity_id)
    find_disease = conn.execute(stmt).mappings().first()
    return find_disease

def update(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_diet_and_food.update().where(t_diet_and_food.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_diet_and_food.insert().values(data)
    conn.execute(stmt)

def find_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_diet_and_food.select().where(t_diet_and_food.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_disease = conn.execute(stmt).mappings().all()
    return find_disease

def details_by_id(conn: Connection, entity_id: str):
    stmt = t_diet_and_food.select().where(t_diet_and_food.c.entity_id == entity_id)
    details_disease = conn.execute(stmt).mappings().first()
    return details_disease

def imports(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    with conn.begin():  # type: Connection
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            stmt = t_diet_and_food.insert()
            conn.execute(stmt, batch)
            inserted += len(batch)
            print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}

def delete_by_id(conn: Connection, entity_id: str):
    stmt = t_diet_and_food.delete().where(t_diet_and_food.c.entity_id == entity_id)
    conn.execute(stmt)