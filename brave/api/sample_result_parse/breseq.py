import glob
import os
import json

def support_analysis_method():
    return "breseq"
def get_analysis_method():
    return "breseq"

def get_key(item):
    key = item.split("/")[len(item.split("/"))-1].replace(".","_")
    if "_1_" in key:
        key = "fastq1"
    elif "_2_" in key:
        key = "fastq2"
    return key

def get_json(file):
    index_html = f"{file}/output/index.html"
    if not os.path.exists(index_html):
        index_html = f"error: not exist {index_html}"

    file_list = glob.glob(f"{file}/data/*")
    content = {get_key(item):item for item in file_list}
    content.update({"index_html":index_html})
    with open(f"{file}/data/reference.name","r") as f:
        first_line = f.readlines()[0].strip()
        content.update({"reference":first_line})
    return json.dumps(content)
def parse(dir_path):
    file_dir_list = glob.glob(f"{dir_path}/*")
    # sample_name,software,content_type,content
    result_data =[]
    for file_dir in file_dir_list:
        file_list = glob.glob(f"{file_dir}/*")
        # analysis_key,sample_name,software,content_type,content
        result_data = result_data+ [(os.path.basename(file_dir)+"-"+os.path.basename(file),os.path.basename(file),"breseq","json",get_json(file)) for file in file_list]
    # print(result_data)
    # print(file_list)
    return result_data
