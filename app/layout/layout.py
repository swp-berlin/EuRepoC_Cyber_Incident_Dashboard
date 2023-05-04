from dash import html
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break
from layout.sidebar import sidebar


card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Map view", tab_id="tab-1", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Conflict dyads", tab_id="tab-2", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Timeline", tab_id="tab-3", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Incident types", tab_id="tab-4", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Targeted sectors", tab_id="tab-5", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Attributions", tab_id="tab-6", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Legal", tab_id="tab-7", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Initiator types", tab_id="tab-8", tab_style={"marginRight": "auto"}),
            ],
            id="card-tabs",
            active_tab="tab-1",
        ),
        html.Div(id="card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})


full_layout = dbc.Container(
    children=[
        dbc.Row([
            dbc.Col([
                html.H1("Cyber Incident Dashboard")
            ], style={"text-align": "center"})
        ]),

        *make_break(2),

        dbc.Row([
            dbc.Col([
                sidebar,
            ], xxl=3, xl=3, lg=3, md=3, sm=12, xs=12),

            dbc.Col([
                dbc.Row([
                    card_tabs
                ]),
            ], xxl=9, xl=9, lg=9, md=9, sm=12, xs=12),
        ]),
    ],
    style={"padding": "50px 70px"}, fluid=True
)
