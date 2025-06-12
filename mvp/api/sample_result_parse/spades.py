import glob
import os
import json

def support_analysis_method():
    return "spades"
def get_analysis_method():
    return "ngs-individual-assembly"

def get_json(file):
    scaffolds = f"{file}/scaffolds.fasta"
    if not os.path.exists(scaffolds):
        scaffolds = f"error: not exist {scaffolds}"
    log =  f"{file}/spades.log"
    if not os.path.exists(log):
        log = f"error: not exist {log}"
    content = {
        "scaffolds":scaffolds,
        "log":log

    }
    return json.dumps(content)
def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    
    result_data = [(os.path.basename(file),"spades","json",get_json(file)) for file in file_list]
    # print(result_data)
    # print(file_list)
    return result_data
