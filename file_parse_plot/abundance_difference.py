import pandas as pd
from skbio.diversity import alpha_diversity
import matplotlib.pyplot as plt
import seaborn as sns
from utils.metaphlan_utils import get_abundance,get_metadata
from scipy.stats import mannwhitneyu  
import numpy as np
from statsmodels.stats.multitest import multipletests
from utils.metaphlan_utils import get_abundance_metadata4

def get_db_field():
    return ['control','treatment']




def parse_data(request_param,db_dict):
    abundance,metadata,groups,abundance1 = get_abundance_metadata4(request_param,db_dict,['control','treatment'])
  
    control_group = groups['control']
    treatment_group = groups['treatment']
   
    df_merge = pd.merge(metadata,abundance,left_index=True, right_index=True).reset_index().set_index(['index'])
    df_merge.to_pickle("test/abundabce.pkl")
    metadata.to_pickle("test/metadata.pkl")
    df_control = df_merge[df_merge['group']==control_group]
    df_treatment = df_merge[df_merge['group']==treatment_group]
    results = []  
    for column_ in df_merge.columns.drop('group'):  
        control_data = df_control[column_].dropna()  
        treatment_data = df_treatment[column_].dropna()  
        stat, p_value = mannwhitneyu(control_data, treatment_data, alternative='two-sided')  
        log2foldchange = np.mean(np.log2(treatment_data+0.000001)) - np.mean(np.log2(control_data+0.000001))
        results.append({'taxonomy': column_, 'Statistic': stat, 'P-value': p_value,"log2foldchange":log2foldchange})  

    # 输出结果  
    results_df = pd.DataFrame(results)  
    # print(results_df)  

    # 可选：多重比较校正  
    results_df['AdjustedP-value'] = results_df['P-value'] * len(results_df)  
    rejected, adj_pvals, _, _ = multipletests(results_df['P-value'] , method='fdr_bh')
    results_df['fdr_bh']  = adj_pvals
    results_df["P-value"] = pd.to_numeric(results_df["P-value"], errors="coerce")  
    results_df.sort_values(by="P-value", ascending=True, inplace=True)  
    # abundance1 = abundance.reset_index()[['taxonomy','tax_id','rank']]
    results_df = pd.merge(results_df, abundance1,on="taxonomy", how='left')

    return {"data":results_df,"in_abundance":df_merge,"in_groups":groups}
    # shannon = alpha_diversity('shannon', abundabce.values, ids=abundabce.index)
    # simpson = alpha_diversity('simpson', abundabce.values, ids=abundabce.index)
    # chao1 = alpha_diversity('chao1', abundabce.values, ids=abundabce.index)
    # # faith_pd = alpha_diversity('faith_pd', abundabce.values, ids=abundabce.index)
    # observed_otus = alpha_diversity('observed_otus', abundabce.values, ids=abundabce.index)
    # pielou_e = alpha_diversity('pielou_e', abundabce.values, ids=abundabce.index)
    # # 合并结果
    # alpha_df = pd.DataFrame({
    #     'Shannon': shannon,
    #     'Observed_OTUs': observed_otus,
    #     "simpson":simpson,
    #     "chao1":chao1,
    #     "pielou_e":pielou_e
    # })
    # alpha_df = alpha_df.merge(metadata, left_index=True, right_index=True).reset_index().rename({"index":"sample_name"},axis=1)
    # return alpha_df

# def boxplot(alpha_df,request_param,metric):
#     control_group = "-".join(request_param['control_group'])
#     treatment_group = "-".join(request_param['treatment_group'])

#     control_alpha = alpha_df.query("group == @control_group")[metric].to_list()
#     treatment_alpha = alpha_df.query("group == @treatment_group")[metric].to_list()
#     stat, p_value = mannwhitneyu(control_alpha, treatment_alpha, alternative='two-sided')  

#     plt.figure(figsize=(6, 6))
#     # sns.boxplot(x='group', y=metric, data=alpha_df)
#     # sns.swarmplot(x='group', y=metric, data=alpha_df, color='black')

#     ax = sns.boxplot(x='group', y=metric, data=alpha_df, 
#                 palette="Set2",  # 配色方案
#                 width=0.5,       # 箱体宽度
#                 linewidth=2.5,
#             showfliers=False
#             )    # 
#     sns.stripplot(x='group', y=metric, data=alpha_df,  # 叠加散点图
#                 color='black', size=4, alpha=0.3)

#     y_min,y_max = ax.get_ylim()
#     plt.text(x=0.5, y=y_max*0.9, s=f"p = {round(p_value,4)}", ha="center", fontsize=12)
  
#     plt.title(f'Alpha Diversity ({metric} Index)')
#     return plt
def ma_plot(abundance,request_param,groups):
    fc_thresh = 0.1
    control_group = groups['control']
    treatment_group = groups['treatment']
    abundance = abundance.set_index("group")
    log_df = np.log2(abundance + 1)
    control_df = log_df.reset_index("group").query("group==@control_group").set_index("group")
    treatment_df = log_df.reset_index("group").query("group==@treatment_group").set_index("group")
    control_mean = control_df.mean(axis=0)
    treatment_mean = treatment_df.mean(axis=0)
    M = treatment_mean - control_mean
    A = (treatment_mean + control_mean) / 2
    plt.figure(figsize=(8, 6))
    colors = np.where(M > fc_thresh, 'red', np.where(M < -fc_thresh, 'blue', 'gray'))
    plt.scatter(A, M, c=colors, alpha=0.7)
    plt.axhline(fc_thresh, color='black', linestyle='--')
    plt.axhline(-fc_thresh, color='black', linestyle='--') 
    plt.xlabel('A = mean log2 expression')
    plt.ylabel('M = log2 Fold Change')
    plt.title('MA Plot')
    plt.tight_layout()  
    return  plt


def volcano(results_df,request_param,groups):
    control_group = groups['control']
    treatment_group = groups['treatment']
    results_df['-log10(pvalue)'] = -np.log10(results_df['P-value'])

    # 设置阈值
    pvalue_thresh = 0.05
    logfc_thresh = 1

    # 标记显著基因
    results_df['color'] = 'gray'
    results_df.loc[(results_df['P-value'] < pvalue_thresh) & (results_df['log2foldchange'] > logfc_thresh), 'color'] = 'red'
    results_df.loc[(results_df['P-value'] < pvalue_thresh) & (results_df['log2foldchange'] < -logfc_thresh), 'color'] = 'blue'

    up_count = ((results_df['P-value'] < pvalue_thresh) & (results_df['log2foldchange'] > logfc_thresh)).sum()
    down_count = ((results_df['P-value'] < pvalue_thresh) & (results_df['log2foldchange'] < -logfc_thresh)).sum()


    # 绘图
    plt.figure(figsize=(8, 6))
    plt.scatter(results_df['log2foldchange'], results_df['-log10(pvalue)'], c=results_df['color'], alpha=0.7)
    plt.axhline(-np.log10(pvalue_thresh), color='black', linestyle='--')
    plt.axvline(logfc_thresh, color='black', linestyle='--')
    plt.axvline(-logfc_thresh, color='black', linestyle='--')

    # 添加图例
    plt.scatter([], [], color='red', label=f'Up ({up_count})')
    plt.scatter([], [], color='blue', label=f'Down ({down_count})')
    plt.scatter([], [], color='gray', label='Not significant')
    plt.legend()

    plt.xlabel('log2 Fold Change')
    plt.ylabel('-log10(p-value)')
    plt.title(f'Volcano Plot({treatment_group} vs {control_group})')
    return plt

def boxplot(abundance,taxonomy):
    final_df = abundance[[taxonomy,"group"]]
    final_df.columns = ['abundance','group']
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='group', y='abundance', data=final_df, 
                palette="Set2",  # 配色方案
                width=0.5,       # 箱体宽度
                linewidth=2.5,
            showfliers=False
            )    # 
    
    sns.stripplot(x='group', y='abundance', data=final_df,  # 叠加散点图
                color='black', size=4, alpha=0.3)
    plt.title(f"boxplot of {taxonomy}")
    plt.grid(axis='y', linestyle=':')
    return plt

def parse_plot(data ,request_param):
    results_df = data['data']
    groups = data['in_groups']
    volcano_plt = volcano(results_df,request_param,groups)
    abundance = data["in_abundance"]
    taxonomy = results_df['taxonomy'][0]
    boxplot_plt = boxplot(abundance,taxonomy)
    ma_plt = ma_plot(abundance,request_param,groups)
    

    return [volcano_plt,boxplot_plt,ma_plt]

#     alpha_df = data
#     Shannon = boxplot(alpha_df,request_param,'Shannon')
#     Observed_OTUs = boxplot(alpha_df,request_param,'Observed_OTUs')
#     simpson = boxplot(alpha_df,request_param,'simpson')
#     chao1 = boxplot(alpha_df,request_param,'chao1')
#     pielou_e = boxplot(alpha_df,request_param,'pielou_e')
#     return [Shannon,Observed_OTUs,simpson,chao1,pielou_e]