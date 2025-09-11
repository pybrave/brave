#!/usr/bin/env python
# coding: utf-8

# In[56]:


import pandas as pd
from brave.api.config.db import get_engine
from brave.microbe.models.core import t_taxonomy

def read_nodes(file):
    """读取 nodes.dmp"""
    cols = [
        "tax_id", "parent_tax_id", "rank", "embl_code", "division_id",
        "inherited_div_flag", "genetic_code_id", "inherited_gc_flag",
        "mitochondrial_genetic_code_id", "inherited_mgc_flag",
        "genbank_hidden_flag", "hidden_subtree_root_flag", "comments"
    ]
    df = pd.read_csv(
        file, sep="|",header=None, usecols=range(len(cols)),
        names=cols
    )
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[["tax_id","parent_tax_id","rank","division_id"]]
    return df


# In[58]:


# read_nodes("/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/nodes.dmp.head")


# In[25]:


def read_names(file):
    """读取 names.dmp，只保留 scientific name"""
    cols = ["tax_id", "name_txt", "unique_name", "name_class"]
    df = pd.read_csv(
        file, sep="|", header=None, usecols=range(len(cols)),
        names=cols
    )
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[df["name_class"] == "scientific name"]
    df = df[["tax_id", "name_txt"]].rename(columns={"name_txt": "scientific_name"})
    return df 


# In[46]:


# df = read_names("/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/names.dmp")


# In[40]:


def read_division(file):
    """读取 division.dmp"""
    cols = ["division_id", "division_cde", "division_name", "comments"]
    df = pd.read_csv(
        file, sep="|", engine="python", header=None, usecols=range(len(cols)),
        names=cols
    )
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[["division_id","division_name"]]
    return df


# In[45]:


# read_division("/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/division.dmp")


# In[41]:


def merge_all(nodes_file, names_file, division_file):
    """合并三张表"""
    nodes = read_nodes(nodes_file)
    names = read_names(names_file)
    division = read_division(division_file)

    # 合并 nodes + names
    merged = pd.merge(nodes, names, on="tax_id", how="left")

    # 合并 division
    merged = pd.merge(merged, division, on="division_id", how="left")

    return merged


# In[59]:




# In[48]:


# len(set(df["scientific_name"]))


# In[49]:


# len(df["scientific_name"])


# In[52]:


# len(set(df["tax_id"]))


# In[53]:


# len(df["tax_id"])



if __name__ == "__main__":
    # nodes_file = "nodes.dmp"
    # names_file = "names.dmp"
    # division_file = "division.dmp"

    # taxonomy = merge_all(nodes_file, names_file, division_file)
    
    taxonomy = merge_all("/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/nodes.dmp","/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/names.dmp","/ssd1/wy/workspace2/nextflow-fastapi/taxonomy/division.dmp")

    # 保存到 CSV
    # taxonomy.to_csv("taxonomy.csv", index=False)
    with get_engine().begin() as conn:
        stmt = t_taxonomy.insert().values(taxonomy.to_dict(orient="records"))
        conn.execute(stmt)

    # 或者保存到 SQLite / MySQL (示例 SQLite)
    # import sqlite3
    # conn = sqlite3.connect("taxonomy.db")
    # taxonomy.to_sql("taxonomy", conn, if_exists="replace", index=False)
    # conn.close()

    # print("整合完成，共有记录：", len(taxonomy))
