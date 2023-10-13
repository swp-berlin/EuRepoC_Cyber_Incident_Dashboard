from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    CONFIG, generate_incident_details_modal,
    generate_datatable_details_layout
)


modal_responses_types = generate_incident_details_modal(
    modal_body_id="modal_responses_content_types",
    modal_id="modal_responses_types"
)


responses_types_details_datatable_layout = generate_datatable_details_layout(
    datatable_id="responses_datatable_types",
    column_name="number_of_political_responses",
    column_label="Number of political responses",
    column_name_2="number_of_legal_responses",
    column_label_2="Number of legal responses",
    column_name_3="weighted_cyber_intensity",
    column_label_3="Weighted cyber intensity",
    modal_layout=modal_responses_types,
)


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
                            style={'height': '300px', 'margin-top': '10px'}
                        ),
                        html.Div(
                            html.P([
                                html.Span("Stabilising measures", style={"font-weight": "bold"}),
                                html.Span(" are statements made by ministers, heads of states, \
                                or subnational executives."),
                                html.Span(" Preventive measures", style={"font-weight": "bold"}),
                                html.Span(" include awareness raising, capacity building in third-countries \
                                and security building dialogues."),
                                html.Span(" Legislative reactions", style={"font-weight": "bold"}),
                                html.Span(" include, legislative initiatives, parliamentary investigation committees, \
                                and dissenting or stabilising statements by members of parliament."),
                                html.Span(" Executive reactions", style={"font-weight": "bold"}),
                                html.Span(" include, removal from office, resignations, and dissenting statements \
                                by executive officials.")
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
            ], style={'margin-top': '20px'}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
        ]),
        *responses_types_details_datatable_layout,
])
