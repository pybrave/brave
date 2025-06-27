from fastapi import APIRouter
from brave.api.config.db import get_engine
from brave.api.models.core import literature,relation_literature
from brave.api.schemas.literature import Literature,LiteratureQuery
from sqlalchemy import select, and_, join, func,insert,update
from typing import List, Optional, Dict, Any
import json
import glob
import os
from brave.api.config.config import get_settings
literature_api = APIRouter()



@literature_api.post(
    "/literature",
    tags=['literature']
)
async def get_analysis(query: LiteratureQuery) -> Dict[str, Any]:
    with get_engine().begin() as conn:
        offset = (query.page_number - 1) * query.page_size

        if query.obj_key and query.obj_type:
            # JOIN 查询
            j = join(
                literature,
                relation_literature,
                literature.c.literature_key == relation_literature.c.literature_key
            )
            base_stmt = select(literature,relation_literature).select_from(j).where(
                and_(
                    relation_literature.c.obj_key == query.obj_key,
                    relation_literature.c.obj_type == query.obj_type
                )
            )
            count_stmt = select(func.count()).select_from(j).where(
                and_(
                    relation_literature.c.obj_key == query.obj_key,
                    relation_literature.c.obj_type == query.obj_type
                )
            )
        else:
            # 单表查询
            base_stmt = select(literature)
            count_stmt = select(func.count()).select_from(literature)

        # 执行分页
        paged_stmt = base_stmt.offset(offset).limit(query.page_size)
        rows = conn.execute(paged_stmt).mappings().all()
        total = conn.execute(count_stmt).scalar()
        items = [Literature(**row) for row in rows]
        for item in items:
            if item.img:
                item.img = f"/brave-api/literature/dir/{item.img}"
            if item.keywords:
                item.keywords = json.loads(item.keywords)
        return {
            "items":items,
            "total": total,
            "page_number":query.page_number,
            "page_size":query.page_size
        }

def get_literature_one(item):
    with open(item,"r") as f:
        value = json.load(f)
    return value

def add_literature_key(item,literature_key):
    item.update({"literature_key":literature_key})
    return item

def add_or_update_relation_literature(conn,literature_key,literature_relation_data):
    # new_data_list = [add_literature_key(item,literature_key) for item in literature_relation_data]
    for item in literature_relation_data:
        new_data = {
            **item,
            "literature_key":literature_key
        }
        conditation = and_(relation_literature.c.obj_key == item["obj_key"],
                    relation_literature.c.literature_key == literature_key)
        stmt = select(relation_literature).where(conditation)
        result = conn.execute(stmt).fetchone()
        if result:
            update_stmt = (
                update(relation_literature)
                .where(conditation)
                .values(**new_data)
            )
            conn.execute(update_stmt)
        else:
            insert_stmt = insert(relation_literature).values(**new_data)
            conn.execute(insert_stmt)
            
    

@literature_api.post(
    "/literature/import",
    tags=['literature']
)
async def import_literature():
    setting = get_settings()
    literature_dir = setting.LITERATURE_DIR
    literature_file_list = glob.glob(f"{literature_dir}/json/*.json")
    literature_dict = {os.path.basename(item).replace(".json",""):get_literature_one(item) for item in literature_file_list}
    for key,literature_list in literature_dict.items():
        with get_engine().begin() as conn:
            for literatureItem in literature_list:
                new_data = {k: v for k, v in literatureItem.items() if k != "relation"}
                new_data['keywords'] = json.dumps(new_data['keywords'])
                literature_relation_data = literatureItem["relation"]
                add_or_update_relation_literature(conn,literatureItem["literature_key"],literature_relation_data)

                stmt = select(literature.c.literature_key).where(
                    literature.c.literature_key == literatureItem["literature_key"]
                )
                result = conn.execute(stmt).fetchone()
                if result:
                    update_stmt = (
                        update(literature)
                        .where(literature.c.literature_key == literatureItem["literature_key"])
                        .values(**new_data)
                    )
                    conn.execute(update_stmt)
                else:
                    insert_stmt = insert(literature).values(**new_data)
                    conn.execute(insert_stmt)
            