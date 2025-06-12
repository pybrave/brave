import glob
import os
import json

def support_analysis_method():
    return "samtools_remove_hosts"

def get_json(file):
    return json.dumps({
        "fastq1":file,
        "fastq2":file.replace("_1.fastp.fastq.gz","_2.fastp.fastq.gz"),
        "html":file.replace("_1.fastp.fastq.gz",".fastp.html")
    })

def parse(dir_path):
    file_list = glob.glob(f"{dir_path}/*_1.fastp.fastq.gz")
    # /ssd1/wy/workspace2/test/test_workspace/result/V1.0/metawrap_assembly/test_s1/final_assembly.fasta
    # sample_name,software,content_type,content
    result_data = [(os.path.basename(file).replace("_1.fastp.fastq.gz",""),"fastp","json",get_json(file)) for file in file_list]
    return result_data
