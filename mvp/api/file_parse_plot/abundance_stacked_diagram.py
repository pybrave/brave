import pandas as pd
import json
import os
import pickle
import matplotlib.pyplot as plt
from mvp.api.utils.metaphlan_utils import get_abundance
import pickle

def get_db_field():
    return ['samples']



def parse_data(request_param,samples):

    abundance = get_abundance(samples)
    rank = "SPECIES"
    if "rank" in request_param:
        rank = request_param['rank']
    abundance = abundance.reset_index(['taxonomy','rank']).reset_index(drop=True).query("rank==@rank").drop("rank",axis=1).set_index("taxonomy").T
  
    df_meta_list = [pd.DataFrame( [ {'sample_key':item.sample_key, "group":getattr(item, request_param['group_field']) }]) for item in samples]
    df_meta = pd.concat(df_meta_list)
    
    with open("test/data.pkl","wb") as f:
        pickle.dump((abundance,df_meta),f)
    abundance.columns.name = None
    abundance = abundance.reset_index().rename({"index":"sample_key"},axis=1)
    df_merge = pd.merge(abundance,df_meta,left_on="sample_key",right_on="sample_key")
    df_merge = df_merge.set_index(['sample_key','group'])
    return [df_merge]

def parse_plot(data ,request_param):
    [df_merge] = data
    df = df_merge.reset_index("group")
    grouped = df.groupby('group')
    n_groups = grouped.ngroups
    fig, axes = plt.subplots(1, n_groups, figsize=(5*n_groups, 8), sharey=True)

    if n_groups == 1:
        axes = [axes]

    for ax, (name, group) in zip(axes, grouped):
        group_data = group.drop(columns='group')
        group_data.plot(kind='bar', stacked=True, ax=ax, legend=False)
        ax.set_title(name)
        ax.set_xticklabels(group.index, rotation=45)
        ax.set_xlabel('')
        ax.set_xticklabels([]) 
        ax.set_xticks([]) 

    handles, labels = axes[0].get_legend_handles_labels()
    # 添加全局 legend：图下方居中
    fig.legend(
        handles, labels,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.1),  # 根据需要可调整偏移
        ncol=n_groups,             # 横排
        frameon=False                 # 可选：去掉图例边框
    )

    # 让出下方空间以容纳 legend
    plt.tight_layout(rect=[0, 0.05, 1, 1])  # 下边留出 5% 空间


    return plt