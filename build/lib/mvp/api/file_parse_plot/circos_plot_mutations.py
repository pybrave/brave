import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
from functools import reduce
from pycirclize import Circos
import numpy as np
def read_breseq(name,path, query):
    df =  pd.read_csv(path, sep="\t") 
    df = df.query(query)[['locus_tag']].drop_duplicates(subset='locus_tag', keep='first') 
    # ,'mutation_category','type','snp_type','seq_id','position', 'position_end', 'position_start',"ref_seq","new_seq","gene_name","gene_product",'genes_promoter'
    df[name] = 1 
    return df

def parse_data(request_param):
    list_file = request_param['list_files']
    query="~locus_tag.str.contains('/') & ~locus_tag.str.contains('\[') & ~locus_tag.str.contains('\|') & ~locus_tag.str.contains('–') "
    # query =query+" & mutation_category=='snp_nonsynonymous'"
    dfs = [ read_breseq(it.split("#")[0],it.split("#")[1],query) for it in list_file]
    df_merged = reduce(lambda left, right: pd.merge(left, right, on='locus_tag',how='outer'), dfs)
    df_merged = df_merged.fillna(0)
    return df_merged.to_dict(orient="records")

def parse_plot(data ,request_param):
    df_merged  = pd.DataFrame(data).set_index("locus_tag")
    sectors = {"A":len(df_merged) }
    circos = Circos(sectors, space=10)
    vmin1, vmax1 = 0, 1
    vmin2, vmax2 = -100, 100
    for sector in circos.sectors:
        # Plot heatmap
        # track1 = sector.add_track((80, 100))
        # track1.axis()
        # track1.xticks_by_interval(1)
        # data = np.random.randint(vmin1, vmax1 + 1, (4, int(sector.size)))
        # track1.heatmap(data, vmin=vmin1, vmax=vmax1, show_value=False)
        # Plot heatmap with labels
        track2 = sector.add_track((50, 100))
        track2.axis()
        x = np.linspace(2, int(track2.size), int(track2.size)) - 2
        # xlabels = [str(int(v + 1)) for v in x]
        track2.xticks(x, df_merged.T.columns.to_list(), outer=True,label_orientation="vertical")
        track2.yticks(2+np.arange(df_merged.shape[1]) * 2, df_merged.columns.to_list()[::-1])
        data = np.array(df_merged.T) # np.random.randint(vmin2, vmax2 + 1, (5, int(sector.size)))
        track2.heatmap(data, cmap="Reds", rect_kws=dict(ec="white", lw=0.5), vmin=0, vmax=1,)

    # circos.colorbar(bounds=(0.35, 0.55, 0.3, 0.01), vmin=vmin1, vmax=vmax1, orientation="horizontal")
    circos.colorbar(bounds=(0.35, 0.55, 0.3, 0.01), vmin=0, vmax=1, orientation="horizontal", cmap="Reds")

    fig = circos.plotfig()
    return plt

#     df = pd.DataFrame(data)
   
#     # 两类字段 
#     # 可视化 1：主要突变类型柱状图
#     main_mutations = [
#         "base_substitution", "small_indel", "large_deletion",
#         "large_insertion", "large_amplification", "large_substitution",
#         "mobile_element_insertion"
#     ]
#     # 可视化 2：碱基替换子类型柱状图
#     substitution_types = [
#         "base_substitution.synonymous", "base_substitution.nonsynonymous",
#         "base_substitution.nonsense", "base_substitution.noncoding",
#         "base_substitution.pseudogene", "base_substitution.intergenic"
#     ]

#     # 准备数据
#     df_main = df[main_mutations].iloc[0]
#     df_sub = df[substitution_types].iloc[0]

#     # 创建画布
#     fig, axes = plt.subplots(1, 2, figsize=(16, 6))  # 1行2列

#     # ---------- 图1：主要突变类型 ----------
#     axes[0].bar(df_main.index, df_main.values, color="skyblue")
#     axes[0].set_title("Main Mutation Types")
#     axes[0].set_ylabel("Count")
#     axes[0].tick_params(axis='x', rotation=45)

#     # 在柱子上标数值
#     for i, val in enumerate(df_main.values):
#         axes[0].text(i, val + max(df_main.values) * 0.01, str(val), ha='center', va='bottom', fontsize=9)

#     # ---------- 图2：碱基替换子类型 ----------
#     axes[1].bar(df_sub.index, df_sub.values, color="lightcoral")
#     axes[1].set_title("Base Substitution Subtypes")
#     axes[1].set_ylabel("Count")
#     axes[1].tick_params(axis='x', rotation=45)

#     # 在柱子上标数值
#     for i, val in enumerate(df_sub.values):
#         axes[1].text(i, val + max(df_sub.values) * 0.01, str(val), ha='center', va='bottom', fontsize=9)

#     # 布局优化 & 显示
#     plt.tight_layout()
#     # plot_data = {k:v for k,v in data.items() if k not in ['contigs','bases']}
#     # # 饼图标签和数值
#     # labels = list(plot_data.keys())
#     # sizes = list(plot_data.values())

#     # # 可选颜色（自动分配也可以）
#     # colors = plt.cm.Paired.colors

#     # # 绘图
#     # plt.figure(figsize=(6, 6))
#     # plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
#     # plt.title("Genome Feature Composition")
#     # plt.axis('equal')  # 保证圆形
#     # plt.tight_layout()
#     return plt

