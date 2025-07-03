from brave.api.config.db import get_engine
from brave.api.models.core import t_bio_database
from brave.api.schemas.bio_database import QueryBiodatabase
from sqlalchemy import select

def list_bio_database(conn,query: QueryBiodatabase):
    condition = []
    if query.database_id:
        condition.append(t_bio_database.c.database_id == query.database_id)
    elif query.type:
        condition.append(t_bio_database.c.type == query.type)
    elif query.name:
        condition.append(t_bio_database.c.name == query.name)
    elif query.path:
        condition.append(t_bio_database.c.path == query.path)
    elif query.type_list:
        condition.append(t_bio_database.c.type.in_(query.type_list))


    stmt = select(t_bio_database).where(*condition)
    result = conn.execute(stmt).mappings().all()
    return result


def get_bio_database_by_id(conn,database_id: str):
    stmt = select(t_bio_database).where(t_bio_database.c.database_id == database_id)
    result = conn.execute(stmt).mappings().first()
    return result
