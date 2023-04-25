from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table


modal_sectors = dbc.Modal([
    dbc.ModalHeader('Incident details'),
    dbc.ModalBody(id='modal_sectors_content'),
], id='modal_sectors', size='lg')


sectors_tab = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H3("What are the most frequently targeted sectors?", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="sectors_title", style={"font-size": "1rem"}),
            dcc.Graph(
                id='sectors_graph',
            ),
        ], sm=12, xs=12, lg=9, xl=9, xxl=9, md=9),
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
        ], align="center", sm=12, xs=12, lg=3, xl=3, xxl=3, md=3),
    ]),
    dbc.Row([
        dbc.Col([
            html.I(
                "Note as of 01/02/2023, the EuRepoC expanded its inclusion criteria to additional types of critical \
                infrastructure, including chemicals, water, food, critical manufacturing, waste management and space.",
                style={"font-weight": "italics"}
            )
        ])
    ], style={"margin-top": "10px"}),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Span("Details on incidents", style={"font-weight": "bold", "font-size": "1rem"}),
                        html.Span(" (click on a point in the graph to see corresponding incidents)",
                                  style={"font-style": "italic", "font-size": "1rem"})
                    ]),
                ], width=7),
                dbc.Col([
                    html.Div(id="sectors_selected",
                             style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'right'}),
                ], width=4),
                dbc.Col([
                    dbc.Button("Clear", id="clear_sectors_click_data", n_clicks=0, color="light", size="sm",
                               style={'margin-bottom': '12px'})
                ], width=1),
            ], style={"margin-top": "22px", "margin-bottom": "5px", "display": "flex", "align-items": "center"}),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            create_table("sectors_datatable", "incident_type", "Incident type"),
            modal_sectors,
            dcc.Store(id='sectors_datatable_store', data={}),
        ]),
    ]),
])
