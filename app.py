# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import datetime as DT
import re

# import figures as figs
import lib.dash_reusable_components as drc
import lib.forecast as forecast
from lib.graph import generateGraph

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# data
severeProv, provRes, otherData = forecast.getData()
severeProvLabel = [{"label": a, "value": a} for a in severeProv]

# x axis
lastDay = otherData['lastDay']
totDays = otherData['totDays']
lastDay = [int(c) for c in re.split('-|/',lastDay)]
lastDay = DT.date(*lastDay)
dates = [(lastDay - DT.timedelta(days = (totDays-i-1))).strftime(r'%m/%d').lstrip("0")  for i in range(totDays + 5)]

# Default 
valDays = 2
predDays = 4
prediction_figure = generateGraph(severeProv[0], dates, provRes[severeProv[0]],totDays,valDays,predDays)

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
                                    "确诊预测模型",
                                    style={
                                        "text-decoration": "none",
                                        "color": "inherit",
                                    },
                                ),
                                html.A(
                                    "by QMSHAO",
                                    style={
                                        "text-decoration": "none",
                                        "color": "inherit",
                                        "padding": "10px",
                                        "font-size": "50%",
                                    },
                                )
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
                                            name="超过100例确诊",
                                            id="dropdown-select-dataset",
                                            options = severeProvLabel,
                                            clearable=False,
                                            searchable=False,
                                            value=severeProvLabel[0]['label' ],
                                        ),
                                        drc.NamedSlider(
                                            name="模型截至日期",
                                            id="slider-training-date",
                                            min=-4,
                                            max=0,
                                            marks={
                                                i: dates[i-6] 
                                                for i in range(-4,1)
                                            },
                                            value=-valDays,
                                        ),
                                         drc.NamedSlider(
                                            name="模型预测天数",
                                            id="slider-forecasting-days",
                                            min=1,
                                            max=5,
                                            marks={
                                                str(i): str(i)
                                                for i in range(1,6)
                                            },
                                            step=1,
                                            value=predDays,
                                        ),
                                    ],
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
        Input("slider-forecasting-days", "value"),
    ],
)
def updateGraph(name, valDays, predDays):
    prediction_figure = generateGraph(name, dates, provRes[name],totDays,abs(valDays),predDays)
    return dcc.Graph(id="graph-prediction", figure=prediction_figure)


# Running the server
if __name__ == "__main__":
    app.run_server(debug=False)