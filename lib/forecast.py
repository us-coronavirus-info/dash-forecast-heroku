# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:28:20 2020

@author: SHAOQM
"""

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from model import expfit, ratetrend


## Get Data
#try: response
#except NameError: response = None
#
#if response is None:
#    try:
#        with open('data.json', 'r') as f:
#            response = json.load(f)    
#    except FileNotFoundError:
#        url = 'http://ncov.nosensor.com:8080/api/'
#        response = json.loads(requests.get(url).text)
#        with open('data.json', 'w') as f:
#            json.dump(response, f)
#    
#    
## Proince Data
#totprovdays = len(response['province'])
#provhist = {}
#
#for day in range(totprovdays):
#    daydata = response['province'][totprovdays-day-1]['ProvinceDetail']
#    for provdata in daydata:
#        prov = provdata['Province']
#        if not (prov in provhist):
#            provhist[prov] = [0] * totprovdays
#        provhist[prov][day] = provdata['Confirmed']
#
## Other Data
#lastDay = response['province'][0]['Time']
#otherData = {"lastDay": lastDay, "totDays": totprovdays}



with open('hist.json', 'r') as f:
    data = json.load(f)  

provhist = data['hist']
time = data['time']

# Other Data
lastDay = time[-1]
totprovdays = len(time)



otherData = {"lastDay": lastDay, "totDays": totprovdays}


# Get provinces over 100 cases
severeProv = []
provRes = {}
expfitdays = 18
sortedprovhist = sorted(provhist.items(),key=lambda a:a[1][-1], reverse=True)
for prov in sortedprovhist:
    if prov[1][-1]>100:
        name = prov[0]
        severeProv.append(name)
        provRes[name] = {'hist' :provhist[name]}
        para = expfit(provhist[name], name, expdays = expfitdays)
        # provRes[prov[0]] = {"cfactor": para[2]}
        provRes[name]['pred'] = {}
        for i in range(5):
            ratefitdays = totprovdays - i
            provRes[name]['pred'][ratefitdays] = ratetrend(provhist[name], para[2], name, ratefitdays)



# Return provinces over 100 cases
def getData(provhist = provhist):
    return (severeProv, provRes, otherData)


