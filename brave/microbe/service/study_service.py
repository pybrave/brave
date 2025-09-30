

from operator import and_, or_

from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_study
from sqlalchemy import select,func
from sqlalchemy.engine import Connection
from brave.microbe.service import graph_service

def page_study(conn: Connection, query: PageEntity):
    stmt =select(
        t_study,
    ) 
    
    # Left join with t_namespace to get namespace name
    # stmt = stmt.select_from(
    #    t_pipeline_components.outerjoin(t_namespace, t_pipeline_components.c.namespace == t_namespace.c.namespace_id)
    # )

    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
            or_(
                t_study.c.study_id.ilike(keyword_pattern),
                t_study.c.study_name.ilike(keyword_pattern),
                t_study.c.description.ilike(keyword_pattern)
            )
        )
    

    # stmt = stmt.where(and_(*conditions))
    # count_stmt = select(func.count()).select_from(t_taxonomy).where(and_(*conditions))
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_study).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_study)
    if query.page_size != -1:
        stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_study = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_study,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def find_study_by_id(conn: Connection, entity_id: str):
    stmt = t_study.select().where(t_study.c.entity_id ==entity_id)
    find_study = conn.execute(stmt).mappings().first()
    return find_study

def update_study(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_study.update().where(t_study.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)  


def add_study(conn: Connection, data: dict):
    data['entity_id'] =uuid()
    stmt = t_study.insert().values(data)
    conn.execute(stmt)


def find_study_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_study.select().where(
        t_study.c.entity_name.ilike(keyword_pattern),
        # or_(
        #     t_study.c.entity_name.ilike(keyword_pattern),
        #     t_study.c.study_name.ilike(keyword_pattern),
        #     t_study.c.description.ilike(keyword_pattern)
        # )
    ).limit(10)
    find_study = conn.execute(stmt).mappings().all()
    find_study = [
        {k:v for k,v in item.items() if v is not None}
        for item in find_study 
    ]
    return find_study

def details_study_by_id(conn: Connection, entity_id: str):  
    stmt = t_study.select().where(t_study.c.entity_id == entity_id)
    details_study = conn.execute(stmt).mappings().first()
    return details_study


def import_studies(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    # with conn.begin():  # type: Connection
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        for item in batch:
            item['entity_id'] = uuid()
        stmt = t_study.insert()
        conn.execute(stmt, batch)
        inserted += len(batch)
        print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}

def delete_study_by_id(conn: Connection, entity_id: str):
    stmt = t_study.delete().where(t_study.c.entity_id == entity_id)
    conn.execute(stmt)


def mining_study(conn: Connection, entity_id: str):
    stmt = t_study.select().where(t_study.c.entity_id ==entity_id)
    find_study = conn.execute(stmt).mappings().first()
    return find_study