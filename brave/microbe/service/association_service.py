
from operator import and_, or_

from shortuuid import uuid
from brave.microbe.schemas.entity import PageEntity
from brave.microbe.models.core import t_association,t_mesh,t_study
from sqlalchemy import select,func
from sqlalchemy.engine import Connection
from brave.microbe.service import graph_service
from brave.microbe.service import mesh_service,study_service


def page(conn: Connection, query: PageEntity):
    mesh_subject = t_mesh.alias("mesh_subject")
    mesh_object = t_mesh.alias("mesh_object")
    mesh_observed = t_mesh.alias("mesh_observed")
    mesh_study = t_mesh.alias("mesh_study")
    association = t_association.alias("assoc")  # 关系表

    stmt = (
        select(
            association,
            mesh_subject.c.entity_name.label("subject_name"),
            mesh_object.c.entity_name.label("object_name"),
            mesh_observed.c.entity_name.label("observed_name"),
            mesh_study.c.entity_name.label("study_name")
        )
        .select_from(association)
        .outerjoin(mesh_subject, mesh_subject.c.entity_id == association.c.subject_id)
        .outerjoin(mesh_object, mesh_object.c.entity_id == association.c.object_id)
        .outerjoin(mesh_observed, mesh_observed.c.entity_id == association.c.observed_id)  # 正确字段
        .outerjoin(mesh_study, mesh_study.c.entity_id == association.c.study_id)
    )
    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
             t_association.c.entity_name.ilike(keyword_pattern)
        )
    
    
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count()).select_from(t_association).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_association)
    if query.page_size != -1:
        stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    stmt = stmt.order_by(association.c.id.desc())
    result  = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    formatted_result = []
    for row in result:
        new_row = dict(row)  # 转成普通字典
        for field in ["created_at", "updated_at"]:
            if field in new_row and new_row[field]:
                new_row[field] = new_row[field].strftime("%Y-%m-%d %H:%M:%S")
        formatted_result.append(new_row)

    return {
        "items": formatted_result ,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def find_by_id(conn: Connection, entity_id: str):
    stmt = t_association.select().where(t_association.c.entity_id ==entity_id)
    find_disease = conn.execute(stmt).mappings().first()
    return find_disease

def update(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_association.update().where(t_association.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_association.insert().values(data)
    conn.execute(stmt)
    return data['entity_id']
    # for item in data.items():
    #     print(item)
    #     pass
    # graph_service.create_node_relation()
    


def find_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_association.select().where(t_association.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_disease = conn.execute(stmt).mappings().all()
    return find_disease

def details_by_id(conn: Connection, entity_id: str):
    stmt = t_association.select().where(t_association.c.entity_id == entity_id)
    details_disease = conn.execute(stmt).mappings().first()
    return details_disease

def imports(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    with conn.begin():  # type: Connection
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            stmt = t_association.insert()
            conn.execute(stmt, batch)
            inserted += len(batch)
            print(f"Inserted {inserted} records...")

    return {"message": f"导入完成，共导入 {inserted} 行"}

def delete_by_id(conn: Connection, entity_id: str):
    stmt = t_association.delete().where(t_association.c.entity_id == entity_id)
    conn.execute(stmt)


def get_entity(conn: Connection,association:dict):
    subject_id = association.get("subject_id") 
    object_id = association.get("object_id") 
    observed_id = association.get("observed_id")
    predicate = association.get("predicate") 
    study_id = association.get("study_id") 
    

    subject = mesh_service.find_by_id(conn,subject_id)


    object = mesh_service.find_by_id(conn,object_id)
    
    observed = mesh_service.find_by_id(conn,observed_id)

    study = study_service.find_study_by_id(conn,study_id)


    entity = {
        "subject":subject,
        "object":object,
    }
    relationship = {
        "predicate": predicate,
        "association_id": association.get("entity_id"), 
        "effect": association.get("effect"),
        "study":study.get("entity_id"),
        "study_name":study.get("entity_name"),
        "observed_id":observed.get("entity_id"),
        "observed_name":observed.get("entity_name")
    }



    # result.update({"association":association})
    
    return entity,relationship
