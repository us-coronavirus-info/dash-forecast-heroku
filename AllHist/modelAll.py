import numpy as np
import math
import requests
from scipy.optimize import curve_fit
from scipy.integrate import odeint
from scipy.optimize import minimize
from scipy.stats.distributions import  t


window = 7 
dispDays = 15
predDays = 3

def expfunc(x, a, b, c):
    return a*(1 - np.exp(-b*(x-c)))

def jac(x, a, b, c):
    return np.array([1 - np.exp(-b*(x-c)), a*(x-c)*np.exp(-b*(x-c)), -a*b*np.exp(-b*(x-c))]).transpose()

# fit a curve to estimate dy and ddy
# W = 1, weight the first most important, W = 2, the last most important
def expfit(x, y, W = 1):
    try:
        x = x - len(x) * (W < 0)
        sigmafactor = 0.5 * W
        sigma = [float(s+1)**sigmafactor for s in range(window)]
        # sigma[0] = sigma[-1]/2
        popt, pcov = curve_fit(expfunc, x, y, p0=(10000, 0.2, 0), jac=jac, sigma = sigma)

        a, b, c = popt
        y0 = math.exp(a*(1-math.exp(b*c)))
        dlogy0 =  a*b*math.exp(b*c)
        dy0 = y0 * dlogy0
        ddy0 = y0 * dlogy0**2 + y0 * dlogy0 * (-b)
    except RuntimeError:
        # In case first order system response doesn't fit, use linar fit
        coef = np.polyfit(x, y, 1)
        a, b = coef
        y0 = math.exp(b)
        dy0 = a * y0
        ddy0 = a * dy0
    return dy0, ddy0


def fitModel(hist):

    
    hist0 = np.array(hist)
    hist0 = np.log(hist0[hist0>0])
    days = len(hist0)
   
    R0hist = []
    pred = []
    bounds = []

    # fit data within window size
    for i in range(days - window + 1): 
        x = np.arange(window)
        y = hist0[i:i+window]

        y0 = math.exp(y[0])
        dy0, ddy0 = expfit(x, y, W = 1)
        
        # SEIR model parameter assumpitons
        DE = 6.1
        DI = 1.4
        
        y = np.exp(y)
        
        def ode(yy, t, R0):
            E,I,C = yy
            return [R0/DI*I-E/DE, E/DE-I/DI, E/DE]
    
        def SEIR_modelode(R0):
            sol = odeint(ode, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,))
            sse = 0
            for i in range(len(x)):
                sse += ((y[i]-sol[i][2])*(i+1)**0)**2
            return sse       

        def SEIR_modelode_ddy0(para):
            R0, ddy0 = para
            sol = odeint(ode, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,))
            sse = 0
            for i in range(len(x)):
                sse += ((y[i]-sol[i][2])*(i+1)**0)**2
            return sse       

        def SEIR_modelode_I0(I0):
            sol = odeint(ode, [dy0*DE, I0 ,y0], x, args=(R0,))
            sse = 0
            for i in range(len(x)):
                sse += ((y[i]-sol[i][2])*(i+1)**0)**2
            return sse  

        def odefR(yy, t, R0, k):
            E,I,C = yy
    #        R = R0*(1 + a*np.exp(-b*t))
            R = R0 + k*t
            
            return [R/DI*I-E/DE, E/DE-I/DI, E/DE]
        
        def SEIR_modelodefR(para):
            
            R0, k = para
            sol = odeint(odefR, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,k))
            sse = 0
            for i in range(len(x)):
                sse += ((y[i]-sol[i][2])*(i+1)**0.5)**2
            
            return sse   

# Fixed R0
        res = minimize(SEIR_modelode, 2, method='BFGS', #'nelder-mead',
                       tol= 1e-8, options={'disp': False})
        [R0] = res.x
        
        # Model Validation
        if R0 > 0:
            x = np.arange(window + predDays)
            sol = odeint(ode, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,))
        else:
            R0 = 0
            res = minimize(SEIR_modelode_I0, dy0, method='BFGS', #'nelder-mead',
                tol= 1e-8, options={'disp': False})
            [I0] = res.x
            x = np.arange(window + predDays)
            sol = odeint(ode, [dy0*DE, I0 ,y0], x, args=(R0,))

        yy = [a[2] for a in sol]
        yy[window:] += y[-1] - yy[window-1]


# # Fit R0 and initial ddy0
#         res = minimize(SEIR_modelode_ddy0, [2, ddy0], method='BFGS', #'nelder-mead',
#                        tol= 1e-8, options={'disp': False})
#         print(res.x)
#         [R0,ddy0] = res.x
#         if R0 < 0:
#             R0 = 0
#         # Model Validation
#         x = np.arange(window + predDays)
#         sol = odeint(ode, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,))
#         yy = [a[2] for a in sol]
#         yy[window:] += y[-1] - yy[window-1]

# R0 as a Linear function
        # res = minimize(SEIR_modelodefR, [3,0], method='BFGS', #'nelder-mead',
        #                tol= 1e-8, options={'disp': False})
        # R0, k = res.x
        # # Model Validation
        # x = np.arange(window + predDays)
        # sol = odeint(odefR, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,k))
        # yy = [a[2] for a in sol]
        # yy[window:] += y[-1] - yy[window-1]
        

# Confidence Interval
        # alpha = 0.05 # 95% confidence interval = 100*(1-alpha)
        # dof = window- 1 # number of degrees of freedom
        # # student-t value for the dof and confidence level
        # tval = t.ppf(1.0-alpha/2., dof) 
        # sigma = res.hess_inv[0][0] ** 0.5
        # fac = sigma*tval 
        # print(fac, tval)

# Pred from last point
        # y0 = y[-1]
        # dy0, ddy0 = expfit(x, np.log(y), W = -1)
        # x = np.arange(predDays+1)
        # sol = odeint(ode, [dy0*DE, (ddy0*DE+dy0)/R0*DI ,y0], x, args=(R0,))
        # yy[-predDays] = sol[-predDays][2]


        R0hist.append(R0)
        pred.append(yy)

#  Vary R0 by trend
        # if i==days - window:
        #     xb = np.arange(window)
        #     coef = np.polyfit(range(3), R0hist[-3:], 1)
        #     solb = odeint(ode, sol[1], xb, args=(R0+coef[0],))
        #     pred[-1][window] = solb[-1][2]

#  Vary R0 by bound
        xb = np.arange(window + predDays-1)
        lb = odeint(ode, sol[1], xb, args=(max(R0-max(R0*0.1,0.1), 0),))
        ub = odeint(ode, sol[1], xb, args=(R0+(max(R0*0.05,0.05)),))
        bounds.append({
            "ub":[a[2] for a in ub[-predDays:]],
            "lb":[a[2] for a in lb[-predDays:]]
            })

    return R0hist, pred, bounds
        
        
        