from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import CONFIG, generate_intensity_popover, \
    generate_text_with_popover_icon, generate_incident_details_modal, generate_datatable_details_layout


modal_timeline = generate_incident_details_modal(modal_body_id="modal_timeline_content", modal_id="modal_timeline")

timeline_datatable_layout = generate_datatable_details_layout(
    datatable_id="timeline_datatable",
    column_name="incident_type",
    column_label="Incident type",
    modal_layout=modal_timeline,
)


mean_intensity_timeline_popover = generate_intensity_popover(target_id="mean_intensity_timeline_info")
mean_intensity_timeline_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_timeline_info", popover=mean_intensity_timeline_popover)


timeline_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("How has the number of cyber incidents evolved overtime?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            id="timeline_text", style={"font-size": "1rem"}
                        )
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="timeline_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '450px'}
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.I("Note as of 01/02/2023, the EuRepoC expanded its inclusion criteria. \
                        This can explain a spike in incidents from this period onwards.",
                               style={"font-weight": "italics"})
                    ])
                ], style={"margin-top": "15px"}),
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
                                    html.B(id="nb_incidents_timeline",
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
                                        id="average_intensity_timeline",
                                        style={'display': 'inline-block', 'margin-left': '5px'}
                                    ),
                                ]),
                                mean_intensity_timeline_popover_icon,
                            ], style={'padding': '5px 0px 15px 5px'}),
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
                                html.Div(id="timeline_description_text"),
                            ]),
                        ]),
                    ], style={"margin-top": "20px"})
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id="timeline_selected",
                                 style={"font-size": "1rem", 'color': '#CC0130', 'text-align': 'center'}),
                    ], style={"margin-top": "20px", "align": "center"}),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Clear graph selection",
                            id="clear_timeline_click_data",
                            n_clicks=0,
                            color="light",
                            size="sm",
                            style={'margin-bottom': '12px'}
                        )
                    ], style={"text-align": "center"}),
                ]),
            ], style={"margin-top": "20px"}, sm=12, xs=12, md=12, lg=3, xl=3, xxl=3),
        ]),
        *timeline_datatable_layout
    ])
)
