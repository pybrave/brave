import pandas as pd
from skbio.diversity import alpha_diversity
import matplotlib.pyplot as plt
import seaborn as sns
from mvp.api.utils.metaphlan_utils import get_abundance,get_metadata
from skbio.diversity import beta_diversity
from skbio.stats.distance import permanova
from skbio.stats.ordination import pcoa
from matplotlib.patches import Ellipse
import numpy as np
from mvp.api.utils.metaphlan_utils import get_abundance_metadata



def get_db_field():
    return ['control','treatment']




def parse_data(request_param,db_dict):
    abundance,metadata,groups = get_abundance_metadata(request_param,db_dict,['control','treatment'])
    # control_sample = db_dict['control_sample']
    # treatment_sample = db_dict['treatment_sample']
    # control_group = "-".join(request_param['control_group'])
    # treatment_group = "-".join(request_param['treatment_group'])
    # abundance = get_abundance(control_sample + treatment_sample)
    # metadata = get_metadata(control_sample,treatment_sample,control_group,treatment_group)
    # abundance.to_pickle("test/abundance.pkl")
    # metadata.to_pickle("test/metadata.pkl")
    # rank = "SPECIES"
    # if "rank" in request_param:
    #     rank = request_param['rank']
    # abundance = abundance.reset_index(['taxonomy','rank']).reset_index(drop=True).query("rank==@rank").drop("rank",axis=1).set_index("taxonomy").T
    # abundance.to_pickle("test/abundance.pkl")

    data = pd.merge(metadata,abundance,left_index=True, right_index=True).reset_index().set_index(['index','group'])
    bc_dm = beta_diversity("braycurtis", data.values, ids=data.index)
    pcoa_result = pcoa(bc_dm)
    pc_df = pcoa_result.samples.loc[:, ['PC1', 'PC2']].reset_index().rename(columns={"level_1":"group"})
    permanova_result = permanova(distance_matrix=bc_dm, 
                                grouping=data.reset_index().set_index(['index','group'],drop=False)['group'],
                                permutations=500)
    return {"data":permanova_result,"pc_df":pc_df,"in_pcoa_result":pcoa_result}
    # shannon = alpha_diversity('shannon', abundance.values, ids=abundance.index)
    # observed_otus = alpha_diversity('observed_otus', abundance.values, ids=abundance.index)
    # # 合并结果
    # alpha_df = pd.DataFrame({
    #     'Shannon': shannon,
    #     'Observed_OTUs': observed_otus
    # })
    # alpha_df = alpha_df.merge(metadata, left_index=True, right_index=True).reset_index().rename({"index":"sample_name"},axis=1)
    
    # # return alpha_df



def parse_plot(data ,request_param):
    pc_df = data['pc_df']
    permanova_result = data['data']
    pcoa_result = data['in_pcoa_result']
    plt.figure(figsize=(7, 6))
    sns.scatterplot(data=pc_df, x='PC1', y='PC2', hue='group', s=100, palette='Set2')
    ax = plt.gca()
    for g, df_g in pc_df.groupby('group'):
        draw_confidence_ellipse(df_g['PC1'], df_g['PC2'], ax)
    plt.xlabel(f"PC1 ({pcoa_result.proportion_explained[0]*100:.2f}%)")
    plt.ylabel(f"PC2 ({pcoa_result.proportion_explained[1]*100:.2f}%)")
    plt.title(f"Beta Diversity - PCoA (Bray-Curtis) PERMANOVA:{permanova_result['p-value']:.3f}")
    return plt
#     alpha_df = data
#     plt.figure(figsize=(6, 6))
#     # sns.boxplot(x='group', y='Shannon', data=alpha_df)
#     # sns.swarmplot(x='group', y='Shannon', data=alpha_df, color='black')

#     sns.boxplot(x='group', y='Shannon', data=alpha_df, 
#                 palette="Set2",  # 配色方案
#                 width=0.5,       # 箱体宽度
#                 linewidth=2.5,
#             showfliers=False
#             )    # 
#     sns.stripplot(x='group', y='Shannon', data=alpha_df,  # 叠加散点图
#                 color='black', size=4, alpha=0.3)


#     plt.title('Alpha Diversity (Shannon Index)')
#     return plt
def draw_confidence_ellipse(x, y, ax, edgecolor='black', facecolor='none', alpha=0.3):
    if len(x) < 2:
        return
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    width, height = 2 * np.sqrt(vals) * 2  # 2σ 对应约 95% 置信区间

    ell = Ellipse((np.mean(x), np.mean(y)), width=width, height=height,
                  angle=theta, edgecolor=edgecolor, facecolor=facecolor,
                  linewidth=1.5, alpha=alpha)
    ax.add_patch(ell)
