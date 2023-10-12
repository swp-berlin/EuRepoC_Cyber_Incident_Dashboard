from dash import html
import dash_bootstrap_components as dbc


attributions_card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Attribution speed", tab_id="timeline_tab"),
                dbc.Tab(label="Attribution bases", tab_id="types_tab"),
            ],
            id="attributions-card-tabs",
            active_tab="timeline_tab",
            className="nav-tabs2"
        ),
        html.Div(id="attributions-card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})


attributions_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.Div(id="attributions_question_title"),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id="attributions_text", style={"font-size": "1rem"}),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                attributions_card_tabs
            ])
        ])
    ])
)