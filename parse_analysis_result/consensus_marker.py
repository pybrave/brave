import glob
import os
import json 


def get_content(file):
    return json.dumps({
        "json":file
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*/*.json.bz2")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace(".json.bz2",""),"strainphlan","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
