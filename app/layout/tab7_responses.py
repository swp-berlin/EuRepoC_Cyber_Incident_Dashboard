from dash import html
import dash_bootstrap_components as dbc


responses_card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Number of responses", tab_id="response_number_tab"),
                dbc.Tab(label="Type of responses", tab_id="reponse_types_tab"),
            ],
            id="responses-card-tabs",
            active_tab="response_number_tab",
            className="nav-tabs2"
        ),
        html.Div(id="responses-card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})


responses_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.Div(id="responses_question_title"),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id="responses_text", style={"font-size": "1rem"}),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                responses_card_tabs
            ])
        ])
    ])
)
