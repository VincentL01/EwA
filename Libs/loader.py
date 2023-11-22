import json

import logging
logger = logging.getLogger(__name__)

def hyploader(hyp_path):

    with open(hyp_path, 'r') as file:
        data = json.load(file)
        
    # convert values to int or float
    for key, value in data.items():
        data[key] = int(float(value))

    return data