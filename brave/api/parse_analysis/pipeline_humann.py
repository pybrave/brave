
from brave.api.models.orm import SampleAnalysisResult
from brave.api.config.db import get_db_session
from fastapi import HTTPException
import json
import pandas as pd 


def get_db_field():
    return ['reads','abundance']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/pipeline_humann.nf"

def get_output_format():
    return [
        {
            "module":"humann_profile",
            "dir":"humann",
            "analysis_method":"humann_profile"
        },
    ]
def parse_data(request_param,db_dict):
    reads = db_dict['reads']
    samples = [get_data(item) for item in reads]
    abundance_list = db_dict['abundance']
    abundance = [get_abundabce(item) for item in abundance_list]
    df_abundance = pd.DataFrame(abundance)
    df_samples = pd.DataFrame(samples)
    df = pd.merge(df_abundance,df_samples,on="sample_key")
    
    result = {
        "samples":df.to_dict(orient="records"),
        # "genome_index":request_param['genome_index']
    }
    return result

def get_abundabce(item):
    content = item.content #json.loads(item.content)
    return {
        "sample_key":item.sample_key,
        "profile":content['profile'],
    }
  
def get_data(item):
    content = item.content #json.loads(item.content)
    return {
        "sample_key":item.sample_key,
        "fastq1":content['fastq1'],
        "fastq2":content['fastq2'],
    }





