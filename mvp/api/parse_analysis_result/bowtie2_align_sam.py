import glob
import os
import json 


def get_content(file):
    return json.dumps({
        "sam":file,
        "log":file.replace(".sam","")+".bowtie2.log"
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*.sam")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace(".sam",""),"bowtie2","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
