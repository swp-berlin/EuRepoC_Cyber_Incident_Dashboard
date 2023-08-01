from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG, generate_intensity_popover, generate_text_with_popover_icon


modal_initiators = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_initiators_content'),
], id='modal_initiators', size='xl', centered=True, scrollable=True)

mean_intensity_initiators_popover = generate_intensity_popover(target_id="mean_intensity_initiators_info")
mean_intensity_initiators_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_initiators_info", popover=mean_intensity_initiators_popover)


initiators_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("What type of actors initiate cyber incidents?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="initiators_text", style={"font-size": "1rem"}),
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="initiators_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '450px'}
                        )
                    ], style={'border-right': '1px solid #e6eaeb'}, sm=12, xs=12, md=12, lg=7, xl=7, xxl=7),
                    dbc.Col([
                        dcc.Graph(
                            id="initiators_graph_2",
                            config={
                                **CONFIG,
                            },
                            style={'height': '450px'}
                        )
                    ], sm=12, xs=12, md=12, lg=5, xl=5, xxl=5)
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
                                    html.B(id="nb_incidents_initiators",
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
                                        id="average_intensity_initiators",
                                        style={'display': 'inline-block', 'margin-left': '5px'}
                                    ),
                                ]),
                                mean_intensity_initiators_popover_icon,
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
                                html.Div(id="initiators_description_text"),
                            ]),
                        ])
                    ], style={'margin-top': '20px'}),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id="initiator_selected",
                                 style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}),
                    ], style={"margin-top": "20px", "align": "center"}),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Clear graph selection",
                            id="clear_initiator_click_data",
                            n_clicks=0,
                            color="light",
                            size="sm",
                            style={'margin-bottom': '12px'}
                        )
                    ], style={"text-align": "center"}),
                ]),
            ], style={'margin-top': '20px'}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3, align="center"),
        ]),
        dbc.Row([
            dbc.Col([
                html.P(["Details on incidents"], style={"font-weight": "bold", "font-size": "1rem"}),
            ])
        ], style={"margin-top": "22px", "margin-bottom": "5px", "display": "flex", "align-items": "center"}),
        dbc.Row([
            dbc.Col([
                create_table(
                    "initiators_datatable",
                    "incident_type",
                    "Incident type",
                ),
                modal_initiators,
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
)

