from models.orm import SampleAnalysisResult
from config.db import get_db_session
from fastapi import HTTPException
import json
import pandas as pd 
def get_data(item):
    content = item.content #json.loads(item.content)
    return {
        "sample_key":item.sample_key,
        "fastq1":content['fastq1'],
        "fastq2":content['fastq2'],
    }

def get_db_field():
    return ['reads']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/ngs_sample_qc.nf"

def get_output_format():
    return [
        {
            "module":"fastp",
            "dir":"fastp",
            "analysis_method":"fastp_clean_reads"
        }
    ]
def parse_data(request_param,db_dict):
    reads = db_dict['reads']
    samples = [get_data(item) for item in reads]
    # df = pd.DataFrame(result)
    # samples = df.to_dict(orient="records")
    # genome_assembly = db_dict['genome_assembly']
    # # genome_assenbly_json = json.loads(genome_assenbly.content)
    # genome_annotation = db_dict['prokka']
    # # gff_json = json.loads(gff.content)
    
    result = {
        "samples":samples,
        
    }
    return result

 
  