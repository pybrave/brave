import glob
import os
import json 


def get_content(file,suffix_list):
    res = {}
    for k,v in suffix_list.items():
        res.update({k:f"{file}{v}"})
    return json.dumps(res)

def parse(dir_path,software,analysis,suffix_list):
    file_list = glob.glob(f"{dir_path}/*")

    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file),software,"json",get_content(file,suffix_list)) for file in file_list]
    # print(result_data)
    # return result_data
    return result_data
