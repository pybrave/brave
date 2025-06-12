
from mvp.api.models.orm import SampleAnalysisResult
from mvp.api.config.db import get_db_session
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
    return ['clean_reads']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/bowtie2_remove_host.nf"

def get_output_format():
    return [
        {
            "module":"bowtie2_align_unsorted",
            "dir":"bowtie2_align_host",
            "analysis_method":"bowtie2_align_host"
        }, {
            "module":"samtools_remove_hosts",
            "dir":"samtools_remove_hosts",
            "analysis_method":"samtools_remove_hosts"
        }
    ]
def parse_data(request_param,db_dict):
    reads = db_dict['clean_reads']
    samples = [get_data(item) for item in reads]

    
    result = {
        "samples":samples,
        "genome_index":request_param['genome_index']
    }
    return result

 
  






