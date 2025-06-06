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
    best_tree = request_param['best_tree']
    tree = Phylo.read(best_tree, "newick")
    # 绘图
    Phylo.draw(tree)
    return plt