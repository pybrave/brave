import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
def parse_data(request_param):
    file_path = request_param['file_path']
    df = pd.read_csv(file_path,sep=",")
    return json.loads(df.to_json(orient="records"))