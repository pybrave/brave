import glob
import os
import json

def support_analysis_method():
    return "tgs_individual_assembly"
def get_analysis_method():
    return "tgs_individual_assembly"

# def get_json(file):
#     scaffolds = f"{file}/scaffolds.fasta"
#     if not os.path.exists(scaffolds):
#         scaffolds = f"error: not exist {scaffolds}"
#     log =  f"{file}/spades.log"
#     if not os.path.exists(log):
#         log = f"error: not exist {log}"
#     content = {
#         "scaffolds":scaffolds,
#         "log":log

#     }
#     return json.dumps(content)
def get_content(file):
    content = {
        "scaffolds":file
    }
    return json.dumps(content)
def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*.fa")
    # sample_name,software,content_type,content
    # analysis_key,software,content_type,content
    
    result_data = [(os.path.basename(file).replace("S-1-1.all.assembly.fa","OSP-3-PACBIO-HIFI"),"copy","json",get_content(file)) for file in file_list]
    result_data.append(("OCF-1-PACBIO-HIFI","copy","json",get_content("/ssd1/wy/workspace2/leipu/leipu_workspace2/output/genomes/OCF-1-PACBIO-HIFI/OCF-1-PACBIO-HIFI.fasta")))
    # print(result_data)
    # print(file_list)
    return result_data
