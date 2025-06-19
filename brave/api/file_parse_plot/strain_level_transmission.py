import pandas as pd
import json
import os
import pickle
import matplotlib.pyplot as plt


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
    phylogenetic_distances = request_param['phylogenetic_distances']
    sample= sample[['sample_name','sample_group','sample_individual']]
    df_list = [get_one(item) for item in strain]
    df = pd.concat(df_list)

    sample = sample.dropna()[['sample_name','sample_individual']]
    # 重命名 meta，用于合并 sample1
    meta1 = sample.rename(columns={
        'sample_name': 'sample1',
        'sample_individual': 'individual1'
    })

    # 合并 sample1 个体信息
    df_merged = df.merge(meta1[['sample1', 'individual1']], on='sample1', how='left')

    # 再处理 sample2
    meta2 = sample.rename(columns={
        'sample_name': 'sample2',
        'sample_individual': 'individual2'
    })

    df_merged = df_merged.merge(meta2[['sample2', 'individual2']], on='sample2', how='left')
    df_merged = df_merged.query("individual1==individual2 and phylogenetic_distances<@phylogenetic_distances")
    # with open("test/data.pkl","wb") as f:
    #     pickle.dump((sample,df),f)
    df_distances =  df_merged.rename(columns={"individual1":"individual"}).drop("individual2",axis=1)
    df_distances['paired_sample'] = df_distances.apply(lambda x: x['sample1']+"_"+x['sample2'], axis=1)
    df_distances = df_distances.drop(['sample1','sample2'],axis=1)
    # df_distances['clade'].value_counts()
    return df_merged,[df_distances]
    # pass

def parse_plot(data ,request_param):
    df_merged,[df_distances] = data
    df_distances['clade'].value_counts().plot(kind='bar', figsize=(6,4), color='skyblue')
    plt.ylabel('Number of paired samples') 
    return plt