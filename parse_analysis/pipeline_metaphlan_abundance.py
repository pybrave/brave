from models.orm import SampleAnalysisResult
from config.db import get_db_session
from fastapi import HTTPException
import json
import pandas as pd 
import re
import os

def get_db_field():
    return ['bowtie2_align_metaphlan']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/pipeline_metaphlan_abundance.nf"

def get_output_format():
    return [
        {
            "module":"metaphlan_abundance",
            "dir":"metaphlan_sam",
            "analysis_method":"metaphlan_sam_abundance"
        }
    ]


regexes = {
    "unpaired_aligned_none": r"(\d+) \([\d\.]+%\) aligned 0 times",
    "unpaired_aligned_one": r"(\d+) \([\d\.]+%\) aligned exactly 1 time",
    "unpaired_aligned_multi": r"(\d+) \([\d\.]+%\) aligned >1 times",
    "paired_aligned_none": r"(\d+) \([\d\.]+%\) aligned concordantly 0 times",
    "paired_aligned_one": r"(\d+) \([\d\.]+%\) aligned concordantly exactly 1 time",
    "paired_aligned_multi": r"(\d+) \([\d\.]+%\) aligned concordantly >1 times",
    "paired_aligned_discord_one": r"(\d+) \([\d\.]+%\) aligned discordantly 1 time",
    "paired_aligned_discord_multi": r"(\d+) \([\d\.]+%\) aligned discordantly >1 times",
    "paired_aligned_mate_one": r"(\d+) \([\d\.]+%\) aligned exactly 1 time",
    "paired_aligned_mate_multi": r"(\d+) \([\d\.]+%\) aligned >1 times",
    "paired_aligned_mate_none": r"(\d+) \([\d\.]+%\) aligned 0 times",
}
def prase_bowte2(file):
    parsed_data = {}
    with open(file) as f:
        filename = os.path.basename(file).replace(".bowtie2.log","")
        parsed_data['sample_name'] = filename
        # print()
        for line in f.readlines():
            # print(line)
            for  k, r in regexes.items():
                match = re.search(r, line)
                if match:
                    parsed_data[k] = int( match.group(1))
                    # print(match.group(1))
                    # match.group(1)

    return parsed_data

def get_nreads(file):
    result = prase_bowte2(file)
    nreads = result['unpaired_aligned_none']+result['unpaired_aligned_one']+result['unpaired_aligned_multi']
    return nreads

def get_data(item):
    content = item.content #json.loads(item.content)
    return {
        "sample_key":item.sample_key,
        "bam":content['bam'],
        "nreads": get_nreads(content['log'] ) 
    }
def parse_data(request_param,db_dict):
    analysis_result = db_dict['bowtie2_align_metaphlan']
    samples = [get_data(item) for item in analysis_result]
    # log_list = [get_nreads(item.content['log'],item.sample_key ) for item in analysis_result]
    
    # df = pd.DataFrame(result)
    # samples = df.to_dict(orient="records")
    # genome_assembly = db_dict['genome_assembly']
    # # genome_assenbly_json = json.loads(genome_assenbly.content)
    # genome_annotation = db_dict['prokka']
    # gff_json = json.loads(gff.content)
    
    result = {
        "samples":samples,
        "stat_q":request_param['stat_q']
        # "genome_assembly":{
        #     "analysis_key":genome_assembly.analysis_key,
        #     "fasta":genome_assembly.content['scaffolds']
        # },
        # "genome_gff":{
        #     "analysis_key":genome_annotation.analysis_key,
        #     "gff":genome_annotation.content['gff']
        # },
        # "bowtie2_output":"bowtie2_RNA_mapping",
        # "fastp_output":"fastp_RNA"
    }
    return result

 
  



