import matplotlib.pyplot as plt
import base64
from Bio import Phylo
import matplotlib.pyplot as plt
import pandas as pd
import json

def parse_data(request_param):
    best_tree = request_param['best_tree']
    with open(best_tree) as f:
        best_tree = f.read()
    tree_pairwisedists = request_param['tree_pairwisedists']
    df = pd.read_csv(tree_pairwisedists,sep="\t", header=None,names=["sample 1","sample 2","phylogenetic distances"])
    return df, best_tree


def parse_plot(data ,request_param):
  # 创建一个新的绘图区域，设置图像大小（单位：英寸）
    fig = plt.figure(figsize=(10, 12))  # 例如：宽10，高8
    axes = fig.add_subplot(1, 1, 1)
    best_tree = request_param['best_tree']
    tree = Phylo.read(best_tree, "newick")
    # 绘图
    Phylo.draw(tree, axes=axes)
    return plt