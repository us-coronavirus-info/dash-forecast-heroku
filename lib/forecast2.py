# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:28:20 2020

@author: SHAOQM
"""

import requests
import json
import numpy as np
from scipy.optimize import curve_fit
from .model2 import fitModel



thres = 500
window = 7 # also defined in model
dispDays = 7
predDays = 3
lastDay = None
servereStates = []
stateRes = {}

def updatedata():
    # Init
    stateRes = {}
    ushist = {}
    servereStates = []

    # Get data
    url = r'https://confirmedmap.us-coronavirus.info/date.json'
    response = json.loads(requests.get(url, verify=False ).text)
    for r in response:
        rec = r['records']
        for item in rec:
            if not (item['name'] in ushist):
                ushist[item['name']] = []
            ushist[item['name']].append(item['confirmedCount'])

    for h in ushist:
        ushist[h].pop()

    lastDay = response[-2]['day']

    sortedhist = sorted(ushist.items(),key=lambda a:a[1][-1], reverse=True)

    cnt = 0 # for testing
    for state, hist in sortedhist:
        
        if hist[-1] < thres or state in ['Virgin Islands', 'unassigned']:
            continue

        servereStates.append(state)
        R0hist, pred = fitModel(hist)
        stateRes[state] = {'R0hist': R0hist, 'pred': pred, 'hist': hist[-window-dispDays+1:], 'forecast': pred[-1][-predDays]-pred[-1][-predDays-1]}

        cnt += 1
        # if cnt == 2:
        #     break

    return (servereStates, stateRes, lastDay)




# Return provinces over thre cases
def getData():
    return (servereStates, stateRes, lastDay)


