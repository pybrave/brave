import glob
import os
import json


# def get_json(file):
#     return json.dumps({
#         "fastq1":file,
#         "fastq2":file.replace("_host_removed_R1.fastq.gz","_host_removed_R2.fastq.gz")
#     })

def parse(dir_path,analysis):
    # file_list = glob.glob(f"{dir_path}/*_host_removed_R1.fastq.gz")
    # # /ssd1/wy/workspace2/test/test_workspace/result/V1.0/metawrap_assembly/test_s1/final_assembly.fasta
    # # sample_name,software,content_type,content
    # result_data = [(os.path.basename(file).replace("_host_removed_R1.fastq.gz",""),"samtools","json",get_json(file)) for file in file_list]
    return []
