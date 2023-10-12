from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG


modal_responses_types = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_responses_content_types'),
], id='modal_responses_types', size='xl', centered=True, scrollable=True)


responses_types_tab = dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="responses_graph_types",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px', 'margin-top':'10px'}
                        ),
                        html.Div(
                            html.P([
                                html.Span("Stabilising measures", style={"font-weight": "bold"}),
                                html.Span(" are statements made by ministers, heads of states, or subnational executives."),
                                html.Span(" Preventive measures", style={"font-weight": "bold"}),
                                html.Span(" include awareness raising, capacity building in third-countries and security building dialogues."),
                                html.Span(" Legislative reactions", style={"font-weight": "bold"}),
                                html.Span(" include, legislative initiatives, parliamentary investigation committees, \
                                and dissenting or stabilising statements by members of parliament."),
                                html.Span(" Executive reactions", style={"font-weight": "bold"}),
                                html.Span(" include, removal from office, resignations, and dissenting statements by executive officials.")
                            ]),
                        style={"font-size": "0.7rem", "margin-bottom": "15px"}
                        )
                    ], sm=12, xs=12, lg=12, xl=12, xxl=12, md=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="responses_graph_2_types",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px'}
                        ),
                    ], sm=12, xs=12, lg=12, xl=12, xxl=12, md=12),
                ]),
            ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(
                                        className="fa-solid fa-landmark",
                                        style={'font-size': '22px', 'color': '#CC0130', 'display': 'inline-block'}),
                                    html.B(id="nb_incidents_responses_types",
                                           style={'display': 'inline-block', 'margin-left': '5px'}),
                                ]),
                                html.P("Incidents with pol. responses"),
                            ], style={'padding': '5px 0px 0px 5px'}),
                        ], style={'padding': '0px', 'margin-top': '0px'}),
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(
                                        className="fa-solid fa-scale-balanced",
                                        style={'font-size': '22px', 'color': '#CC0130', 'display': 'inline-block'}
                                    ),
                                    html.B(
                                        id="average_intensity_responses_types",
                                        style={'display': 'inline-block', 'margin-left': '5px'}
                                    ),
                                    html.P("Incidents with legal responses")
                                ]),
                            ], style={'padding': '5px 0px 0px 5px'}),
                        ], style={'padding': '0px', 'margin-top': '0px'})
                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader([
                                html.P([
                                    html.I(
                                        className="fa-solid fa-magnifying-glass-chart",
                                        style={"color": "#CC0130", "font-size": "22px"}
                                    ),
                                    html.B("  Key insight")
                                ]),
                            ], style={"display": "flex", "align-items": "center"}),
                            dbc.CardBody([
                                html.Div(id="responses_description_text_types"),
                            ]),
                        ])
                    ], style={'margin-top': '20px'}),
                ]),
            ], style={'margin-top': '20px'}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3), #align="center"
        ]),
        dbc.Row([
            dbc.Col([
                html.P(["Details on incidents with responses"], style={"font-weight": "bold", "font-size": "1rem"}),
            ])
        ], style={"margin-top": "22px", "margin-bottom": "5px", "display": "flex", "align-items": "center"}),
        dbc.Row([
            dbc.Col([
                create_table(
                    "responses_datatable_types",
                    "number_of_political_responses",
                    "Number of political responses",
                    "number_of_legal_responses",
                    "Number of legal responses",
                    "weighted_cyber_intensity",
                    "Weighted cyber intensity",
                ),
                modal_responses_types,
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.P([
                    html.I(
                        className="fa-solid fa-arrow-pointer",
                        style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                    ),
                    " Click on a row in the table above to display all information about the incident",
                ], style={"font-style": "italic", "font-size": "1rem", "color": "#CC0130", "text-align": "center"}
                )
            ]),
        ], style={"margin-top": "1px"}),
])

