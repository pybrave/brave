import glob
import os
import json 


def get_content(file):
    best_tree = glob.glob(f"{file}/RAxML_bestTree.*.StrainPhlAn4.tre")[0]
    tree_pairwisedists = glob.glob(f"{file}/*_tree_pairwisedists.tsv")[0]
    return json.dumps({
        "best_tree":best_tree,
        "tree_pairwisedists":tree_pairwisedists,
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file),"strainphlan","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
