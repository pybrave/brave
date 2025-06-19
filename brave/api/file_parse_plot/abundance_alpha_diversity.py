import pandas as pd
from skbio.diversity import alpha_diversity
import matplotlib.pyplot as plt
import seaborn as sns
from brave.api.utils.metaphlan_utils import get_abundance,get_metadata
from scipy.stats import mannwhitneyu  
from brave.api.utils.metaphlan_utils import get_abundance_metadata


def get_db_field():
    return ['control','treatment']




def parse_data(request_param,db_dict):
    abundance,metadata,groups = get_abundance_metadata(request_param,db_dict,['control','treatment'])

    # control_sample = db_dict['control_sample']
    # treatment_sample = db_dict['treatment_sample']
    # control_group = "-".join(request_param['control_group'])
    # treatment_group = "-".join(request_param['treatment_group'])
    # abundabce = get_abundance(control_sample + treatment_sample)
    # metadata = get_metadata(control_sample,treatment_sample,control_group,treatment_group)
    # abundabce.to_pickle("test/abundabce.pkl")
    # metadata.to_pickle("test/metadata.pkl")
    # rank = "SPECIES"
    # if "rank" in request_param:
    #     rank = request_param['rank']
    # abundabce = abundabce.reset_index(['taxonomy','rank']).reset_index(drop=True).query("rank==@rank").drop("rank",axis=1).set_index("taxonomy").T

    shannon = alpha_diversity('shannon', abundance.values, ids=abundance.index)
    simpson = alpha_diversity('simpson', abundance.values, ids=abundance.index)
    chao1 = alpha_diversity('chao1', abundance.values, ids=abundance.index)
    # faith_pd = alpha_diversity('faith_pd', abundance.values, ids=abundance.index)
    observed_otus = alpha_diversity('observed_otus', abundance.values, ids=abundance.index)
    pielou_e = alpha_diversity('pielou_e', abundance.values, ids=abundance.index)
    # 合并结果
    alpha_df = pd.DataFrame({
        'Shannon': shannon,
        'species richness': observed_otus,
        "simpson":simpson,
        "chao1":chao1,
        "pielou_e":pielou_e
    })
    alpha_df = alpha_df.merge(metadata, left_index=True, right_index=True).reset_index().rename({"index":"sample_name"},axis=1)
    return {"data":alpha_df,"groups":groups}

def boxplot(alpha_df,groups,metric,index="Index"):
    control_group = groups['control']
    treatment_group = groups['treatment']

    control_alpha = alpha_df.query("group == @control_group")[metric].to_list()
    treatment_alpha = alpha_df.query("group == @treatment_group")[metric].to_list()
    stat, p_value = mannwhitneyu(control_alpha, treatment_alpha, alternative='two-sided')  

    plt.figure(figsize=(6, 6))
    # sns.boxplot(x='group', y=metric, data=alpha_df)
    # sns.swarmplot(x='group', y=metric, data=alpha_df, color='black')

    ax = sns.boxplot(x='group', y=metric, data=alpha_df, 
                palette="Set2",  # 配色方案
                width=0.5,       # 箱体宽度
                linewidth=2.5,
            showfliers=False
            )    # 
    sns.stripplot(x='group', y=metric, data=alpha_df,  # 叠加散点图
                color='black', size=4, alpha=0.3)

    y_min,y_max = ax.get_ylim()
    plt.text(x=0.5, y=y_max*0.9, s=f"p = {round(p_value,4)}", ha="center", fontsize=12)
  
    plt.title(f'Alpha Diversity ({metric} {index})')
    return plt
def parse_plot(data ,request_param):
    alpha_df = data['data']
    groups = data['groups']
    Shannon = boxplot(alpha_df,groups,'Shannon')
    Observed_OTUs = boxplot(alpha_df,groups,'species richness',"")
    simpson = boxplot(alpha_df,groups,'simpson')
    chao1 = boxplot(alpha_df,groups,'chao1')
    pielou_e = boxplot(alpha_df,groups,'pielou_e')
    return [Shannon,Observed_OTUs,simpson,chao1,pielou_e]