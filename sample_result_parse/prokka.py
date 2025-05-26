import glob
import os
import json

def support_analysis_method():
    return "prokka"
def get_analysis_method():
    return "prokka"

def get_json(file):
    file_list = glob.glob(f"{file}/*")
    content = {item.split(".")[1]:item for item in file_list}
    return json.dumps(content)
def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    
    result_data = [(os.path.basename(file),"prokka","json",get_json(file)) for file in file_list]
    # print(result_data)
    # print(file_list)
    return result_data
