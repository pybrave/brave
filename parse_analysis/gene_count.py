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
    return ['genome_assembly','rna_seq','prokka']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/single_genome_rna.nf"

def parse_data(request_param,db_dict):
    analysis_result = db_dict['rna_seq']
    result = [get_data(item) for item in analysis_result]
    df = pd.DataFrame(result)
    samples = df.to_dict(orient="records")
    genome_assembly = db_dict['genome_assembly']
    # genome_assenbly_json = json.loads(genome_assenbly.content)
    genome_annotation = db_dict['prokka']
    # gff_json = json.loads(gff.content)
    
    result = {
        "samples":samples,
        "genome_assembly":{
            "analysis_key":genome_assembly.analysis_key,
            "fasta":genome_assembly.content['scaffolds']
        },
        "genome_gff":{
            "analysis_key":genome_annotation.analysis_key,
            "gff":genome_annotation.content['gff']
        }
    }
    return result

 
  



