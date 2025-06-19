import pandas as pd
from skbio.diversity import alpha_diversity
import matplotlib.pyplot as plt
import seaborn as sns
from brave.api.utils.metaphlan_utils import get_abundance,get_metadata
from skbio.diversity import beta_diversity
from skbio.stats.distance import permanova
from skbio.stats.ordination import pcoa
from matplotlib.patches import Ellipse
import numpy as np
from brave.api.utils.metaphlan_utils import get_abundance_metadata
from sklearn.preprocessing import LabelEncoder  
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import StandardScaler
import scipy.stats as stats


def get_db_field():
    return ['control','treatment']




def parse_data(request_param,db_dict):
    abundance,metadata,groups = get_abundance_metadata(request_param,db_dict,['control','treatment'])
    df_merge = pd.merge(abundance,metadata,left_index=True,right_index=True)
    df_merge.to_pickle("test/df_merge.pkl")
    X = df_merge.drop('group', axis=1)
    y = df_merge['group']

    le = LabelEncoder()
    y = le.fit_transform(y)  # HC→0, SCZ→1  
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    param_grid = {
        'n_estimators': [100, 300, 500],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2],
        'max_features': ['sqrt', 'log2']
    }
    clf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(clf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X, y)

    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    mean_fpr = np.linspace(0, 1, 100)
    tprs = []
    aucs = []
    for train_idx, test_idx in cv.split(X, y):
        model = RandomForestClassifier(
            min_samples_leaf=grid_search.best_params_['min_samples_leaf'],
            max_features=grid_search.best_params_['max_features'], 
            n_estimators=grid_search.best_params_['n_estimators'],   # 树的数量  
            criterion='gini',    # 分裂标准（基尼指数）  
            max_depth=grid_search.best_params_['max_depth'],        # 单棵树最大深度  
            min_samples_split=grid_search.best_params_['min_samples_split'],# 节点最小分裂样本数  
            random_state=42)
        model.fit(X[train_idx], y[train_idx])
        y_proba = model.predict_proba(X[test_idx])[:, 1]

        fpr, tpr, _ = roc_curve(y[test_idx], y_proba)
        roc_auc = auc(fpr, tpr)
        aucs.append(roc_auc)

        # 插值 TPR 到统一的 FPR 上
        tpr_interp = np.interp(mean_fpr, fpr, tpr)
        tpr_interp[0] = 0.0
        tprs.append(tpr_interp)
    # 转为 numpy 数组
    tprs = np.array(tprs)
    mean_tpr = tprs.mean(axis=0)
    std_tpr = tprs.std(axis=0)
    mean_auc = np.mean(aucs)
    std_auc = np.std(aucs, ddof=1)
    ci_low, ci_high = stats.norm.interval(0.95, loc=mean_auc, scale=std_auc / np.sqrt(len(aucs)))

    # 置信区间带
    tprs_upper = np.minimum(mean_tpr + 1.96 * std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - 1.96 * std_tpr, 0)

    # breakpoint() 
    return (mean_fpr,mean_tpr,ci_low,ci_high,tprs_lower,tprs_upper,mean_auc),None
 
def parse_plot(data ,request_param):
    (mean_fpr,mean_tpr,ci_low,ci_high,tprs_lower,tprs_upper,mean_auc),a =data
    plt.figure()
    plt.plot(mean_fpr, mean_tpr, color='blue', label=f'Mean ROC(AUC: {mean_auc:.2f}, 95%CI: {round(ci_low,2)}-{round(ci_high,2)})')
    plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='blue', alpha=0.2)
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Cross-Validated ROC with 95% Confidence Interval')
    plt.legend(loc='lower right')
    plt.grid(False)
    return plt

# def parse_plot(data ,request_param):
#     pc_df = data['pc_df']
#     permanova_result = data['data']
#     pcoa_result = data['in_pcoa_result']
#     plt.figure(figsize=(7, 6))
#     sns.scatterplot(data=pc_df, x='PC1', y='PC2', hue='group', s=100, palette='Set2')
#     ax = plt.gca()
#     for g, df_g in pc_df.groupby('group'):
#         draw_confidence_ellipse(df_g['PC1'], df_g['PC2'], ax)
#     plt.xlabel(f"PC1 ({pcoa_result.proportion_explained[0]*100:.2f}%)")
#     plt.ylabel(f"PC2 ({pcoa_result.proportion_explained[1]*100:.2f}%)")
#     plt.title(f"Beta Diversity - PCoA (Bray-Curtis) PERMANOVA:{permanova_result['p-value']:.3f}")
#     return plt
# #     alpha_df = data
# #     plt.figure(figsize=(6, 6))
# #     # sns.boxplot(x='group', y='Shannon', data=alpha_df)
# #     # sns.swarmplot(x='group', y='Shannon', data=alpha_df, color='black')

# #     sns.boxplot(x='group', y='Shannon', data=alpha_df, 
# #                 palette="Set2",  # 配色方案
# #                 width=0.5,       # 箱体宽度
# #                 linewidth=2.5,
# #             showfliers=False
# #             )    # 
# #     sns.stripplot(x='group', y='Shannon', data=alpha_df,  # 叠加散点图
# #                 color='black', size=4, alpha=0.3)


# #     plt.title('Alpha Diversity (Shannon Index)')
# #     return plt
# def draw_confidence_ellipse(x, y, ax, edgecolor='black', facecolor='none', alpha=0.3):
#     if len(x) < 2:
#         return
#     cov = np.cov(x, y)
#     vals, vecs = np.linalg.eigh(cov)
#     order = vals.argsort()[::-1]
#     vals = vals[order]
#     vecs = vecs[:, order]

#     theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
#     width, height = 2 * np.sqrt(vals) * 2  # 2σ 对应约 95% 置信区间

#     ell = Ellipse((np.mean(x), np.mean(y)), width=width, height=height,
#                   angle=theta, edgecolor=edgecolor, facecolor=facecolor,
#                   linewidth=1.5, alpha=alpha)
#     ax.add_patch(ell)
