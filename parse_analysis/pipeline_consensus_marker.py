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
    return "/ssd1/wy/workspace2/nextflow/pipeline_consensus_marker.nf"

def get_output_format():
    return [
        {
            "module":"consensus_marker",
            "dir":"sample2markers",
            "analysis_method":"consensus_marker"
        }
    ]




def get_data(item):
    content = item.content #json.loads(item.content)
    return {
        "sample_key":item.sample_key,
        "bam":content['bam'],
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

 
  



