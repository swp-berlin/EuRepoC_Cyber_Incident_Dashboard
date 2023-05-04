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
            'background-color': '#002C38',
            'width': '30px',
            'height': '30px',
        }
    }
]


modal_network = dbc.Modal([
    dbc.ModalHeader(html.H3('Incident details')),
    dbc.ModalBody(id='modal_network_content'),
], id='modal_network', size='lg')


network_tab = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H3("Which initiator nationalities attack each other the most?", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),

    dbc.Row([
        dbc.Col([
            html.Div(id="network_title", style={"font-size": "1rem"}),
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
                minZoom=1,
                maxZoom=1.2,
            ),
            dcc.Store(id='nodes_graph'),
        ], sm=12, xs=12, lg=9, xl=9, xxl=9, md=9),
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
        ], align="center", sm=12, xs=12, lg=3, xl=3, xxl=3, md=3),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Span("Details on incidents", style={"font-weight": "bold", "font-size": "1rem"}),
                        html.Span(" (click on a point in the network to see corresponding incidents)",
                                  style={"font-style": "italic", "font-size": "1rem"})
                    ]),
                ], width=7),
                dbc.Col([
                    html.Div(id="network_selected",
                             style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'right'}),
                ], width=4),
                dbc.Col([
                    dbc.Button("Clear", id="clear_network_click_data", n_clicks=0, color="light", size="sm",
                               style={'margin-bottom': '12px'})
                ], width=1),
            ], style={"margin-top": "22px", "margin-bottom": "5px", "display": "flex", "align-items": "center"}),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            create_table(table_id="network_datatable", column_name="incident_type", column_label="Incident type"),
            modal_network,
            dcc.Store(id='network_datatable_store', data={}),
        ]),
    ])
])
