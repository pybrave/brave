
import uuid

from brave.api.schemas.store import CreateStore, StoreQuery
from brave.api.models.core import t_store
from sqlalchemy import select

from brave.api.config.db import get_engine

def create_store(conn, store_data:dict):
    # store_data = createStore.dict(exclude_none=True)
    store_id = store_data.get("store_id") or str(uuid.uuid4())
    store_data["store_id"] = store_id
    stmt = t_store.insert().values(**store_data)
    conn.execute(stmt)
    return store_id

def update_store(conn,store_id,update_data:dict):
    # update_data = updateStore.dict(exclude_none=True)
    update_data = {k: v for k, v in update_data.items() if v is not None}
    update_data.pop("store_id", None)
    if not update_data:
        return
    stmt = t_store.update().where(t_store.c.store_id == store_id).values(**update_data)
    conn.execute(stmt)


def find_store_by_id(conn,store_id):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.store_id ==store_id)
    find_store = conn.execute(stmt).mappings().first()
    return find_store

def update_store_version(conn, store_id, version):
    stmt = t_store.update().where(t_store.c.store_id == store_id).values(version=version)
    conn.execute(stmt)

def find_by_path_name(conn,path_name):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.path_name ==path_name)
    find_store = conn.execute(stmt).mappings().first()
    return find_store

def list_store(conn, query: StoreQuery):
    stmt =select(t_store) 
    if query:
        if query.store_id:
            stmt = stmt.where(t_store.c.store_id == query.store_id)
        if query.url:
            stmt = stmt.where(t_store.c.url == query.url)
        if query.name:
            stmt = stmt.where(t_store.c.name == query.name)
        if query.status:
            stmt = stmt.where(t_store.c.status == query.status)
        if query.path_name:
            stmt = stmt.where(t_store.c.path_name == query.path_name)
        if query.category:
            stmt = stmt.where(t_store.c.category == query.category)
            
    find_store = conn.execute(stmt).mappings().all()
    find_store = [dict(item) for item in find_store]
    return find_store

def delete_store(conn,store_id):
    stmt = t_store.delete().where(t_store.c.store_id == store_id)
    conn.execute(stmt)

def delete_store_db(store_id):
    with get_engine().begin() as conn:
        delete_store(conn,store_id)

def find_store_by_url(conn,url):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.url ==url)
    find_store = conn.execute(stmt).mappings().first()
    return find_store

def update_store_status(conn, store_id,status,category=None):
    update_data = {"status": status}
    if category is not None:
        update_data["category"] = category
    stmt = t_store.update().where(t_store.c.store_id == store_id).values(**update_data)
    conn.execute(stmt)

def  update_store_status_db(store_id,status,category=None):
    with get_engine().begin() as conn:
        update_store_status(conn, store_id,status,category)
    
def  update_store_db(store_id,update_data:dict):
    with get_engine().begin() as conn:
        update_store(conn, store_id, update_data)