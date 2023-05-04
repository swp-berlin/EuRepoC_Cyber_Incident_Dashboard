from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table


modal_types = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_types_content'),
], id='modal_types', size='lg')


types_tab = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H3("What are the main types of cyber incidents?", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="types_title", style={"font-size": "1rem"}),
            dcc.Graph(id="types_graph")
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
                    html.Div(id="types_description_text"),
                ]),
            ]),
        ], align="center", sm=12, xs=12, lg=3, xl=3, xxl=3, md=3),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Span(
                            "Details on incidents",
                            style={"font-weight": "bold", "font-size": "1rem"}
                        ),
                        html.Span(
                            " (click on a point in the graph to see corresponding incidents)",
                            style={"font-style": "italic", "font-size": "1rem"}
                        )
                    ]),
                ], width=7),
                dbc.Col([
                    html.Div(id="types_selected",
                             style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'right'}),
                ], width=4),
                dbc.Col([
                    dbc.Button(
                        "Clear",
                        id="clear_types_click_data",
                        n_clicks=0,
                        color="light",
                        size="sm",
                        style={'margin-bottom': '12px'}
                    )
                ], width=1),
            ], style={"margin-top": "22px", "margin-bottom": "5px", "display": "flex", "align-items": "center"}),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            create_table("types_datatable", "weighted_cyber_intensity", "Weighted cyber intensity"),
            modal_types,
            dcc.Store(id='types_datatable_store', data={}),
        ]),
    ]),
])
