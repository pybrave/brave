
import uuid

from brave.api.schemas.store import CreateStore
from brave.api.models.core import t_store
from sqlalchemy import select

from brave.api.config.db import get_engine

def create_store(conn, createStore:CreateStore):
    store_data = createStore.dict(exclude_none=True)
    store_id = store_data.get("store_id") or str(uuid.uuid4())
    store_data["store_id"] = store_id
    stmt = t_store.insert().values(**store_data)
    conn.execute(stmt)
    return store_id

def update_store(conn,store_id,updateStore:CreateStore):
    update_data = updateStore.dict(exclude_none=True)
    update_data.pop("store_id", None)
    if not update_data:
        return
    stmt = t_store.update().where(t_store.c.store_id == store_id).values(**update_data)
    conn.execute(stmt)

def save_store(conn,createStore:CreateStore):
    if createStore.store_id:
        update_store(conn,createStore.store_id,createStore)
    else:
        create_store(conn,createStore)

def find_store_by_id(conn,store_id):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.store_id ==store_id)
    find_store = conn.execute(stmt).mappings().first()
    return find_store

def list_store(conn):
    stmt =select(t_store) 
    find_store = conn.execute(stmt).mappings().all()
    find_store = [dict(item) for item in find_store]
    return find_store

def delete_store(conn,store_id):
    stmt = t_store.delete().where(t_store.c.store_id == store_id)
    conn.execute(stmt)


def find_store_by_url(conn,url):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.url ==url)
    find_store = conn.execute(stmt).mappings().first()
    return find_store


def  update_store_status(store_id,status):
    with get_engine().connect() as conn:
        stmt = t_store.update().where(t_store.c.store_id == store_id).values(status=status)
        conn.execute(stmt)