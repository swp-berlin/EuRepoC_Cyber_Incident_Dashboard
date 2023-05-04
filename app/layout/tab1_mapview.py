from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break


map_tab = dbc.Row([

    dbc.Row([
        dbc.Col([
            html.Div(id="selected_options_text", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(
                                    className="fa-solid fa-explosion",
                                    style={'font-size': '25px', 'color': '#CC0130', 'display': 'inline-block'}),
                                html.H3(id="nb_incidents", style={'display': 'inline-block', 'margin-left': '5px'}),
                            ]),
                            html.P("Cyber incidents"),
                        ], style={'padding': '5px 0px 0px 5px'}),
                    ], style={'padding': '0px', 'margin': '0px'}),
                ], md=4, align="center"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(
                                    className="fa-solid fa-user-group",
                                    style={'font-size': '25px', 'color': '#CC0130', 'display': 'inline-block'}),
                                html.H3(id="nb_threat_groups", style={'display': 'inline-block', 'margin-left': '5px'}),
                            ]),
                            html.P("Threat groups"),
                        ], style={'padding': '5px 0px 0px 5px'}),
                    ], style={'padding': '0px', 'margin': '0px'})
                ], md=4, align="center"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(
                                    className="fa-solid fa-gauge",
                                    style={'font-size': '25px', 'color': '#CC0130', 'display': 'inline-block'}
                                ),
                                html.H3(
                                    id="average_intensity",
                                    style={'display': 'inline-block', 'margin-left': '5px'}
                                ),
                            ]),
                            html.P("Average intensity"),
                        ], style={'padding': '5px 0px 0px 5px'}),
                    ], style={'padding': '0px', 'margin': '0px'})
                ], md=4, align="center"),
            ], align="center"),
        ], md=6, align="center"),
        dbc.Col([
            html.P([
                "The map displays all incidents recorded in the database for your selected initiator and \
                target countries and timeframe. Please note that our database only covers incidents that have \
                a political dimension. This includes incidents that have not (yet) been politicized and cases for \
                which no political motivation and/or a political affiliation of the attacker(s) has been reported. \
                The graph below shows our inclusion criteria along with the number of incidents corresponding to \
                each inclusion criteria."
            ]),
        ]),
    ]),

    *make_break(1),

    dbc.Row([
        dbc.Col([
            *make_break(1),
            html.P(html.B("Number of incidents"), style={"font-size": "1rem"}),
            dbc.Spinner(
                children=[dcc.Graph(id='map', style={'width': '100%', 'height': '480px'})],
                color="#002C38",
                delay_show=300,
            ),
        ], md=6),
        dbc.Col([
            *make_break(1),
            html.P(html.B("Types of incidents included in the database"), style={"font-size": "1rem"}),
            dcc.Graph(id="inclusion_graph")
        ], md=6),
    ]),
])
