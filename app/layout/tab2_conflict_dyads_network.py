from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from layout.layout_functions import create_table, generate_incident_details_modal, generate_datatable_details_layout


# Default stylesheet for the cytoscape graph
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


modal_conflict_dyads_network = generate_incident_details_modal(
    modal_body_id="modal_conflict_dyads_network_content",
    modal_id="modal_conflict_dyads_network"
)


conflict_dyads_network_datatable_layout = generate_datatable_details_layout(
    datatable_id="network_datatable",
    column_name="incident_type",
    column_label="Incident type",
    modal_layout=modal_conflict_dyads_network,
)


conflict_dyads_network_tab = dbc.Row([
    dbc.Col([
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
            )
        ], style={"border-width": "1px", "border-style": "solid", "border-color": "#e6eaeb"}),
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
    ], style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
    *conflict_dyads_network_datatable_layout,
    dcc.Store(id='network_datatable_store', data={}),
])
