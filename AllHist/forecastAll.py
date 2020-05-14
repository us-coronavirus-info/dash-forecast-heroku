# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:28:20 2020

@author: SHAOQM
"""

import requests
import json
from modelAll import fitModel
import matplotlib.pyplot as plt


thres = 5000
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

    # Get data
    url = r'https://charts.us-coronavirus.info/history.json'
    response = json.loads(requests.get(url, verify=True ).text)
    ushist['United States'] = response['confirmed_global']['hist']['US'][1:]
    for r in response['confirmed_US']['hist']:
        ushist[r] = response['confirmed_US']['hist'][r]

    dates = response['confirmed_US']['dates']

    sortedhist = sorted(ushist.items(),key=lambda a:a[1][-1], reverse=True)

    cnt = 0 # for testing
#    errorMap = {'header':[], 'data':[]}
    for state, hist in sortedhist:
        
        if hist[-1] < thres or state in ['Virgin Islands', 'unassigned']:
            continue
        print('Modeling ' + state)
        servereStates.append(state)
        
        # start from 3/1
        hist = hist[38:]
        R0hist, pred, bounds = fitModel(hist)

        dispDays = len(R0hist)
        stateErr =  []
        for i in range(dispDays):
            predIncr = pred[i][window] - hist[-dispDays+i]
            realIncr = hist[-dispDays+1+i] - hist[-dispDays+i]
            stateErr.append( (realIncr -predIncr) / predIncr)
#        errorMap['data'].append(stateErr)
#        errorMap['header'].append(state)

        # plt.figure()        
        # plt.plot(R0hist)
        # plt.show()
        
        stateRes[state] = {
            'dates': dates[-dispDays:],
            'R0hist': R0hist, 
            # 'pred': pred, 
            # 'hist': hist[-window-dispDays+1:], 
            # 'forecast': pred[-1][-predDays]-pred[-1][-predDays-1],
            # 'forecast': [
            #         bounds[-1]['lb'][-predDays] - hist[-1], 
            #         bounds[-1]['ub'][-predDays] - hist[-1],
            #         pred[-1][-predDays] - hist[-1], 
            #     ],
            'err': [None, *stateErr[:-1]],
            # 'bounds': bounds,
            }

        cnt += 1
        # if cnt == 1:
        #    break
    
    return stateRes


stateRes = updatedata()
with open('./summary.json', 'w') as f:
    json.dump(stateRes, f)
#plt.plot(stateRes['New York']['R0hist'])
#plt.bar(range(len(stateRes['New York']['err'][:-1])), stateRes['New York']['err'][:-1])