

import json
from turtle import update

from sqlalchemy import insert
from brave.api.models.core import t_context
import uuid

from brave.api.service.pipeline import get_pipeline_dir 

def save_context(conn,saveContext):
    str_uuid = str(uuid.uuid4())     
    saveContext["context_id"] = str_uuid
    stmt = t_context.insert().values(saveContext)
    conn.execute(stmt)

def find_context(conn,context_id):
    stmt = t_context.select().where(t_context.c.context_id == context_id)
    return conn.execute(stmt).fetchone()

def update_context(conn,context_id,updateContext):
    stmt = t_context.update().where(t_context.c.context_id == context_id).values(updateContext)
    conn.execute(stmt)

def delete_context(conn,context_id):
    stmt = t_context.delete().where(t_context.c.context_id == context_id)
    conn.execute(stmt)

def list_context_by_type(conn,type): 
    stmt = t_context.select().where(t_context.c.type == type)
    return conn.execute(stmt).mappings().all()


def import_context(conn,context_id,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{context_id}"
    with open(f"{pipeline_dir}/namespace.json","r") as f:
        find_context = json.load(f)
    # for item in find_context:
    if force:
        update_stmt = t_context.update().where(t_context.c.context_id == item['context_id']).values(find_context)
        conn.execute(update_stmt)
    else:
        conn.execute(insert(t_context).values(find_context))
    return find_context