# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:22:53 2020

@author: SHAOQM
"""

import pandas as pd
import json

url = 'http://datanews.caixin.com/interactive/2020/pneumonia-h5/data/data2.csv'
raw = pd.read_csv(url)

data = {'hist':{}, 'time':raw['time'][2:-1].tolist()}
for col in raw.columns[1:]: 
    data['hist'][col] = pd.to_numeric(raw[col][2:-1]).tolist()


with open('../hist.json', 'w') as f:
    json.dump(data, f)    
