import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
def parse_data(request_param):
    file_path = request_param['file_path']
    df = pd.read_csv(file_path,sep="\t",comment="#")
    return df


def parse_plot(data ,request_param):
    df_annotation = data
    df_annotation = df_annotation.query("ftype!='gene'").rename({"gene":"gene_name"},axis=1)
    df_annotation['product'] = df_annotation['product'].replace('hypothetical protein', pd.NA)
    non_nan_counts  = df_annotation[['locus_tag','gene_name','EC_number','COG','product']].notna().sum()
    ax = non_nan_counts.plot(kind='bar', color='skyblue')
    for i, value in enumerate(non_nan_counts):
        ax.text(i, value + 0.1, str(value), ha='center', va='bottom')
    plt.ylabel("Number of gene")
    # plt.title("Non-NaN Values per Column")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt
