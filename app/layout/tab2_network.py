from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from layout.layout_functions import create_table


default_stylesheet = [
    {
        'selector': 'edge',
        'style': {
            'arrow-shape': 'triangle',
            'line-color': '#CCD8CC',
            'target-arrow-color': '#CCD8CC',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'width': 'data(weight)',
            'min-width': '1px',
            'max-width': '5px',
        }
    },
    {
        'selector': 'node',
        'style': {
            'label': 'data(flag)',
            'font-size': '22px',
            'background-color': '#002C38',
            'width': '30px',
            'height': '30px',
        }
    }
]


modal_network = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_network_content'),
], id='modal_network', size='xl', centered=True, scrollable=True)


network_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("From where to where are cyber incidents most frequently initiated and received?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id="network_title", style={"font-size": "1rem", "margin-bottom": "10px"}),
                html.Div([
                    cyto.Cytoscape(
                        id='cytoscape-graph',
                        elements=[],
                        responsive=True,
                        style={'height': '600px', 'width': '100%', 'margin': '0px', 'padding': '0px'},
                        layout={
                            'name': 'cola',
                            'nodeSpacing': 9,
                            "animate": True,
                        },
                        stylesheet=default_stylesheet,
                        minZoom=0.5,
                        maxZoom=1.5,
                    )], style={"border-width": "1px", "border-style": "solid", "border-color": "#e6eaeb"}
                ),
                dcc.Store(id='nodes_graph'),
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
                                    html.B(
                                        id="cytoscape-tapNodeData-output-title")
                                ], style={"display": "flex", "align-items": "center"}),
                            ]),
                            dbc.CardBody(id='cytoscape-tapNodeData-output')
                        ]),
                     ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            id="network_selected",
                            style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}
                        ),
                    ], style={"margin-top": "20px", "align": "center"}),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Clear graph selection",
                            id="clear_network_click_data",
                            n_clicks=0,
                            color="light",
                            size="sm",
                            style={'margin-bottom': '12px'}
                        )
                     ], style={"text-align": "center"}),
                ])
            ], align="center", style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
        ]),
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
                    table_id="network_datatable",
                    column_name="incident_type",
                    column_label="Incident type",
                ),
                modal_network,
                dcc.Store(id='network_datatable_store', data={}),
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