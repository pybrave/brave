import pandas as pd
from functools import reduce
from utils.metaphlan_utils import get_abundance
def get_db_field():
    return ['metaphlan_sam_abundance']


def parse_data(request_param,db_dict):
    metaphlan_sam_abundance = db_dict['metaphlan_sam_abundance']
    df = get_abundance(metaphlan_sam_abundance)
    df = df.reset_index()
    # df.to_pickle("test/test.pkl")

    return {"data":df}

