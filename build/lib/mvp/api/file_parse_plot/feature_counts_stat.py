import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
from  functools import reduce
def parse_data(request_param,sample):
    log_path_list = request_param['log_path_list']
    df_list = [pd.read_csv(item,sep="\t") for item in log_path_list ]
    df = reduce(lambda x,y:pd.merge(x,y,on='Status'),df_list)
    df = df.set_index("Status").T
    df['assigned_total_reads'] = df.apply(lambda x:sum(x) ,axis=1)
    df['assigned_rate'] = df.apply(lambda x:x['Assigned']/x['assigned_total_reads'] ,axis=1)
    df = df.reset_index().rename({'index':"sample_name"},axis=1)
    df['sample_name'] = df['sample_name'].apply(lambda x: x.replace(".sorted.bam",""))

    sample= sample[['sample_name','sample_group']]

    df_merge = pd.merge(df,sample,on="sample_name",how="inner" )
    return df_merge

def parse_plot(data ,request_param):
    alignment_rate = data[['assigned_rate','sample_group']]
    groups = alignment_rate.groupby('sample_group')

    # 设置子图
    fig, axes = plt.subplots(1, len(groups), figsize=(12, 4), sharey=True)

    for ax, (group_name, group_data) in zip(axes, groups):
        group_data['assigned_rate'].plot.hist(ax=ax, bins=4, edgecolor='black', title=f'Group {group_name}')
        ax.set_xlabel('assigned_rate')
        ax.set_ylabel('Frequency')

    plt.tight_layout()
    # alignment_rate.plot.hist(bins=4, edgecolor='black')
    # plt.xlabel('Value')
    # plt.ylabel('Frequency')
    # plt.title('Frequency Histogram')
    return {"img":plt}