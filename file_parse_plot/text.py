import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import json
def parse_data(request_param):
    text = request_param['text']
    with open(text) as f:
        text = f.read()
    return text