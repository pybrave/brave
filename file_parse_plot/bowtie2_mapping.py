import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
import os
import re

regexes = {
    "unpaired_aligned_none": r"(\d+) \([\d\.]+%\) aligned 0 times",
    "unpaired_aligned_one": r"(\d+) \([\d\.]+%\) aligned exactly 1 time",
    "unpaired_aligned_multi": r"(\d+) \([\d\.]+%\) aligned >1 times",
    "paired_aligned_none": r"(\d+) \([\d\.]+%\) aligned concordantly 0 times",
    "paired_aligned_one": r"(\d+) \([\d\.]+%\) aligned concordantly exactly 1 time",
    "paired_aligned_multi": r"(\d+) \([\d\.]+%\) aligned concordantly >1 times",
    "paired_aligned_discord_one": r"(\d+) \([\d\.]+%\) aligned discordantly 1 time",
    "paired_aligned_discord_multi": r"(\d+) \([\d\.]+%\) aligned discordantly >1 times",
    "paired_aligned_mate_one": r"(\d+) \([\d\.]+%\) aligned exactly 1 time",
    "paired_aligned_mate_multi": r"(\d+) \([\d\.]+%\) aligned >1 times",
    "paired_aligned_mate_none": r"(\d+) \([\d\.]+%\) aligned 0 times",
}
def prase_bowte2(file):
    parsed_data = {}
    with open(file) as f:
        filename = os.path.basename(file).replace(".bowtie2.log","")
        parsed_data['sample_name'] = filename
        # print()
        for line in f.readlines():
            # print(line)
            for  k, r in regexes.items():
                match = re.search(r, line)
                if match:
                    parsed_data[k] = int( match.group(1))
                    # print(match.group(1))
                    # match.group(1)

    return parsed_data


def parse_data(request_param,sample):
    log_path_list = request_param['log_path_list']
    sample= sample[['sample_name','sample_group']]
    bowte2_dict_list = [prase_bowte2(x) for x in log_path_list]
    bowtie2_df = pd.DataFrame(bowte2_dict_list)
    if request_param['mappping_type'] =='unpaired':
        bowtie2_df['alignment_reads'] = bowtie2_df.apply(lambda x:x['unpaired_aligned_one']+x['unpaired_aligned_multi'] ,axis=1)
        bowtie2_df['alignment_reads_num'] = bowtie2_df.apply(lambda x:   x['unpaired_aligned_one']+x['unpaired_aligned_multi']+x['unpaired_aligned_none'] , axis=1)
        bowtie2_df['alignment_rate'] =bowtie2_df.apply(lambda x: x['alignment_reads'] / x['alignment_reads_num'] ,axis=1)
    else:
        bowtie2_df['alignment_reads'] = bowtie2_df.apply(lambda x:(x['paired_aligned_one']+x['paired_aligned_multi']+x['paired_aligned_discord_one'])*2+x['paired_aligned_mate_one']+x['unpaired_aligned_multi'] ,axis=1)
        bowtie2_df['alignment_reads_num'] = bowtie2_df.apply(lambda x:   (x['paired_aligned_none']+x['paired_aligned_one']+x['paired_aligned_multi'])*2 , axis=1)
        bowtie2_df['alignment_rate'] =bowtie2_df.apply(lambda x: x['alignment_reads'] / x['alignment_reads_num'] ,axis=1)    
    
    df_merge = pd.merge(bowtie2_df,sample,on="sample_name",how="inner" )
    return df_merge

def parse_plot(data ,request_param):
    alignment_rate = data[['alignment_rate','sample_group']]
    groups = alignment_rate.groupby('sample_group')

    # 设置子图
    fig, axes = plt.subplots(1, len(groups), figsize=(12, 4), sharey=True)

    for ax, (group_name, group_data) in zip(axes, groups):
        group_data['alignment_rate'].plot.hist(ax=ax, bins=4, edgecolor='black', title=f'Group {group_name}')
        ax.set_xlabel('alignment_rate')
        ax.set_ylabel('Frequency')

    plt.tight_layout()
    # alignment_rate.plot.hist(bins=4, edgecolor='black')
    # plt.xlabel('Value')
    # plt.ylabel('Frequency')
    # plt.title('Frequency Histogram')
    return {"img":plt}
    # annotations = data
    # pathway_stat = annotations.query("term.str.contains('map') ")['term'].value_counts()
    # pathway_stat = pd.DataFrame(pathway_stat).query("count>20")['count']
    # # pathway_stat
    # ax = pathway_stat.plot(kind='bar', color='skyblue')
    # for i, value in enumerate(pathway_stat):
    #     ax.text(i, value + 0.1, str(value), ha='center', va='bottom')
    # plt.ylabel("Number of gene")
    # # plt.title("Non-NaN Values per Column")
    # plt.xticks(rotation=80)
    # plt.tight_layout()
    # return {"img":plt}
    # return plt