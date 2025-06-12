import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
import os
def parse_data(request_param):
    file_path = request_param['file_path']
    df = pd.read_csv(file_path,sep=",")
    return json.loads(df.to_json(orient="records"))

def parse_plot(data ,request_param):
    df = pd.DataFrame(data)
    
    sample_name_path = request_param['file_path'].split("/")
    sample_name = sample_name_path[len(sample_name_path)-3]
    reference_name = sample_name_path[len(sample_name_path)-4]
    # 两类字段 
    # 可视化 1：主要突变类型柱状图
    main_mutations = [
        "base_substitution", "small_indel", "large_deletion",
        "large_insertion", "large_amplification", "large_substitution",
        "mobile_element_insertion"
    ]
    # 可视化 2：碱基替换子类型柱状图
    substitution_types = [
        "base_substitution.synonymous", "base_substitution.nonsynonymous",
        "base_substitution.nonsense", "base_substitution.noncoding",
        "base_substitution.pseudogene", "base_substitution.intergenic"
    ]

    # 准备数据
    df_main = df[main_mutations].iloc[0]
    df_sub = df[substitution_types].iloc[0]

    # 创建画布
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))  # 1行2列

    # ---------- 图1：主要突变类型 ----------
    axes[0].bar(df_main.index, df_main.values, color="skyblue")
    axes[0].set_title("Main Mutation Types")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis='x', rotation=90)

    # 在柱子上标数值
    for i, val in enumerate(df_main.values):
        axes[0].text(i, val + max(df_main.values) * 0.01, str(val), ha='center', va='bottom', fontsize=9)

    # ---------- 图2：碱基替换子类型 ----------
    axes[1].bar(df_sub.index, df_sub.values, color="lightcoral")
    axes[1].set_title("Base Substitution Subtypes")
    axes[1].set_ylabel("Count")
    axes[1].tick_params(axis='x', rotation=90)

    # 在柱子上标数值
    for i, val in enumerate(df_sub.values):
        axes[1].text(i, val + max(df_sub.values) * 0.01, str(val), ha='center', va='bottom', fontsize=9)
    plt.suptitle(f"{sample_name} ({reference_name})")
    # 布局优化 & 显示
    plt.tight_layout()
    # plot_data = {k:v for k,v in data.items() if k not in ['contigs','bases']}
    # # 饼图标签和数值
    # labels = list(plot_data.keys())
    # sizes = list(plot_data.values())

    # # 可选颜色（自动分配也可以）
    # colors = plt.cm.Paired.colors

    # # 绘图
    # plt.figure(figsize=(6, 6))
    # plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
    # plt.title("Genome Feature Composition")
    # plt.axis('equal')  # 保证圆形
    # plt.tight_layout()
    return plt

