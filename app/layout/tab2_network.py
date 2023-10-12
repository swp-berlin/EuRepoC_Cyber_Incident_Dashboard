from dash import html
import dash_bootstrap_components as dbc
#import dash_cytoscape as cyto
#from layout.layout_functions import create_table

network_card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Network graph", tab_id="network_tab"),
                dbc.Tab(label="Bar chart", tab_id="network_bar"),
            ],
            id="network-card-tabs",
            active_tab="network_tab",
            className="nav-tabs2"
        ),
        html.Div(id="network-card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})

network_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("From where to where are cyber incidents most frequently initiated and received?", style={'text-align': 'center'}),
            ], style={'margin-top': '20px', "margin-left": "20px", "margin-right": "20px", "margin-bottom": "10px"}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id="network_title", style={"font-size": "1rem", "margin-bottom": "5px", "margin-left": "12px"}),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                network_card_tabs
            ]),
        ]),
    ])
)
