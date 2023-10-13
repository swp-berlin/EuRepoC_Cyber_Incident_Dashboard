from dash import html
import dash_bootstrap_components as dbc


conflict_dyads_card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Network graph", tab_id="network_tab"),
                dbc.Tab(label="Bar chart", tab_id="bar_tab"),
            ],
            id="conflict_dyads_card_tabs",
            active_tab="network_tab",
            className="nav-tabs2"
        ),
        html.Div(id="conflict_dyads_card_content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})


conflict_dyads_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3(
                    "From where to where are cyber incidents most frequently initiated and received?",
                    style={'text-align': 'center'}
                ),
            ], style={'margin-top': '20px', "margin-left": "20px", "margin-right": "20px", "margin-bottom": "10px"}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    id="dyads_title",
                    style={"font-size": "1rem", "margin-bottom": "5px", "margin-left": "12px"}
                ),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                conflict_dyads_card_tabs
            ]),
        ]),
    ])
)