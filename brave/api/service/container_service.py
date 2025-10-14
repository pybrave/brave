
from brave.api.executor.base import JobExecutor
from brave.api.schemas.container import ListContainerQuery, PageContainerQuery,SaveContainer
from brave.api.models.core import t_container
from sqlalchemy import delete, select, and_, join, func,insert,update
# from brave.api.service.pipeline import get_pipeline_dir 
import json

from brave.api.config.config import get_settings

def page_container(conn,query:PageContainerQuery):
    stmt =select(t_container) 
    
    stmt =select(
        t_container
    ) 
    
   
    conditions = []
 
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
    stmt = select(
        t_container
    )
   
    stmt = stmt.where(t_container.c.container_id ==container_id)
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

def import_container(conn,path,force=False):
    # pipeline_dir = get_pipeline_dir()
    with open(f"{path}/container.json","r") as f:
        find_container_list = json.load(f)
    for item in find_container_list:
        find_container = find_container_by_id(conn,item['container_id'])
        if find_container:
            if force:
                update_stmt = update(t_container).where(t_container.c.container_id == item['container_id']).values(item)
                conn.execute(update_stmt)
        else:
            conn.execute(insert(t_container).values(item))   
        



def list_container_key(conn,query:ListContainerQuery):
    stmt = t_container.select().where(
        and_(
            t_container.c.container_key.in_(query.container_key)
        )
        
    )
    return conn.execute(stmt).mappings().all()

def find_container_key(conn,query:ListContainerQuery):
    stmt = t_container.select().where(t_container.c.container_key==query.container_key)
    return conn.execute(stmt).mappings().first()
# def update_images_status(conn,job_executor:JobExecutor ):
#     container_list = list_container()
#     for item in container_list:
#         image = job_executor.get_image(item.image)
#         pass



def find_by_container_ids(conn,container_ids):
    if not container_ids:
        return []
    stmt = t_container.select().where(t_container.c.container_id.in_(container_ids))
    return conn.execute(stmt).mappings().all()


