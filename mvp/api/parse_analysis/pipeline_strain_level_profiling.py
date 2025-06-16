from mvp.api.models.orm import SampleAnalysisResult
from mvp.api.config.db import get_db_session
from fastapi import HTTPException
import json
import pandas as pd 
import re
import os
from mvp.api.utils.metaphlan_utils import get_abundance,get_last_num

def get_db_field():
    return ['consensus_marker','assembly_genome','samples_abundance']

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
    samples = [item.content['json'] for item in consensus_marker]
    clade = {}
    if "clade" in request_param and len(request_param['clade']) >0:
        clade = request_param['clade']
    elif  "samples_abundance" in db_dict:
        samples_abundance = db_dict['samples_abundance']
        abundance = get_abundance(samples_abundance)
        abundance = abundance[(abundance!=0).sum(axis=1)>3]
        abundance = abundance.reset_index(['clade_name','taxonomy','rank']).reset_index(drop=True).query("rank=='SGB'")[['clade_name']]
        abundance['SGB'] = abundance['clade_name'].apply(lambda x : get_last_num(x,1))
        abundance['species'] = abundance.apply(lambda x : get_last_num(x['clade_name'],2)+"_"+x['SGB'],axis=1)
        abundance.to_dict(orient="records")
        abundance = abundance[['SGB','species']].rename({'SGB':"value","species":"label"},axis=1)
        clade = abundance.to_dict(orient="records")
    result = {
        "samples":samples,
        "clade":clade,
        
    }
    if "assembly_genome" in db_dict:
        assembly_genome = db_dict['assembly_genome']
        result.update({"reference":assembly_genome.content['scaffolds']})
    return result

 
  



