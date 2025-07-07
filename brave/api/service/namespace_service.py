

import json
from turtle import update

from sqlalchemy import insert
from brave.api.models.core import t_namespace
import uuid

from brave.api.service.pipeline import get_pipeline_dir 

def save_namespace(conn,saveNamespace):
    str_uuid = str(uuid.uuid4())     
    saveNamespace["namespace_id"] = str_uuid
    stmt = t_namespace.insert().values(saveNamespace)
    conn.execute(stmt)

def find_namespace(conn,namespace_id):
    stmt = t_namespace.select().where(t_namespace.c.namespace_id == namespace_id)
    return conn.execute(stmt).fetchone()

def update_namespace(conn,namespace_id,updateNamespace):
    stmt = t_namespace.update().where(t_namespace.c.namespace_id == namespace_id).values(updateNamespace)
    conn.execute(stmt)

def delete_namespace(conn,namespace_id):
    stmt = t_namespace.delete().where(t_namespace.c.namespace_id == namespace_id)
    conn.execute(stmt)

def list_namespace(conn): 
    stmt = t_namespace.select()
    return conn.execute(stmt).mappings().all()


def import_namespace(conn,namespace_id,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace_id}"
    with open(f"{pipeline_dir}/namespace.json","r") as f:
        find_namespace = json.load(f)
    if force:
        update_stmt = t_namespace.update().where(t_namespace.c.namespace_id == namespace_id).values(find_namespace)
        conn.execute(update_stmt)
    else:
        conn.execute(insert(t_namespace).values(find_namespace))
    return find_namespace