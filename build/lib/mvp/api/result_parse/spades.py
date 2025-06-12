import glob
import os

def support_analysis_name():
    return "spades"

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*")
    result_data = [(os.path.basename(file).replace(".sam",""),"spades","sam",f"{file}",file.replace(".sam",".bowtie2.log")) for file in file_list]
    # print(result_data)
    return result_data
