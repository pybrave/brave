
import json
# from operator import and_, or_
from sqlalchemy import and_,or_

import pandas as pd
from shortuuid import uuid
from brave.microbe.schemas.entity import AddMeshNode, PageEntity
from brave.microbe.models.core import t_mesh,t_mesh_tree,t_registry_numbers,t_taxonomy
from sqlalchemy import select,func
from sqlalchemy.engine import Connection
from sqlalchemy import select,func,insert,case,exists

from brave.microbe.utils import import_ncbi_mesh
from brave.microbe.utils import import_kegg
from sqlalchemy.dialects.mysql import insert as mysql_insert



def page(conn: Connection, query: PageEntity):
    
    child = t_mesh_tree.alias("child")
    select_list = [
            t_mesh.c.entity_id,
         
            func.any_value(t_mesh.c.is_research).label("is_research"),
            func.any_value(t_mesh.c.entity_type).label("entity_type"),

            func.any_value(t_mesh.c.tags).label("tags"),
            func.any_value(t_mesh.c.short_name).label("short_name"),

            # func.any_value(t_mesh.c.describe).label("describe"),
            func.group_concat(func.distinct(t_mesh_tree.c.parent_tree)).label("parent_trees"),
            func.any_value(t_mesh_tree.c.tree_number).label("tree_number"),
            func.any_value(case(
                    (exists().where(child.c.parent_tree == t_mesh_tree.c.tree_number), True),
                    else_=False
            )).label("has_children"),
    ]
    if query.locale and query.locale=="zh_CN":
        select_list.extend([
            func.any_value(t_mesh.c.entity_name).label("entity_name_en"),
            func.any_value(
                func.coalesce(
                    func.nullif(t_mesh.c.entity_name_zh, ''),  # 如果 entity_name_zh = '' → NULL
                    t_mesh.c.entity_name                       # 如果为 NULL 或空 → 用 entity_name
                )
            ).label("entity_name"),
        ])
        # stmt =select(
           
        #     # t_mesh_tree.c.parent_tree.label("parent_tree"),
        #     # t_mesh_tree.c.tree_number.label("tree_number"),
        # )

    else:    
        select_list.extend([
            func.any_value(t_mesh.c.entity_name).label("entity_name")
        ])
    stmt =select(*select_list)
    
    # stmt = stmt.with_only_columns(select_list)

    if query.registry_join:
        if  query.registry_join=="taxonomy":
            stmt = select(*select_list,
            func.group_concat(func.distinct(t_taxonomy.c.entity_name)).label("taxonomy_name"),
            func.group_concat(func.distinct(t_taxonomy.c.rank)).label("rank"),
            func.group_concat(func.distinct(t_taxonomy.c.tax_id)).label("tax_id"),
                          )
        
            stmt = stmt.outerjoin(t_registry_numbers, t_mesh.c.entity_id == t_registry_numbers.c.entity_id)
            stmt = stmt.outerjoin(t_taxonomy, t_registry_numbers.c.registry_number == t_taxonomy.c.entity_id)


    if query.parent_id and query.parent_id=="default":
        query.parent_id = query.category
        
    stmt = stmt.select_from(
        t_mesh.outerjoin(t_mesh_tree,t_mesh.c.entity_id==t_mesh_tree.c.entity_id)
            )
  
    conditions = []
  
    if query.keywords:
        keyword_pattern = f"%{query.keywords.strip()}%"
        conditions.append(
             t_mesh.c.entity_name.ilike(keyword_pattern)
        )
    if query.category:
        if type (query.category) is str:
            conditions.append(
                t_mesh_tree.c.category == query.category
            )
        elif type (query.category) is list:
            conditions.append(
                t_mesh_tree.c.category.in_(query.category)
            )
    # if query.major_category:
    #     conditions.append(
    #          t_mesh_tree.c.major_category == query.major_category
    #     )
    if query.parent_id:
        if type (query.parent_id) is str:
            conditions.append(
                t_mesh_tree.c.parent_tree == query.parent_id
            )
        elif type (query.parent_id) is list:
            conditions.append(
                t_mesh_tree.c.tree_number.in_(query.parent_id)
        
            )
    if query.is_research is not None and query.is_research is True:
        conditions.append(
             t_mesh.c.is_research == query.is_research
        )   
    
    if conditions:  # 只有有条件时才加 where
        conditions = and_(*conditions) if len(conditions) > 1 else conditions[0]
        stmt = stmt.where(conditions)
        count_stmt = select(func.count( func.distinct(t_mesh.c.entity_id) )).select_from(t_mesh.outerjoin(t_mesh_tree,t_mesh.c.entity_id==t_mesh_tree.c.entity_id)).where(conditions)
    else:
        count_stmt = select(func.count()).select_from(t_mesh)
    
    stmt = stmt.group_by(t_mesh.c.entity_id)

    if query.page_size != -1:
        stmt = stmt.offset((query.page_number - 1) * query.page_size).limit(query.page_size)
    find_disease = conn.execute(stmt).mappings().all()
    total = conn.execute(count_stmt).scalar()

    return {
        "items": find_disease,
        "total":total,
        "page_number":query.page_number,
        "page_size":query.page_size
    }

def get_parents(conn, entity_id: str):
    # 获取该 entity_id 对应的所有 tree_number
    tree_numbers = conn.execute(
        select(t_mesh_tree.c.tree_number).where(t_mesh_tree.c.entity_id == entity_id)
    ).scalars().all()
    
    if not tree_numbers:
        return []
    
    # 生成所有父前缀
    parent_prefixes = []
    for tn in tree_numbers:
        parent_prefixes.extend(tree_numbers)
        parts = tn.split(".")
        parent_prefixes.extend([".".join(parts[:i]) for i in range(1, len(parts))])
    parent_prefixes = list(set(parent_prefixes))
    
    if not parent_prefixes:
        return []
    
    # 查询所有父节点
    stmt_parents = (
        select(t_mesh.c.entity_name, t_mesh_tree.c.entity_id, t_mesh_tree.c.tree_number, t_mesh_tree.c.parent_tree)
        .select_from(t_mesh_tree.outerjoin(t_mesh, t_mesh.c.entity_id == t_mesh_tree.c.entity_id))
        .where(t_mesh_tree.c.tree_number.in_(parent_prefixes))
        .order_by(t_mesh_tree.c.tree_number)
    )
    all_nodes = conn.execute(stmt_parents).mappings().all()
    if not all_nodes:
        return []

    # 4. 构建字典: tree_number -> 节点
    nodes_dict = {node['tree_number']: dict(node) for node in all_nodes}
    # 初始化 children 列表
    for node in nodes_dict.values():
        node['children'] = []

    # 5. 构建树结构
    tree_roots = []
    for tn, node in nodes_dict.items():
        parent_tn = node['parent_tree']
        if parent_tn and parent_tn in nodes_dict:
            nodes_dict[parent_tn]['children'].append(node)
        else:
            tree_roots.append(node)  # 根节点

    return tree_roots
def find_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.select().where(t_mesh.c.entity_id ==entity_id)
    find_disease = conn.execute(stmt).mappings().first()
    parents  = get_parents(conn, entity_id)
    find_disease = dict(find_disease) if find_disease else {}
    find_disease["parents"] = parents
    return find_disease



def update(conn: Connection, entity_id: str, updateData: dict):
    stmt = t_mesh.update().where(t_mesh.c.entity_id == entity_id).values(updateData)
    conn.execute(stmt)

def add(conn: Connection, data: dict):
    data['entity_id'] = str(uuid())
    stmt = t_mesh.insert().values(data)
    conn.execute(stmt)

def find_by_keywords(conn: Connection, keywords: str):
    keyword_pattern = f"%{keywords.strip()}%"
    stmt = t_mesh.select().where(t_mesh.c.entity_name.ilike(keyword_pattern)).limit(10)
    find_disease = conn.execute(stmt).mappings().all()
    return find_disease

def details_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.select().where(t_mesh.c.entity_id == entity_id)
    details_disease = conn.execute(stmt).mappings().first()
    return details_disease

# def imports(conn: Connection, records: list, batch_size: int = 1000):
#     inserted = 0

#     for i in range(0, len(records), batch_size):
#         batch = records[i:i + batch_size]
#         stmt = t_mesh.insert()
#         conn.execute(stmt, batch)
#         inserted += len(batch)
#         print(f"Inserted {inserted} records...")

#     return {"message imports mesh": f"导入完成，共导入 {inserted} 行"}




def imports(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        stmt = mysql_insert(t_mesh).values(batch)
        # 如果 entity_id 已存在，则更新其它字段
        stmt = stmt.on_duplicate_key_update(
            entity_name=stmt.inserted.entity_name,
            # second_entity_id=stmt.inserted.second_entity_id
        )

        conn.execute(stmt)
        inserted += len(batch)
        print(f"Processed {inserted} records...")

    return {"message imports mesh": f"导入完成，共处理 {inserted} 行"}



def imports_tree(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        stmt = mysql_insert(t_mesh_tree).values(batch)
        # 如果 entity_id 已存在，则更新其它字段
        stmt = stmt.on_duplicate_key_update(

            category=stmt.inserted.category
        )

        conn.execute(stmt)
        inserted += len(batch)
        print(f"Processed {inserted} records...")
    return {"message imports mesh": f"导入完成，共处理 {inserted} 行"}

def  import_registry_numbers(conn: Connection, records: list, batch_size: int = 1000):
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        stmt = mysql_insert(t_registry_numbers).values(batch)
        # 如果 entity_id 已存在，则更新其它字段
        stmt = stmt.on_duplicate_key_update(

            registry_type=stmt.inserted.registry_type
        )

        conn.execute(stmt)
        inserted += len(batch)
        print(f"Processed {inserted} records...")
    return {"message imports registry_numbers": f"导入完成，共处理 {inserted} 行"}

def delete_by_id(conn: Connection, entity_id: str):
    stmt = t_mesh.delete().where(t_mesh.c.entity_id == entity_id)
    conn.execute(stmt)
    stmt = t_mesh_tree.delete().where(t_mesh_tree.c.entity_id==entity_id)
    conn.execute(stmt)



def get_parent(tree_number):
    if pd.isna(tree_number):
        return None
    parts = tree_number.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else None

# def imports_tree(conn: Connection, records: list, batch_size: int = 1000):
#     inserted = 0
#     for i in range(0, len(records), batch_size):
#         batch = records[i:i + batch_size]
#         stmt = t_mesh_tree.insert()
#         conn.execute(stmt, batch)
#         inserted += len(batch)
#         print(f"Inserted {inserted} records...")

#     return {"message imports_tree": f"导入完成，共导入 {inserted} 行"}

# def imports_tree(conn: Connection, records: list, batch_size: int = 1000):
#     inserted = 0

#     for i in range(0, len(records), batch_size):
#         batch = records[i:i + batch_size]

#         stmt = insert(t_mesh_tree).values(batch)
#         stmt = stmt.on_duplicate_key_update(
#             category=stmt.inserted.category
#         )

#         conn.execute(stmt)
#         inserted += len(batch)
#         print(f"Processed {inserted} records...")

#     return {"message imports_tree": f"导入完成，共处理 {inserted} 行"}

def init(conn: Connection,category):
    if category == "mesh":
        json_data = import_ncbi_mesh.get_json("/ssd1/wy/workspace2/nextflow-fastapi/desc2025.xml")
        df = pd.DataFrame(json_data)
        df['second_entity_id'] = df['registry_numbers'].apply(
            lambda x: x[0].replace("txid","TAX") if isinstance(x, list) and len(x)>0 and x[0].startswith("txid") else ""
        )
        # df = df.drop("registry_numbers",axis=1)

        df_exploded = df.explode(["TreeNumberList"], ignore_index=True)

        df_exploded["ParentTree"] = df_exploded["TreeNumberList"].apply(get_parent)
        df_exploded_rename = df_exploded[["DescriptorUI","DescriptorName","TreeNumberList","ParentTree","second_entity_id"]].rename({
                "DescriptorUI":"entity_id",
                "DescriptorName":"entity_name",
                "TreeNumberList":"tree_number",
                "ParentTree":"parent_tree",
                "second_entity_id":"registry_number"
            },axis=1)
        df_exploded_rename["category"]  = df_exploded_rename["tree_number"].apply(lambda x: str(x).split(".")[0])
        df_exploded_rename["registry_type"]  = df_exploded_rename["registry_number"].apply(lambda x: "taxonomy" if x.startswith("TAX")  else "_NULL_")
        df_exploded_rename["parent_tree"]  = df_exploded_rename["parent_tree"].apply(lambda x: x if not pd.isna(x) else "_NULL_")
        df_exploded_rename["tree_number"]  = df_exploded_rename["tree_number"].apply(lambda x: x if not pd.isna(x) else "_NULL_")

        # df_exploded_rename["major_category"]  = df_exploded_rename["tree_number"].apply(lambda x: str(x).split(".")[0][0])
        df_exploded_rename_node = df_exploded_rename[["entity_id","entity_name"]].drop_duplicates( keep="first")
        # df_exploded_rename_node["entity_id"] = df_exploded_rename_node.apply(lambda x: uuid(),axis=1)
        data = json.loads(df_exploded_rename_node.to_json(orient="records"))
        imports(conn, data)
        df_exploded_rename_tree = df_exploded_rename[["entity_id","tree_number","parent_tree","category"]].drop_duplicates( keep="first")
        data_tree = json.loads(df_exploded_rename_tree.to_json(orient="records"))
        imports_tree(conn, data_tree)
        df_exploded_rename_registry = df_exploded_rename[["entity_id","registry_number"]].drop_duplicates( keep="first")
        df_exploded_rename_registry = df_exploded_rename_registry[df_exploded_rename_registry["registry_number"]!=""]
        data_registry =  json.loads(df_exploded_rename_registry.to_json(orient="records"))
        import_registry_numbers(conn, data_registry)

    elif category == "kegg":
        with open("/data/DATABASES/br_br08901.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        data_tree = import_kegg.parse_kegg_hierarchy(lines)
        
        # df_exploded_tree = pd.DataFrame(data_tree)
        # df_exploded_tree = df_exploded_tree[["entity_id","entity_name"]]
        # data = json.loads(df_exploded_rename_node.to_json(orient="records"))
        node = [ 
                { k:v for k,v in item.items() if k  in ["entity_id","entity_name"] }
                for item in data_tree  
            ]
        tree = [ 
                { k:v for k,v in item.items() if k  in ["entity_id","tree_number","parent_tree","category"] }
                for item in data_tree  
            ]
        
        # { k:v for k,v in data_tree if k  in ["entity_id","tree_number","parent_tree","category"] }
        pass
        imports(conn, node)
        imports_tree(conn, tree)

        # # df_exploded_rename_tree = df_exploded_rename_tree.merge(df_exploded_rename_node,on="entity_name",how="left")
        # df_exploded_rename_tree = df_exploded_rename_tree.merge(df_exploded_rename_node[["entity_name","entity_id"]],on="entity_name",how="left")
        # data_tree = json.loads(df_exploded_rename_tree.to_json(orient="records"))
        # imports_tree(conn, data_tree)
    return "success"

'''
{
    "entity_name": "KEGG",
    "category": "KEGG"
}
{
    "entity_name": "Metabolism",
    "category": "KEGG",
    "parent_tree": "KEGG"
}
{
    "entity_name": "Global and overview maps",
    "category": "KEGG",
    "parent_tree": "KEGG.001"
}
{
    "entity_name": "Metabolic pathways",
    "category": "KEGG",
    "entity_id":"map01100",
    "parent_tree": "KEGG.001.001"
}

{
    "entity_name": "Biosynthesis of secondary metabolites",
    "category": "KEGG",
    "entity_id":"map01110",
    "parent_tree": "KEGG.001.001"
}
'''

def add_mesh_node(conn: Connection, data: AddMeshNode):
    """
    同时新增 t_test 和 t_test_tree 节点，并自动生成 tree_number 和 parent_tree
    """
    # entity_id: str, entity_name: str, parent_tree: str = None
    # entity_id 
    # entity_name = data.entity_name
    # parent_tree = data.parent_tree
    # category = data.category
    data_dict = dict(data)
    node_values = {k:v for k,v in data_dict.items() if k!="parent_tree" and k!="category"}
    node_values["entity_id"] = str(uuid())
    # 1️ 插入 t_test 表
    stmt_insert = insert(t_mesh).values(**node_values)
    conn.execute(stmt_insert)
    parent_tree = data.parent_tree
    category = data.category
    # 2️ 生成 tree_number
    if parent_tree is None:
        # 根节点
        tree_number = category #entity_id[:1].upper()  # 可自定义规则
        parent_tree = "_NULL_"
    else:
        # 查询当前父节点已有多少个子节点
        stmt = select(t_mesh_tree.c.tree_number).where(t_mesh_tree.c.parent_tree == parent_tree)
        result = conn.execute(stmt).scalars().all()
        count = len(result) + 1
        tree_number = f"{parent_tree}.{count:03d}"  # 格式化为三位，如 001, 002
    

    # 3️ 插入 t_test_tree 表
    stmt_tree = insert(t_mesh_tree).values(
        entity_id=node_values["entity_id"],
        tree_number=tree_number,
        parent_tree=parent_tree,
        category=category
    )
    conn.execute(stmt_tree)
    return tree_number