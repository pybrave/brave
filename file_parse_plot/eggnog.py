import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
from matplotlib_venn import venn2
from Bio import SeqIO

def parse_data(request_param):
    # file_path = request_param['input_faa']
    # gene_set = set([record.id for record in SeqIO.parse(file_path, "fasta")])
    res_file_path = request_param['file_path']
    annotations0 = pd.read_csv(res_file_path,sep="\t",comment="#")
    # annotations_gene_set = set(annotations0['query'])
    # unannotated_gene_set =  gene_set-annotations_gene_set
    # # return json.loads(df.to_json(orient="records"))
    # return {"data":annotations0,"all_gene_set":gene_set,"annotated_gene_set":annotations_gene_set,"unannotated_gene_set":unannotated_gene_set}
    return annotations0
def parse_plot(data ,request_param):
    df_annotation = data
    df_annotation_filter = df_annotation[['Preferred_name','Description','eggNOG_OGs','GOs','EC','KEGG_ko','KEGG_Pathway','KEGG_Module','KEGG_Reaction','KEGG_rclass','BRITE','KEGG_TC','CAZy','BiGG_Reaction','PFAMs']]
    file_path = request_param['input_faa']
    locus_tag = set([record.id for record in SeqIO.parse(file_path, "fasta")])

    
    counts = (df_annotation_filter != '-').sum()
    new_data = pd.Series({'locus_tag': len(locus_tag)})
    all_counts = pd.concat([new_data, counts])

    ax = all_counts.plot(kind='bar', color='skyblue')
    for i, value in enumerate(all_counts):
        ax.text(i, value + 0.1, str(value), ha='center', va='bottom')
    plt.ylabel("Number of gene")
    # plt.title("Non-NaN Values per Column")
    plt.xticks(rotation=80)
    plt.tight_layout()
    return plt
