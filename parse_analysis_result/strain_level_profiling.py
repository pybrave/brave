import glob
import os
import json 


def get_content(file,analysis):
    best_tree = glob.glob(f"{file}/RAxML_bestTree.*.StrainPhlAn4.tre")[0]
    tree_pairwisedists = glob.glob(f"{file}/*_tree_pairwisedists.tsv")[0]
    request_param = json.loads(analysis.request_param)

    return json.dumps({
        "best_tree":best_tree,
        "tree_pairwisedists":tree_pairwisedists,
        "reference":request_param['assembly_genome']['label']
    })

def parse(dir_path,analysis):
    file_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file),"strainphlan","json",get_content(file,analysis)) for file in file_list]
    # print(result_data)
    return result_data
