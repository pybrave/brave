import glob
import os
import json

def support_analysis_method():
    return "eggnog"
def get_analysis_method():
    return "eggnog"

def get_json(file):
    file_list = glob.glob(f"{file}/*")
    file_list = [x for x in file_list if "input.faa" not in x]
    content = {item.split(".")[2]:item for item in file_list}
    with open(f"{file}/input.faa")  as f:
        line = f.readline().strip()
        content.update({"input_faa":line})
    return json.dumps(content)
def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    
    result_data = [(os.path.basename(file),"eggnog","json",get_json(file)) for file in file_list]
    # print(result_data)
    # print(file_list)
    return result_data
