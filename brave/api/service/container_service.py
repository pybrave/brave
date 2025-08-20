
from brave.api.schemas.container import PageContainerQuery,SaveContainer
from brave.api.models.core import t_container,t_namespace
from sqlalchemy import delete, select, and_, join, func,insert,update
# from brave.api.service.pipeline import get_pipeline_dir 
import json
from brave.api.config.config import get_settings

def page_container(conn,query:PageContainerQuery):
    stmt =select(t_container) 
    
    stmt =select(
        t_container,
        t_namespace.c.name.label("namespace_name")
    ) 
    
    # Left join with t_namespace to get namespace name
    stmt = stmt.select_from(
       t_container.outerjoin(t_namespace, t_container.c.namespace == t_namespace.c.namespace_id)
    )
   
    conditions = []
    # if query.component_type is not None:
    #     conditions.append(t_pipeline_components.c.component_type == query.component_type)
    
    stmt = stmt.where(and_(*conditions))
    count_stmt = select(func.count()).select_from(t_container).where(and_(*conditions))

    stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_container = conn.execute(stmt).mappings().all()
    find_container = [dict(item) for item in find_container]
    # find_container = [format_pipeline_componnet_one() for item in find_container]

    total = conn.execute(count_stmt).scalar()
    return {
        "items": find_container,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }



def find_container_by_id(conn,container_id):
    stmt = t_container.select().where(t_container.c.container_id ==container_id)
    find_container = conn.execute(stmt).mappings().first()
    return find_container


def save_container(conn,saveContainer):
    # str_uuid = str(uuid.uuid4())     
    # saveContainer["container_id"] = str_uuid
    stmt = t_container.insert().values(saveContainer)
    conn.execute(stmt)


def update_container(conn,container_id,updateContainer):
    stmt = t_container.update().where(t_container.c.container_id == container_id).values(updateContainer)
    conn.execute(stmt)

def delete_container(conn,container_id):
    stmt = t_container.delete().where(t_container.c.container_id == container_id)
    conn.execute(stmt)

def list_container(conn): 
    stmt = t_container.select()
    return conn.execute(stmt).mappings().all()
def get_pipeline_dir():
    settings = get_settings()
    return settings.PIPELINE_DIR
def write_all_container(conn,namespace):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    stmt = t_container.select().where(t_container.c.namespace == namespace)
    find_container = conn.execute(stmt).mappings().all()
    find_container = [ {k:v for k,v in item.items() if k!="id" and k!="created_at" and k!="updated_at"} for item in find_container]
    with open(f"{pipeline_dir}/container.json","w") as f:
        json.dump(find_container,f)
     

def import_container(conn,namespace,force=False):
    pipeline_dir = get_pipeline_dir()
    pipeline_dir = f"{pipeline_dir}/{namespace}"
    with open(f"{pipeline_dir}/container.json","r") as f:
        find_container_list = json.load(f)
    for item in find_container_list:
        find_container = find_container_by_id(conn,item['container_id'])
        if find_container:
            if force:
                update_stmt = update(t_container).where(t_container.c.container_id == item['container_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_container).values(item))   