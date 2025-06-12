import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
from bioservices import KEGG
import os

def getName(terms):
    k = KEGG()
    # kegg_ids = ["map00010", "map00020", "map04010"]
    id_to_name = []
    for kid in terms:
        try:
            data = k.parse(k.get(f"path:{kid}"))
            id_to_name.append((kid,data['NAME'][0]))
        except Exception as e:
            id_to_name.append((kid,None))
    term_name = pd.DataFrame(id_to_name,columns=['term','name'])
    return term_name

def read_kegg_pathway_term_name(name):
    file_path = f"/ssd1/wy/workspace2/nextflow-fastapi/databases/kegg_{name}_term_name.tsv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path, sep="\t")
    k = KEGG()
    pathways = k.list(name)
    lines = pathways.strip().split("\n")
    list_map = [(line.split("\t")[0], line.split("\t")[1]) for line in lines]
    db_term_name = pd.DataFrame(list_map,columns=['term','name'])
    db_term_name.to_csv(file_path, sep="\t",index=False)
    return db_term_name

def parse_data(request_param):
    file_path = request_param['file_path']
    annotations0 = pd.read_csv(file_path,sep="\t",comment="#")
    annotations = annotations0[["query","KEGG_ko","KEGG_Pathway","Preferred_name"]] # ,"KEGG_Module","KEGG_Reaction","KEGG_rclass"
    annotations = annotations.assign(
        KEGG_Pathway=annotations["KEGG_Pathway"].str.split(",")
    ).explode("KEGG_Pathway")
    # annotations = annotations.query("KEGG_Pathway.str.contains('ko')")
    annotations.columns = ['gene','KO','term','gene_name']
    # term_name = getName(set(annotations['term'].to_list()))
    term_name = read_kegg_pathway_term_name("pathway")
    df = pd.merge(annotations,term_name,on="term",how="left")
    return df # json.loads(df.to_json(orient="records"))

def parse_plot(data ,request_param):
    annotations = data
    pathway_stat = annotations.query("term.str.contains('map') ")['term'].value_counts()
    pathway_stat = pd.DataFrame(pathway_stat).query("count>20")['count']
    # pathway_stat
    ax = pathway_stat.plot(kind='bar', color='skyblue')
    for i, value in enumerate(pathway_stat):
        ax.text(i, value + 0.1, str(value), ha='center', va='bottom')
    plt.ylabel("Number of gene")
    # plt.title("Non-NaN Values per Column")
    plt.xticks(rotation=80)
    plt.tight_layout()
    return {"img":plt}
    # return plt