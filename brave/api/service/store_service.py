
import os
import shutil
import uuid

from brave.api.config.config import get_settings
from brave.api.schemas.store import CreateStore, PageStoreQuery, StoreQuery
from brave.api.models.core import t_store,t_pipeline_components_relation
from sqlalchemy import and_, func, select
from brave.api.utils import git_utils

from brave.api.config.db import get_engine

def create_store(conn, store_data:dict):
    # store_data = createStore.dict(exclude_none=True)
    store_id = store_data.get("store_id") or str(uuid.uuid4())
    store_data["store_id"] = store_id
    stmt = t_store.insert().values(**store_data)
    conn.execute(stmt)
    return store_id

    # update_data = updateStore.dict(exclude_none=True)
def update_store(conn,store_id,update_data:dict):
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


def find_store_by_app_id(conn,app_id):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.app_id ==app_id)
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

def format_store(store):
    if store["img"] is None:
        store['img'] = f"/brave-api/img/pipeline.jpg"
    return store

def page_store(conn, query: PageStoreQuery):
    conditions = []

    if query.url:
        conditions.append(t_store.c.url == query.url)
    if query.name:
        conditions.append(t_store.c.name == query.name)
    if query.status:
        conditions.append(t_store.c.status == query.status)
    if query.category:
        conditions.append(t_store.c.category == query.category)
    if query.store_id:
        conditions.append(t_store.c.store_id == query.store_id)
    if query.app_id:
        conditions.append(t_store.c.app_id == query.app_id)
    if query.keywords:
        keyword_condition = (t_store.c.name.ilike(f"%{query.keywords}%")) | (t_store.c.url.ilike(f"%{query.keywords}%"))
        conditions.append(keyword_condition)

    stmt = select(
        t_store,
        t_pipeline_components_relation.c.relation_id.label("tool_id")
    )
    stmt = stmt.select_from(t_store.outerjoin(
        t_pipeline_components_relation,
        t_pipeline_components_relation.c.relation_id == t_store.c.app_id
    ))

    stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    stmt = stmt.order_by(t_store.c.id.desc())
    items = conn.execute(stmt).mappings().all()
    items = [format_store(dict(item)) for item in items]

    count_stmt = select(func.count()).select_from(t_store).where(and_(*conditions))
    total = conn.execute(count_stmt).scalar()

    return {
        "items": items,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }
    

def delete_store(conn,store_id):
    find_store = find_store_by_id(conn,store_id)
    if not find_store:
        raise Exception(f"Store with id {store_id} not found")
    store_path = find_store.get("path")
    if store_path and os.path.exists(store_path):
        shutil.rmtree(store_path)
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

def build_store_data(app_id,name,img,category,tags,version,update_info,status="done"):
    store_data = {
        # **createStore.dict(exclude_none=True),
        "name":name,
        "img": img,
        "category": category,
        "tags": tags,
        "version": version,
        "update_info": update_info,
        "status": status,
        "app_id": app_id
    }
    return store_data



def create_or_update_store(url,app_id,name,img,category,tags,version,update_info):
    path_name, filename = git_utils.get_path_name_from_url(url)
    publish_urls = git_utils.build_publish_urls(path_name)
    settings = get_settings()
    store_path = f"{settings.STORE_DIR}"
    store_path = f"{store_path}/{path_name}"
    if not os.path.exists(store_path):
        os.makedirs(store_path)
        print(f"Created directory at {store_path}")
    tools_img =None
    if img:
        if "/" in img:
            filename = img.split("/")[-1]
            tools_img = f"/brave-api/store-dir/{path_name}/tools/{filename}"

    store_data_ = build_store_data(app_id,name,tools_img,category,tags,version,update_info)
    store_data = {
        # **createStore.dict(exclude_none=True),
        "url": url,
        "path": store_path,
        "path_name": path_name,
        "publish_urls": publish_urls,
        "origin":"local",
        **store_data_
       
    }
    return store_data


def find_list_in_urls(conn, urls):
    stmt = select(
        t_store
    )
   
    stmt = stmt.where(t_store.c.url.in_(urls))
    find_store = conn.execute(stmt).mappings().all()
    return find_store