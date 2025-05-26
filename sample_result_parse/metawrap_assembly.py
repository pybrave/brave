import glob
import os

def support_analysis_method():
    return "metawrap_assembly"


def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    # /ssd1/wy/workspace2/test/test_workspace/result/V1.0/metawrap_assembly/test_s1/final_assembly.fasta
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file),"metawrap","file",f"{file}/final_assembly.fasta") for file in file_list]
    return result_data
