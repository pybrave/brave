from brave.api.utils.metaphlan_utils import get_abundance_metadata
import pandas as pd
import matplotlib.pyplot as plt


def get_db_field():
    return ['sites1','sites2']

def get_abundance_prev(request_param,db_dict,groups):
    abundance0,metadata,groups = get_abundance_metadata(request_param,db_dict,groups)
    # df_merge = pd.merge(metadata,abundance,left_index=True, right_index=True).reset_index().set_index(['index'])
    # control_df = df_merge.query("group==@control_group")
    sites1= groups['sites1']
    sites2= groups['sites2']
    abundance = abundance0.T
    abundance[sites1]  = abundance[metadata.query("group==@sites1").index].apply(lambda x: sum(x!=0)/len(x)*100 ,axis=1)
    abundance[sites2]  = abundance[metadata.query("group==@sites2").index].apply(lambda x: sum(x!=0)/len(x)*100 ,axis=1)
    abundance_prev = abundance[[sites1,sites2]]
    abundance_prev['type'] = abundance_prev.apply(lambda x: set_type(x[sites1],x[sites2],sites1,sites2),axis=1)
    abundance_prev = abundance_prev.reset_index()
    return abundance_prev
def parse_data(request_param,db_dict):
    abundance_prev = get_abundance_prev(request_param,db_dict,['sites1','sites2'])
    # abundance_prev = abundance[['prev']]
    # df_merge = pd.merge(metadata,abundance_prev,left_index=True, right_index=True).reset_index().set_index(['index'])
    return abundance_prev

def pie_plot(data):
    plt.figure(figsize=(8, 6))
    data.plot.pie(autopct='%.1f%%', figsize=(6, 6), startangle=90)
    plt.ylabel('')
    return plt
def bar_polt(data):
    plt.figure(figsize=(8, 6))
    ax = data.plot(kind='bar', figsize=(6,4), color='skyblue')
    for i, v in enumerate(data):
        ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=10)
    return plt
    # 设置标题和标签
    # plt.title('类别数量柱状图')
    # plt.ylabel('数量')
    # plt.xlabel('类别')

def parse_plot(data ,request_param):
    abundance_prev = data
    prev_data = abundance_prev['type'].value_counts()
    pie_plt = pie_plot(prev_data)
    bar_plt = bar_polt(prev_data)
    return [pie_plt,bar_plt]



def set_type(control_prev, treatment_prev,control_group,treatment_group):
    if control_prev>= 10 and treatment_prev>=10:
        return f"Prevalent in both sites"
    elif control_prev>= 10 and treatment_prev<10:
        return f"Prevalent in {control_group}"
    elif control_prev< 10 and treatment_prev>=10:
        return f"Prevalent in {treatment_group}"
    else:
        return "Not prevalent in either sites"