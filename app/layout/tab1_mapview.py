from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break, CONFIG, generate_intensity_popover, generate_text_with_popover_icon


cyber_intensity_popover = generate_intensity_popover(target_id="cyber_intensity_popover")
cyber_intensity_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="cyber_intensity_popover", popover=cyber_intensity_popover
)

threat_groups_popover = dbc.Popover([
        dbc.PopoverBody([
            "This is the number of known actors/groups having initiated cyber incidents recorded in our database \
            for your current selection."
        ]),
    ], target="threat_groups_info", trigger="hover")

threat_groups_popover_icon = generate_text_with_popover_icon(
    text="Threat groups", span_id="threat_groups_info", popover=threat_groups_popover
)

inclusion_criteria_popover = dbc.Popover([
        dbc.PopoverBody([
            "Please note that that one incident can have multiple inclusion criteria"
        ]),
    ], target="inclusion_criteria_info", trigger="hover")


map_tab = dbc.Row([

    dbc.Row([
        dbc.Col([
            html.Div(id="selected_options_text", style={'text-align': 'center'}),
        ], style={'margin': '20px'}),
    ]),

    dbc.Row([
        dbc.Col([
            html.P([
                "The map displays all incidents recorded in our database, based on your selected initiator country, \
                 target country and timeframe. Please note that our database only covers ",
                html.B("cyber incidents with a political dimension"),
                 ". This includes incidents that have not yet been politicised and \
                 cases where no political motivation and/or affiliation of the attacker(s) has been reported. \
                 The graph on the bottom right illustrates our inclusion criteria, along with the number of incidents \
                 corresponding to each criterion."
            ]),
        ], style={"margin-top": "10px"}),
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
                ], style={"margin-bottom": "10px"}, md=4, align="center"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(
                                    className="fa-solid fa-user-group",
                                    style={'font-size': '25px', 'color': '#CC0130', 'display': 'inline-block'}),
                                html.H3(id="nb_threat_groups", style={'display': 'inline-block', 'margin-left': '5px'}),
                            ]),
                            threat_groups_popover_icon,
                        ], style={'padding': '5px 0px 15px 5px'}),
                    ], style={'padding': '0px', 'margin': '0px'})
                ], style={"margin-bottom": "10px"}, md=4, align="center"),
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
                            cyber_intensity_popover_icon,
                        ], style={'padding': '5px 0px 15px 5px'}),
                    ], style={'padding': '0px', 'margin': '0px'})
                ], style={"margin-bottom": "10px"}, md=4, align="center"),
            ], align="center"),
        ], lg=6, align="center"),
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
        ], lg=6),
        dbc.Col([
            *make_break(1),
            html.Span([
                html.B("Types of incidents included in the database", style={"font-size": "1rem"}),
                html.I(
                    id="inclusion_criteria_info",
                    className="fa-regular fa-circle-question",
                    style={
                        'text-align': 'center',
                        'font-size': '12px',
                        'color': '#002C38',
                        'right': '-14px', 'top': '-2px',
                        'position': 'absolute'
                    },
                ),
                inclusion_criteria_popover
            ], className="position-relative"),
            dcc.Graph(
                id="inclusion_graph",
            config={
                **CONFIG,
            }

            ),
        ], lg=6),
    ]),
])
