from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table, CONFIG


modal_network_graph = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_network_content_graph'),
], id='modal_network_graph', size='xl', centered=True, scrollable=True)


network_bar_tab = dbc.Row([
    dbc.Col([
        html.Div([
            dcc.Graph(
                id='network-bar-graph',
                responsive=True,
                config={
                    **CONFIG,
                    },
                style={'height': '600px'}
            )
        ], style={"border-width": "1px", "border-style": "solid", "border-color": "#e6eaeb"}),
    ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
    dbc.Col([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.P([
                            html.I(
                                className="fa-solid fa-magnifying-glass-chart",
                                style={"color": "#CC0130", "font-size": "22px", "margin-right": "5px"}),
                            html.B('Key insight')
                        ], style={"display": "flex", "align-items": "center"}),
                    ]),
                    dbc.CardBody(id='network-bar-graph-key-insight')
                ]),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    id="network-bar-selected",
                    style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}
                ),
            ], style={"margin-top": "20px", "align": "center"}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Clear graph selection",
                    id="clear_network_bar_click_data",
                    n_clicks=0,
                    color="light",
                    size="sm",
                    style={'margin-bottom': '12px'}
                )
            ], style={"text-align": "center"}),
        ])
    ], style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3), #align="center",
    dbc.Row([
        dbc.Col([
            html.P([
                "Details on incidents",
            ], style={"font-weight": "bold", "font-size": "1rem"}),
        ], style={"margin-top": "28px", "margin-bottom": "5px"}),
    ]),
    dbc.Row([
        dbc.Col([
            create_table(
                table_id="network_datatable_graph",
                column_name="incident_type",
                column_label="Incident type",
            ),
            modal_network_graph,
            dcc.Store(id='network_datatable_store_graph', data={}),
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