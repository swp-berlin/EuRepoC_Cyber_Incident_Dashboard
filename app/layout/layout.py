from dash import html, dcc
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break
from layout.sidebar import generate_sidebar


card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Overview", tab_id="tab-1"),
                dbc.Tab(label="Conflict dyads", tab_id="tab-2"),
                dbc.Tab(label="Timeline", tab_id="tab-3"),
                dbc.Tab(label="Incident types", tab_id="tab-4"),
                dbc.Tab(label="Targeted sectors", tab_id="tab-5"),
                dbc.Tab(label="Attributions", tab_id="tab-6"),
                dbc.Tab(label="Responses", tab_id="tab-7"),
                dbc.Tab(label="Initiator types", tab_id="tab-8"),
            ],
            id="card-tabs",
            active_tab="tab-1",
            className="tab-row"
        ),
        html.Div(id="card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})

def serve_layout():
    full_layout = dbc.Container(
        children=[
            dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    max_intervals=1
                ),
            dbc.Row([
                dcc.Store(id='metric_values'),
                dcc.Store(id='nb_threat_groups_data'),
                #dcc.Store(id='prev-receiver-country'),
                #dcc.Store(id='prev-initiator-country'),
                #dcc.Store(id='prev-incident-type'),
                #dcc.Store(id='prev-start-date'),
                #dcc.Store(id='prev-end-date'),
            ]),

            #*make_break(2),

            dbc.Row([
                dbc.Col([
                    generate_sidebar(),
                ], xxl=3, xl=3, lg=3, md=4, sm=12, xs=12),

                dbc.Col([
                    dbc.Row([
                        card_tabs
                    ]),
                ], xxl=9, xl=9, lg=9, md=8, sm=12, xs=12),
            ]),
        ],
        style={"padding": "10px 35px"}, fluid=True
    )
    return full_layout
