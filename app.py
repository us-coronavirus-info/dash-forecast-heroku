# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import datetime as DT
import re

# import figures as figs
import lib.dash_reusable_components as drc
import lib.forecast2 as forecast
from lib.graph2 import generateGraph
import dash_daq as daq

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-106805084-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
        
          gtag('config', 'UA-106805084-1');
        </script>

        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

server = app.server

# data
severeStates, stateRes, lastDay = forecast.updatedata()
severeProvLabel = [{"label": a, "value": a} for a in severeStates]
totDays = 16 # equal to window + dispDays - 1 + predDays for now

# x axis
lastDay = [int(c) for c in re.split('-|/',lastDay)]

lastDay = DT.date(2020, *lastDay) # Hardcoded Year
dates = [(lastDay - DT.timedelta(days = (totDays-i-4))).strftime(r'%m/%d').lstrip("0")  for i in range(totDays)]

# Default 
predDays = 3
valDays = 0
dispDays = 7
prediction_figure = generateGraph(severeStates[0], dates, stateRes[severeStates[0]], totDays, valDays)

# HTML
app.layout = html.Div(
    children=[
        # .container class is fixed, .container.scalable is scalable
        html.Div(
            className="banner",
            children=[
                # Change App Name here
                html.Div(
                    className="container scalable",
                    children=[
                        # Change App Name here
                        html.H2(
                            id="banner-title",
                            children=[
                                html.A(
                                    "US Confimred Case Forecast",
                                    style={
                                        "text-decoration": "none",
                                        "color": "inherit",
                                    },
                                ),
                                # html.A(
                                #     "by QMSHAO",
                                #     style={
                                #         "text-decoration": "none",
                                #         "color": "inherit",
                                #         "padding": "10px",
                                #         "font-size": "50%",
                                #     },
                                # )
                            ],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            id="body",
            className="container scalable",
            children=[
                html.Div(
                    id="app-container",
                    # className="row",
                    children=[
                        html.Div(
                            # className="three columns",
                            id="left-column",
                            children=[
                                drc.Card(
                                    id="first-card",
                                    children=[
                                        drc.NamedDropdown(
                                            name="States over 1000 Cases",
                                            id="dropdown-select-dataset",
                                            options = severeProvLabel,
                                            clearable=False,
                                            searchable=False,
                                            value=severeProvLabel[0]['label' ],
                                        ),
                                        html.P("Forecast Today"),
                                        html.Div(
                                            id = 'LEDcontainer',
                                            style = {"display":"flex"},
                                            children = [
                                                    daq.LEDDisplay(
                                                    id="forecast-lb",
                                                    value=int(stateRes[severeStates[0]]['forecast'][0]),
                                                    color="#92e0d3",
                                                    backgroundColor="#1e2130",
                                                    size=12,
                                                ),
                                                html.Div(
                                                    style={"padding":5, "color": "#92e0d3"},
                                                    children = [
                                                        html.P(''),
                                                        html.P('to'),
                                                    ]
                                                ),
                                                daq.LEDDisplay(
                                                    id="forecast-ub",
                                                    value=int(stateRes[severeStates[0]]['forecast'][2]),
                                                    color="#92e0d3",
                                                    backgroundColor="#1e2130",
                                                    size=12,
                                                ),
                                            ]
                                        ),
                                        drc.NamedSlider(
                                            name="Date to Start Forecasting",
                                            id="slider-training-date",
                                            min=-dispDays+1,
                                            max=0,
                                            marks={
                                                i: dates[i-4] 
                                                for i in range(-dispDays+1,1)
                                            },
                                            value=-valDays,
                                        ),
                                    ],
                                ),
                                    
                                drc.Card(
                                    id="second-card",
                                    children=[
                                        html.P('R0 is estimated from simplified SEIR model, only reflecting the trend. \
                                                    Daily % diff is the real confirmed number compared to the forecast, \
                                                        postive means worse than the forecset, and negtive means better than the forecast.')
                                    ]
                                ),
                            ],
                        ),
                        html.Div(
                            id="div-graphs",
                            children= [
                                html.Div(
                                    id="svm-graph-container",
                                    children=dcc.Loading(
                                        className="graph-wrapper",
                                        id='div-prediction',
                                        children=dcc.Graph(id="graph-prediction", figure=prediction_figure),
                                        style={"display": "none"},
                                    ),
                                ),
                            ]

                        ),
                    ],
                )
            ],
        ),
    ]
)

@app.callback(
    Output("div-prediction", "children"),
    [
        Input("dropdown-select-dataset", "value"),
        Input("slider-training-date", "value"),
    ],
)
def updateGraph(name, valDays):
    prediction_figure = generateGraph(name, dates, stateRes[name],totDays,abs(valDays))

    return dcc.Graph(id="graph-prediction", figure=prediction_figure)

@app.callback(
    Output("forecast-lb", "value"),
    [
        Input("dropdown-select-dataset", "value"),
    ],
)
def updateForecasetLb(name):
    return int(stateRes[name]['forecast'][0]),


ubfilterlist = ['New York', 'United States']
@app.callback(
    Output("forecast-ub", "value"),
    [
        Input("dropdown-select-dataset", "value"),
    ],
)
def updateForecasetUb(name):
    return int(stateRes[name]['forecast'][2 if name in ubfilterlist else 1]),

# Running the server
if __name__ == "__main__":
    app.run_server(debug=False)
