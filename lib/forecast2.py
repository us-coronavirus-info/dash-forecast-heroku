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



thres = 8000
window = 7 # also defined in model
dispDays = 15
predDays = 3
lastDay = None
servereStates = []
stateRes = {}

def updatedata():
    # Init
    stateRes = {}
    ushist = {}
    servereStates = []

    ushist['United States'] = []
    # Get data
    url = r'https://confirmedmap.us-coronavirus.info/date.json'
    response = json.loads(requests.get(url, verify=True ).text)
    for r in response:
        rec = r['records']
        for item in rec:
            if not (item['name'] in ushist):
                ushist[item['name']] = []
            ushist[item['name']].append(item['confirmedCount'])
        ushist['United States'].append(r['confirmedCount'])

    for h in ushist:
        ushist[h].pop()

    lastDay = response[-2]['day']

    sortedhist = sorted(ushist.items(),key=lambda a:a[1][-1], reverse=True)

    cnt = 0 # for testing
    errorMap = {'header':[], 'data':[]}
    for state, hist in sortedhist:
        
        if hist[-1] < thres or state in ['Virgin Islands', 'unassigned']:
            continue
        print('Modeling ' + state)
        servereStates.append(state)
        R0hist, pred, bounds = fitModel(hist)

        stateErr =  []
        for i in range(1, dispDays):
            predIncr = pred[i][window] - hist[-dispDays+i]
            realIncr = hist[-dispDays+1+i] - hist[-dispDays+i]
            stateErr.append( (realIncr -predIncr) / predIncr)
        errorMap['data'].append(stateErr)
        errorMap['header'].append(state)

        stateRes[state] = {
            'R0hist': R0hist, 
            'pred': pred, 
            'hist': hist[-window-dispDays+1:], 
            # 'forecast': pred[-1][-predDays]-pred[-1][-predDays-1],
            'forecast': [
                    bounds[-1]['lb'][-predDays] - hist[-1], 
                    bounds[-1]['ub'][-predDays] - hist[-1],
                    pred[-1][-predDays] - hist[-1], 
                ],
            'err':stateErr,
            'bounds': bounds,
            }

        cnt += 1
        # if cnt == 2:
        #     break
    
    with open(r'assets/ErrorMap.json', 'w') as f:
        json.dump(errorMap, f)
    return (servereStates, stateRes, lastDay, thres)




# Return provinces over thre cases
def getData():
    return (servereStates, stateRes, lastDay, thres)


