from file_parse_plot.abundance_prevalence import get_abundance_prev
from file_parse_plot.abundance_prevalence import bar_polt,pie_plot
from scipy.stats import mannwhitneyu  

from mvp.api.utils.metaphlan_utils import get_abundance_metadata
import seaborn as sns
import  pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
import statsmodels.formula.api as smf
import statsmodels.api as sm

def get_db_field():
    return ['control','treatment','sites1','sites2']


def parse_data(request_param,db_dict):
    abundance_prev =get_abundance_prev(request_param,db_dict,['sites1','sites2'])
    query = request_param['query']
    calculation_method = request_param['calculation_method']
    hypothesis = request_param['hypothesis']
    abundance_prev_filter = abundance_prev.query("type in @query")
    abundance,metadata,groups = get_abundance_metadata(request_param,db_dict,['control','treatment'])
    safe_cols = [col for col in abundance_prev_filter['taxonomy'] if col in abundance.columns]

    abundance = abundance[safe_cols]
    df_cumulative=None
    if calculation_method=="sum":
        df_cumulative =  pd.DataFrame(abundance.sum(axis=1)).rename({0:"abundance"},axis=1)
    elif calculation_method=="count":
        df_cumulative =  pd.DataFrame((abundance!=0).sum(axis=1)).rename({0:"abundance"},axis=1)
    df_cumulative = pd.merge(df_cumulative,metadata,left_index=True,right_index=True,how="left")
    # pass
    control = df_cumulative[df_cumulative['group']==groups["control"]]['abundance'].to_list()
    treatment = df_cumulative[df_cumulative['group']==groups["treatment"]]['abundance'].to_list()
    
    p_value=None
    if hypothesis=="mannwhitneyu":
        stat, p_value = mannwhitneyu(control, treatment, alternative='two-sided') 
    elif  hypothesis=="poisson":
        model = smf.glm(formula="abundance ~ group", data=df_cumulative, family=sm.families.Poisson()).fit()
        p_value = model.pvalues[1]

    return {"data":df_cumulative.reset_index(),"in_venn":{
        "detection":set(abundance.columns),
        "select":set(abundance_prev_filter['taxonomy'])
    },"in_select_stats":abundance_prev['type'].value_counts(),"in_p_value":p_value}
    # abundance_cumulative = abundance.reset_index() \
    #     .query("taxonomy in @abundance_prev_filter['taxonomy']") \
    #         .set_index("taxonomy").T
    # abundance_cumulative_group = pd.merge(abundance_cumulative, metadata,left_index=True,right_index=True, how='left') \
    #     .reset_index().set_index(['index','group'])
    # calc_abundance_cumulative_group = pd.DataFrame(abundance_cumulative_group.sum(axis=1).reset_index()) \
    #     .rename({0:"sum"},axis=1)
    
    # return abundance_prev_filter

def boxplot(df_cumulative,p_value):
    plt.figure(figsize=(8, 6))
    ax = sns.boxplot(x='group', y='abundance', data=df_cumulative, 
                palette="Set2",  # 配色方案
                width=0.5,       # 箱体宽度
                linewidth=2.5,
               showfliers=False
               )    # 
    sns.stripplot(x='group', y='abundance', data=df_cumulative,  # 叠加散点图
                  color='black', size=4, alpha=0.3)
    y_min,y_max = ax.get_ylim()
    plt.text(x=0.5, y=y_max*0.9, s=f"p = {p_value:.3e}", ha="center", fontsize=12)
    return plt


def venn_plot(venn_data):
    plt.figure(figsize=(8, 6))
    venn2(subsets=[set(venn_data['detection']), set(venn_data['select'])], set_labels = ('detection', 'select'))
    return plt



def parse_plot(data ,request_param):
    df_cumulative = data['data']
    p_value = data['in_p_value']
    boxplot_plt = boxplot(df_cumulative,p_value)
    venn_data = data['in_venn']
    venn_plt = venn_plot(venn_data)
    select_stats = data['in_select_stats']
    bar_plt = bar_polt(select_stats)
    pie_plt = pie_plot(select_stats)
    return [boxplot_plt,venn_plt,bar_plt,pie_plt]