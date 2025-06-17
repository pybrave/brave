import pandas as pd
import json
import os
def get_db_field():
    return ['strain']

def get_one(item):
    content = item.content

    tree_pairwisedists = content['tree_pairwisedists']
    name = os.path.basename(tree_pairwisedists).replace("_tree_pairwisedists.tsv","")
    df = pd.read_csv(tree_pairwisedists,sep="\t",header=None,names=["sample1","sample2","phylogenetic_distances"])
    df["clade"] = name
    return df

def parse_data(request_param,strain,sample):
    # strain = db_dict['strain']
    sample= sample[['sample_name','sample_group']]
    df_list = [get_one(item) for item in strain]
    df = pd.concat(df_list)
    return df
    # pass