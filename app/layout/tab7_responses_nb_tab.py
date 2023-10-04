from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG, generate_intensity_popover, generate_text_with_popover_icon


modal_responses = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_responses_content'),
], id='modal_responses', size='xl', centered=True, scrollable=True)

mean_intensity_responses_popover = generate_intensity_popover(target_id="mean_intensity_responses_info")
mean_intensity_responses_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_responses_info", popover=mean_intensity_responses_popover)

#How many cyber incidents are met with a political or legal response?

responses_nb_tab = dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="responses_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px'}
                        ),
                        html.Div(
                            id="responses_donut_annotation",
                            style={
                                "font-size": "0.7rem",
                                "margin-bottom": "15px"
                            }
                        )
                    ], sm=12, xs=12, lg=12, xl=12, xxl=12, md=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(html.B("Percentage of incidents with a political or legal response by intensity score"), style={"font-size": "1rem"}),
                        dcc.Graph(
                            id="responses_graph_2",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px'}
                        ),
                        html.Div(id="responses_scatter_annotation", style={"font-size": "0.7rem", "margin-top": "10px"})
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
                                        className="fa-solid fa-explosion",
                                        style={'font-size': '22px', 'color': '#CC0130', 'display': 'inline-block'}),
                                    html.B(id="nb_incidents_responses",
                                           style={'display': 'inline-block', 'margin-left': '5px'}),
                                ]),
                                html.P("Total incidents"),
                            ], style={'padding': '5px 0px 0px 5px'}),
                        ], style={'padding': '0px', 'margin-top': '0px'}),
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.I(
                                        className="fa-solid fa-gauge",
                                        style={'font-size': '22px', 'color': '#CC0130', 'display': 'inline-block'}
                                    ),
                                    html.B(
                                        id="average_intensity_responses",
                                        style={'display': 'inline-block', 'margin-left': '5px'}
                                    ),
                                ]),
                                mean_intensity_responses_popover_icon,
                            ], style={'padding': '5px 0px 15px 5px'}),
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
                                html.Div(id="responses_description_text"),
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
                    "responses_datatable",
                    "number_of_political_responses",
                    "Number of political responses",
                    "number_of_legal_responses",
                    "Number of legal responses",
                    "weighted_cyber_intensity",
                    "Weighted cyber intensity",
                ),
                modal_responses,
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

