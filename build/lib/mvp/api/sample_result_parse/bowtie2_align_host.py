import glob
import os
import json 

def support_analysis_method():
    return "bowtie2_align_host"

def get_content(file):
    return json.dumps({
        "bam":file,
        "log":file.replace(".bam","")+".bowtie2.log"
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*.bam")
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace(".bam",""),"bowtie2","json",get_content(file)) for file in file_list]
    # print(result_data)
    return result_data
