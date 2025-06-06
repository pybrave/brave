from models.orm import SampleAnalysisResult
from config.db import get_db_session
from fastapi import HTTPException
import json
import pandas as pd 
import re
import os

def get_db_field():
    return ['consensus_marker','assembly_genome']

def get_script():
    return "/ssd1/wy/workspace2/nextflow/pipeline_strain_level_profiling.nf"

def get_output_format():
    return [
        {
            "module":"strain_level_profiling",
            "dir":"strainphlan",
            "analysis_method":"strain_level_profiling"
        }
    ]

# def get_data(item):
#     content = item.content #json.loads(item.content)
#     return {
#         "sample_key":item.sample_key,
#         "json":content['json'],
#     }
def parse_data(request_param,db_dict):
    consensus_marker = db_dict['consensus_marker']
    assembly_genome = db_dict['assembly_genome']
    samples = [item.content['json'] for item in consensus_marker]

    
    result = {
        "samples":samples,
        "reference":assembly_genome.content['scaffolds'],
        "clade":request_param['clade']

    }
    return result

 
  



