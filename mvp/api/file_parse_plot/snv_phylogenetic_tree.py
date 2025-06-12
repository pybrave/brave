import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

def get_db_field():
    return ['sites']


def read_breseq(file):
    df = pd.read_csv(file,sep="\t")
    return df

def fill_ref_seq(x):
    ref_seq = x['ref_seq']
    for index,value in x.items():
        if pd.isna(value):
            x[index]= x['ref_seq']
    return x

def convert_dataframe_to_phy(df):
    num_samples = df.shape[0]
    num_sites = df.shape[1] - 1  # 除去 Sample 列

    phy_lines = [f"{num_samples} {num_sites}"]
    for _, row in df.iterrows():
        sample_name = str(row.iloc[0]).ljust(10)[:10]  # PHYLIP 要求名字不超过10字符
        snv_string = ''.join(row.iloc[1:].astype(str).tolist())
        phy_lines.append(f"{sample_name} {snv_string}")
    return phy_lines


def parse_data(request_param,db_dict):
    sites = db_dict['sites']
    df_list = [read_breseq(item.content['annotated_tsv']) for item in sites]
    df = pd.concat(df_list)
    df = df.query("type=='SNP'")
    df_long  = df[['position','title','ref_seq','new_seq','gene_name','snp_type','gene_position','genes_promoter']]
    df_wide = df_long.pivot(index=['gene_name','position','ref_seq','snp_type'], columns='title', values='new_seq').reset_index(level='ref_seq')
    df_matrix = df_wide.apply(lambda x: fill_ref_seq(x), axis=1)

    distance_vector = pdist(df_matrix.T, lambda u, v: (u != v).sum())
    distance_matrix = squareform(distance_vector)
    df_distance = pd.DataFrame(distance_matrix,columns=df_matrix.T.index,index=df_matrix.T.index).rename_axis(None)

    phy_lines = convert_dataframe_to_phy(df_matrix.T.reset_index('title'))
    # return {"phy_lines":'\n'.join(phy_lines),"data":df_distance,"in_distance_vector":distance_vector,"in_df_matrix":df_matrix}
    phy_lines_str = '\n'.join(phy_lines)
    return df_distance,phy_lines_str,(distance_vector,df_matrix)
    # pass

def parse_plot(data ,request_param):
    df_distance,phy_lines_str,(distance_vector,df_matrix) = data

    Z = linkage(distance_vector, method='average')
    plt.figure(figsize=(10, 5))
    dendrogram(Z, labels=df_matrix.T.index.tolist(),orientation='left')
    plt.title("UPGMA Tree")

    # pass
    return plt