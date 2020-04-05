
import colorlover as cl
import plotly.graph_objs as go
import numpy as np
import plotly.express as px

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
    
    ylb = [yhist[-valDays-1], *data['bounds'][dispDays - valDays - 1]['lb']]
    yub = [yhist[-valDays-1], *data['bounds'][dispDays - valDays - 1]['ub']]

    xR0 = dates[-window-predDays:-predDays]
    yR0 = data['R0hist']
    
    xErr = dates[-predDays-window+1:-predDays]
    yErr = np.array(data['err']) * data['hist'][-1] / 1.5
    textErr = list(map(lambda e: '{0:+0.1f}%'.format(e*100), data['err']))
    baseErr = data['hist'][-window+1:]
    colorErr = list(map(lambda e: 'crimson' if e>0 else px.colors.qualitative.Dark2[0], yErr))

    # Plot 
    # sizefactor = 1 if name in ['湖北省','全国','湖北'] else 1
    sizefactor = 3
    tracehist = go.Scatter(
        x=xhist,
        y=yhist,
        mode="markers",
        name="Confirmed Cases",
        line=None,
        marker=dict(size=5, color=px.colors.qualitative.Set1[5], #'#E55A4D', np.log10(yhist+1)*sizefactor
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
        name="Fitting",
        line = dict(dash='dash',color='Violet'),
    ) 
    
    # Lower Bound
    tracelb = go.Scatter(
        x=xpred,
        y=ylb,
        mode="lines",
        name="Social Distancing Impact",
        line = dict(dash='dash',color='GoldenRod'),
        # fill='tonexty',
        # showlegend=False
    )    

    # Upper Bound
    traceub = go.Scatter(
        x=xpred,
        y=yub,
        mode="lines",
        name="5% R0 Increase",
        fill='tonexty',
        line = dict(dash='dash',color='DeepSkyBlue'), #GoldenRod
        showlegend=False
    )    

    tracepred = go.Scatter(
        x=xpred,
        y=ypred,
        mode="lines",
        name="Forecasting",
        # fill='tonexty',
        line = dict(dash='dash',color='DeepSkyBlue'),
    ) 
    
    traceR0 = go.Scatter(
        x = xR0,
        y = yR0,
        mode="lines",
        name="R0 Trend",
        line = dict(color='White', shape='spline',smoothing= 1),
        yaxis="y2"
    )

    tracedivider = go.Scatter(
        x=[dates[-predDays-valDays-1], dates[-predDays-valDays-1]],
        y=[0,10],
        mode="lines",
        name="Divider",
        line = dict(dash='dash',color='grey'),
        yaxis="y2", 
        showlegend=False
    ) 

    traceErr = go.Bar(x=xErr, y=yErr,
        base=baseErr,
        text=textErr,
        texttemplate='%{text}', textposition='outside',
        marker_color=colorErr,
        name=r'Daily % diff')

    layout = go.Layout(
        xaxis=dict(ticks="", showticklabels=True, showgrid=False, zeroline=False, fixedrange=True, 
            # type='category',
            # categoryorder="array",
            # categoryarray = dates,
        ),
        yaxis=dict(ticks="inside", showticklabels=False, showgrid=False, zeroline=False, fixedrange=True, ), #title="Confirmed Cases"
        yaxis2=dict(
            ticks="inside", showticklabels=False, showgrid=False, zeroline=False, fixedrange=True,
            # title="R0",
            overlaying="y",
            side="right",
            range=[0,10],
            # position=0.15
        ),
        barmode='relative',
        hovermode="closest",
        legend=dict(x=0.05, y=0.95, orientation="v"),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="#282b38",
        paper_bgcolor="#282b38",
        font={"color": "#a5b1cd"},
    )



    data = [tracehist,tracefit, tracepred, tracelb, traceub, traceR0, tracedivider, traceErr]
    figure = go.Figure(data=data, layout=layout)

    return figure
