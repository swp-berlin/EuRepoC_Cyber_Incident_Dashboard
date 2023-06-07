from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG


modal_types = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_types_content'),
], id='modal_types', size='lg')

data_theft_popover = dbc.Popover(
    "Incidents initiated to gather information from a targeted computer or computer system. Although data or \
    information is not “lost” for the target - it still possesses it - the data is no longer confidential. \
    If state actors are involved, it is regularly called “Cyber Espionage.”",
    target="data_theft_info",
    body=True,
    trigger="hover",
)

data_theft_doxing_popover = dbc.Popover(
    "Additionally to the ‘theft’ of data, the attacker(s) leak(s) the stolen information to the public.",
    target="data_theft_doxing_info",
    body=True,
    trigger="hover",
)

disruption_popover = dbc.Popover(
    "Incidents that negatively impact the functioning of the targeted systems, with potentially disruptive effects \
    on connected physical systems. Examples include DDoS attacks, defacements and wiper attacks.",
    target="disruption_info",
    body=True,
    trigger="hover",
)

hijacking_with_misuse_popover = dbc.Popover(
    "Incidents where the attacker penetrates or takes over the attacked system(s), gaining deeper administrative rights, \
     and some abuse of these rights has been observed - e.g. data theft and/or disruption.",
    target="hijacking_misuse_info",
    body=True,
    trigger="hover",
)

hijacking_without_misuse_popover = dbc.Popover(
    "Incidents where the attacker penetrates or takes over the attacked system(s), gaining deeper administrative rights, \
     but no obvious abuse of these rights has been observed so far.",
    target="hijacking_without_misuse_info",
    body=True,
    trigger="hover",
)

ransomware_popover = dbc.Popover(
    "Ransomware is a type of malicious software (malware) that encrypts the victim's files. \
    The attacker then demands a ransom from the victim to restore access to the data upon payment.",
    target="ransomware_info",
    body=True,
    trigger="hover",
)


types_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("What are the main types of cyber incidents?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="types_title", style={"font-size": "1rem"}),
                        dcc.Graph(
                            id="types_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '450px'}
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(204, 1, 48, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px'
                                        }
                                    ),
                                    " Data theft",
                                        html.I(
                                            id="data_theft_info",
                                            className="fa-regular fa-circle-question",
                                            style={
                                                'text-align': 'center',
                                                'font-size': '12px',
                                                'color': '#002C38',
                                                'right': '-14px', 'top': '-2px',
                                                'position': 'absolute'
                                            }
                                    ),
                                    data_theft_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(0, 44, 56, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Data theft & doxing",
                                    html.I(
                                        id="data_theft_doxing_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    data_theft_doxing_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(137, 189, 158, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Disruption",
                                    html.I(
                                        id="disruption_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    disruption_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                        ], style={"text-align": "left"}),
                        dbc.Row([
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(132, 126, 137, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px'
                                        }
                                    ),
                                    " Hijacking with misuse",
                                    html.I(
                                        id="hijacking_misuse_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    hijacking_with_misuse_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(244, 185, 66, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Hijacking without misuse",
                                    html.I(
                                        id="hijacking_without_misuse_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                           'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    hijacking_without_misuse_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(121, 68, 59, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Ransomware",
                                    html.I(
                                        id="ransomware_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                           'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    ransomware_popover
                                ], className="position-relative")
                            ], lg=4, xl=4, xxl=4)
                        ], style={"text-align": "left", "margin-top": "2px"}),
                    ], style={"padding-left": "50px"}),
                ], style={'margin-top': '15px'}),
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
                                    html.B(id="nb_incidents_types",
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
                                        id="average_intensity_types",
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
                                html.Div(id="types_description_text"),
                            ]),
                        ]),
                    ], style={"margin-top": "20px"})
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id="types_selected",
                                 style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}),
                    ], style={"margin-top": "20px", "align": "center"}),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Clear graph selection",
                            id="clear_types_click_data",
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
                html.P(
                    "Details on incidents",
                    style={"font-weight": "bold", "font-size": "1rem"}
                ),
            ])
        ], style={"margin-top": "25px", "margin-bottom": "5px"}),
        dbc.Row([
            dbc.Col([
                create_table("types_datatable", "weighted_cyber_intensity", "Weighted cyber intensity"),
                modal_types,
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
