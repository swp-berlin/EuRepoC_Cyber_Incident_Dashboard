from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import create_table


modal_attributions = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_attributions_content'),
], id='modal_attributions', size='lg')


attributions_tab = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H3("How long does it take for the initiator of a cyber incident to be attributed?", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="attributions_text", style={"font-size": "1rem"}),
            dcc.Graph(id="attributions_graph")
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
                    html.Div(id="attributions_description_text"),
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
                            " (click on a point in the graph to see incidents)",
                            style={"font-style": "italic", "font-size": "1rem"}
                        )
                    ]),
                ], width=6),
                dbc.Col([
                    html.Div(id="attributions_selected",
                             style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'right'}),
                ], width=5),
                dbc.Col([
                    dbc.Button(
                        "Clear",
                        id="clear_attributions_click_data",
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
            create_table("attributions_datatable", "number_of_attributions", "Number of attributions"),
            modal_attributions,
        ]),
    ]),
])
