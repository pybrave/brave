import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
import pandas as pd
from functools  import reduce
import numpy as np
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests


def get_db_field():
    return ['control','treatment']

def get_one_df(file,sample_key):
    df = pd.read_csv(file,sep="\t",comment="#")
    df.columns.values[-1] = sample_key
    df = df.set_index(['Geneid','Chr','Start','End','Strand','Length']) # 'Chr','Start','End','Strand','Length'
    # df = df.drop(['Chr','Start','End','Strand','Length'],axis=1)
    return df

def get_df(data):
    df_list =  [get_one_df(item.content['count'],item.sample_key) for item in data]
    df = reduce(lambda x,y:pd.merge(x,y,left_index=True,right_index=True, how="inner"),df_list)
    return df

def poisson_test(k1, k2):
    if k1 + k2 == 0:
        return 1.0
    rate1 = k1
    rate2 = k2
    var = rate1 + rate2
    z = (rate1 - rate2) / np.sqrt(var)
    p = 2 * (1 - norm.cdf(abs(z)))
    return p
def parse_data(request_param,db_dict):
    # file_path = request_param['file_path']
    # df = pd.read_csv(file_path,sep=",")
    control = db_dict['control']
    treatment = db_dict['treatment']
    # df_control = get_df(control)
    # df_treatment = get_df(treatment)
    df = get_df(control+treatment)
    lib_sizes = df.sum()
    df = df.div(lib_sizes, axis=1) * 1e6


    df = df.reset_index()
    df['Geneid'] = df['Geneid'].apply(lambda x: x.replace("_gene",""))
    control_sample = [item.sample_key for item in  control]
    treatment_sample = [item.sample_key for item in  treatment]

    df['control_mean'] = df[control_sample].mean(axis=1)
    df['treatment_mean'] = df[treatment_sample].mean(axis=1)
    df['pval'] = df.apply(lambda row: poisson_test(row["treatment_mean"], row["control_mean"]), axis=1)
    rejected, adj_pvals, _, _ = multipletests(df['pval'] , method='fdr_bh')
    df['adj_pvals']  = adj_pvals
    epsilon = 1e-6  # 避免除0

    df['fold_change'] = (df['treatment_mean'] + epsilon) / (df['control_mean'] + epsilon)
    df['log2FC'] = np.log2(df['fold_change'])
    df = df.sort_values(by='log2FC', key=lambda x: x.abs(), ascending=False)
    
    # group_dict = { item.sample_key:"control" for item in  control}
    # group_dict.update({ item.sample_key:"treatment" for item in  treatment})
    # treatment_df = get_df()
    # df = df.reset_index().rename({"index":"Geneid"},axis=1)
    # df['group']= df.apply(lambda x: group_dict[x['Geneid']],axis=1)


    return df #json.dumps(request_param)


def parse_plot(data ,request_param):
    results_df = data
    results_df['-log10(pval)'] = -np.log10(results_df['pval'])

    # 设置阈值
    pvalue_thresh = 0.01
    logfc_thresh = 1

    # 标记显著基因
    results_df['color'] = 'gray'
    results_df.loc[(results_df['pval'] < pvalue_thresh) & (results_df['log2FC'] > logfc_thresh), 'color'] = 'red'
    results_df.loc[(results_df['pval'] < pvalue_thresh) & (results_df['log2FC'] < -logfc_thresh), 'color'] = 'blue'


    plt.figure(figsize=(8, 6))
    plt.scatter(results_df['log2FC'], results_df['-log10(pval)'], c=results_df['color'], alpha=0.7)
    plt.axhline(-np.log10(pvalue_thresh), color='black', linestyle='--')
    plt.axvline(logfc_thresh, color='black', linestyle='--')
    plt.axvline(-logfc_thresh, color='black', linestyle='--')
    plt.xlabel('log2 Fold Change')
    plt.ylabel('-log10(p-value)')
    return plt