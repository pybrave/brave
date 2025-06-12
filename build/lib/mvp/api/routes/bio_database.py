from fastapi import APIRouter
import pandas as pd
import json

bio_database = APIRouter()

@bio_database.get("/fast-api/get_metaphlan_clade")
def get_metaphlan_clade():
    with open("/ssd1/wy/workspace2/nextflow-fastapi/databases/clade.json") as f:
        data = json.load(f)
    return data