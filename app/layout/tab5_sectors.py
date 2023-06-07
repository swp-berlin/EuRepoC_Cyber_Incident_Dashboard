from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG


modal_sectors = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_sectors_content'),
], id='modal_sectors', size='lg')


sectors_tab = dbc.Container([
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("What are the most frequently targeted sectors?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="sectors_title", style={"font-size": "1rem"}),
                        dcc.Graph(
                            id='sectors_graph',
                            config={
                                **CONFIG,
                            },
                            style={'height': '500px'}
                        ),
                        dcc.Store(id='top_sector_store'),
                        dcc.Store(id='top_sector_value_store'),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.I(
                            "Note as of 01/02/2023, the EuRepoC expanded its inclusion criteria to additional types of critical \
                            infrastructure, including chemicals, water, food, critical manufacturing, waste management and space.",
                            style={"font-weight": "italics"}
                        )
                    ], style={"margin-top": "10px"})
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
                                    html.B(id="nb_incidents_sectors",
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
                                        id="average_intensity_sectors",
                                        style={'display': 'inline-block', 'margin-left': '5px'}
                                    ),
                                ]),
                                html.P("Mean intensity"),
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
                                html.Div(id="sectors_description_text"),
                            ]),
                        ]),
                    ], style={"margin-top": "20px"}),
                ]),
                dbc.Row([
                        dbc.Col([
                            html.Div(id="sectors_selected",
                                     style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}),
                        ], style={"margin-top": "20px", "align": "center"}),
                    ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Clear graph selection",
                            id="clear_sectors_click_data",
                            n_clicks=0,
                            color="light",
                            size="sm",
                            style={'margin-bottom': '12px'}
                        )
                    ], style={"text-align": "center"}),
                ]),
            ], align="center", style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
        ]),
        dbc.Row([
            dbc.Col([
                html.P([
                    "Details on incidents"
                ], style={"font-weight": "bold", "font-size": "1rem"}),
            ], style={"margin-top": "22px", "margin-bottom": "5px"}),
        ]),
        dbc.Row([
            dbc.Col([
                create_table("sectors_datatable", "incident_type", "Incident type"),
                modal_sectors,
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
])