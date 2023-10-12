from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import CONFIG, generate_incident_details_modal, generate_datatable_details_layout


modal_conflict_dyads_bar = generate_incident_details_modal(
    modal_body_id="modal_conflict_dyads_bar_content",
    modal_id="modal_conflict_dyads_bar",
)


conflict_dyads_bar_datatable_layout = generate_datatable_details_layout(
    datatable_id="dyads_bar_datatable",
    column_name="incident_type",
    column_label="Incident type",
    modal_layout=modal_conflict_dyads_bar,
)


conflict_dyads_bar_tab = dbc.Row([
    dbc.Col([
        html.Div([
            dcc.Graph(
                id='dyads-bar-graph',
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
                    dbc.CardBody(id='dyads-bar-graph-key-insight')
                ]),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    id="dyads-bar-selected",
                    style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}
                ),
            ], style={"margin-top": "20px", "align": "center"}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Clear graph selection",
                    id="clear_dyads_bar_click_data",
                    n_clicks=0,
                    color="light",
                    size="sm",
                    style={'margin-bottom': '12px'}
                )
            ], style={"text-align": "center"}),
        ])
    ], style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
    *conflict_dyads_bar_datatable_layout,
])
