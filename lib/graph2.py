
import colorlover as cl
import plotly.graph_objs as go
import numpy as np


# Colorscale
#    bright_cscale = [[0, "#ff3700"], [1, "#0b8bff"]]
cscale = [
    (0, "#ffffff"),
    (0.125, "#FDEBCF"),
    (0.25, "#FFE0D7"),
    (0.375, "#ffe7dc"),
    (0.5, "#ffb199"),
    (0.625, "#E55A4D"),
    (0.75, "#CB2A2E"),
    (1, "#6F161D"),
]
window = 7
predDays = 3
dispDays = 7

def generateGraph(name, dates, data, totDays, valDays=0):

    # Prepare Data
    xhist = dates[:-predDays]
    yhist = np.array(data['hist'])

    xfit = dates[totDays-window-valDays-predDays:totDays-valDays-predDays]
    yfit = data['pred'][dispDays - valDays - 1][:window]
    
    xpred = dates[totDays-valDays-predDays-1:totDays-valDays]
    ypred = [yhist[-valDays-1], *data['pred'][dispDays - valDays - 1][window:]]
    
    xR0 = dates[-window-predDays:-predDays]
    yR0 = data['R0hist']
    
    # Plot 
    # sizefactor = 1 if name in ['湖北省','全国','湖北'] else 1
    sizefactor = 3
    tracehist = go.Scatter(
        x=xhist,
        y=yhist,
        mode="markers",
        name="Confirmed Cases",
        line=None,
        marker=dict(size=np.log10(yhist+1)*sizefactor, color='#E55A4D',
                line=dict(
                    color='#000',
                    width=0
                ),),
    )

    # tracevali = go.Scatter(
    #     x=xvali,
    #     y=yvali,
    #     mode="markers",
    #     name="验证确诊数据",
    #     marker=dict(
    #             size=np.log10(yvali+1)*sizefactor, 
    #             color='#CB2A2E',
    #             line=dict(
    #                 color='#000',
    #                 width=2
    #             ),
    #         ),
    # )    
   
                
    # # Polinimal Lower Bound
    # tracepred0 = go.Scatter(
    #     x=xpredb,
    #     y=ypred0,
    #     mode="lines",
    #     name="多项式预测下限区间",
    #     line = dict(dash='dash',color='GoldenRod'),
    #     showlegend=False
    # )     
    
    # tracepred0shade = go.Scatter(
    #     x=xpredb,
    #     y=ypred[-predDays-1:],
    #     mode="none",
    #     fill='tonexty',
    #     name="多项式预测下限区间",
    #     fillcolor="rgba(218,165,32,0.4)",
    # )    
    
    
    tracefit = go.Scatter(
        x=xfit,
        y=yfit,
        mode="lines",
        name="Model Fitting",
        line = dict(dash='dash',color='Violet'),
    ) 
    
    tracepred = go.Scatter(
        x=xpred,
        y=ypred,
        mode="lines",
        name="Model Prediction",
        line = dict(dash='dash',color='DeepSkyBlue'),
    ) 
    
    traceR0 = go.Scatter(
        x = xR0,
        y = yR0,
        mode="lines",
        name="Estimated R0 Trend",
        line = dict(color='White', shape='spline',smoothing= 1),
        yaxis="y2"
    )

    tracedivider = go.Scatter(
        x=[dates[-predDays-valDays-1], dates[-predDays-valDays-1]],
        y=[0,10],
        mode="lines",
        name="Model Fitting",
        line = dict(dash='dash',color='grey'),
        yaxis="y2", 
        showlegend=False
    ) 

    layout = go.Layout(
        xaxis=dict(ticks="", showticklabels=True, showgrid=False, zeroline=False, fixedrange=True, 
            # type='category',
            # categoryorder="array",
            # categoryarray = dates,
        ),
        yaxis=dict(ticks="", showticklabels=True, showgrid=False, zeroline=False, fixedrange=True, title="Confirmed Cases"),
        yaxis2=dict(
            ticks="", showticklabels=True, showgrid=False, zeroline=False, fixedrange=True,
            title="R0",
            overlaying="y",
            side="right",
            range=[0,10],
            # position=0.15
        ),
        hovermode="closest",
        legend=dict(x=0.05, y=0.95, orientation="v"),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="#282b38",
        paper_bgcolor="#282b38",
        font={"color": "#a5b1cd"},
    )

    data = [tracehist,tracefit, tracepred, traceR0, tracedivider]
    figure = go.Figure(data=data, layout=layout)

    return figure
