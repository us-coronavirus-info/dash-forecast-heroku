import numpy as np
from scipy.optimize import curve_fit

def exponenial_func(x, a, b, c):
    return a*np.exp(b*(x-c)) - a

def jac(x, a, b, c):
    return np.array([np.exp(b*(x-c))-1, a*np.exp(b*(x-c))*(x-c), a*np.exp(b*(x-c))*(-b)]).transpose()


def expfit(cityhistory, cityname = None, expdays = 0):
    totdays = len(cityhistory)
    if cityhistory[0]:
        nonzeroidx = 0
    else:
        nonzeroidx = -1
        
    for i in range(1,totdays):
        if cityhistory[i] == 0:
            cityhistory[i] = cityhistory[i-1]
        if nonzeroidx==-1 and cityhistory[i]:
            nonzeroidx = i
    enddays = 0
    if expdays:
        enddays = totdays - expdays
    
    x = np.array(range(totdays))
    
    sigmafactor = 1
    while True:
        try:
            sigma = [float(s+1)**sigmafactor for s in range(totdays)]
            popt, pcov = curve_fit(exponenial_func, x[nonzeroidx:totdays-enddays], cityhistory[nonzeroidx:totdays-enddays], p0=(10, 0.2, 0), jac=jac, sigma = sigma[:totdays-nonzeroidx-enddays])
            break
        except RuntimeError:
            sigmafactor -= 0.1
            if not sigmafactor:
                print('DEAD')
                break
            
    yy = exponenial_func(x, *popt)
    yy[yy < 0] = 0
    
    
    # if cityname:
    #     print(cityname)
        
    return popt




def getdifffunc(c):
    def diff_func(x, a, b):
        return a*(1-np.exp(-b*(x-c)))
    return diff_func

def getdiffjac(c):
    def diff_jac(x, a, b):
        return np.array([(1-np.exp(-b*(x-c))), a*(np.exp(-b*(x-c)))*(x-c)]).transpose()
    return diff_jac

def ratetrend(hist,c, name = None, fitdays = None, preddays =5, dispconf = True):
    
    hist = hist[:fitdays]
        
    totdays = len(hist)
    logdiff = np.log(np.diff(hist))
    x = np.array(range(1,len(logdiff)+1))
    x = x[logdiff>-100]
    logdiff = logdiff[logdiff>-100]
    
    
    # exponential
    sigma = [1/(a+1)**1 for a in range(len(logdiff))]
    newdifffunc = getdifffunc(c)
    newdiffjac = getdiffjac(c)
    popt, pcov = curve_fit(newdifffunc, x, logdiff, p0=(10,0.2), jac=newdiffjac, sigma=sigma, absolute_sigma=True)
    conf = np.sqrt(np.diagonal(pcov))
#    if name:
#        plt.text((plt.axis()[0]+plt.axis()[1])*0.45-len(cityname)*0.05,  plt.axis()[3]*0.35, cityname, fontsize=32)
#        plt.text((plt.axis()[0]+plt.axis()[1])*0.46-len(cityname)*0.05,  plt.axis()[3]*0.25, f'时间常数： {round(1/b,1)}', fontsize=12)    
    

    # Polynomial
    coeff = np.polyfit([c,*x], [0,*logdiff], 2, w=[(a+1)**0.5 for a in range(len(logdiff)+1)])
#    coeff = np.polyfit([c,*x], [0,*logdiff], 2)
    p = np.poly1d(coeff)
    
    pred = [hist[-1]]
    pred2 = [hist[-1]]
    if dispconf:
        pred2u = [hist[-1]]
        pred2l = [hist[-1]]
    totdays = len(hist)
    predx = range(totdays, totdays+preddays)
    
    for i in predx:
        pred.append(pred[-1] + (np.exp(p(i))))
        pred2.append(pred2[-1] + (np.exp(newdifffunc(i,*popt))))
        if dispconf:
            pred2u.append(pred2u[-1] + (np.exp(newdifffunc(i,*(popt+conf)))))
            pred2l.append(pred2l[-1] + (np.exp(newdifffunc(i,*(popt-conf)))))
        
    
    
    
    # Prediction
    lastidx = c
    lastval = 0
    lastval2 = 0
    est = [0]*totdays
    est2 = [0]*totdays
    
    for i in range(totdays):
        if i<lastidx:
            est[i] = 0
            est2[i] = 0
            continue
        est[i] += lastval + np.exp(p(i))
        lastval = est[i]
        est2[i] += lastval2 + np.exp(newdifffunc(i,*popt))
        lastval2 = est2[i]
        
    return [[*est[:-1],*pred], [*est2[:-1],*pred2], pred2u, pred2l]
    # if dispconf:
    #     plt.fill_between([totdays-1,*predx], pred2u,pred2l, alpha = 0.3, facecolor='blue')
    
    # if validate:
    #     plt.plot(range(fitdays,fitdays+len(validate)), validate,'rx',)

