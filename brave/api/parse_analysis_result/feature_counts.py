import glob
import os
import json 


def get_content(file):
    return json.dumps({
        "count":file,
        "log":f"{file}.summary"
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*/*.count")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace(".count",""),"featureCounts","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
