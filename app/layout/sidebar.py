from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break
import pickle
from datetime import date
from datetime import datetime as dt


# Reading in the dropdown menu options
receiver_countries_dd_options = pickle.load(open("./data/receiver_countries_dd.pickle", "rb"))
initiator_country_dd_options = pickle.load(open("./data/initiator_country_dd.pickle", "rb"))
initiator_country_dd_options[2]["label"] = "Africa (region)"


# Popovers
incident_type_popover = dbc.Popover(
    "Depicts the cyber incident(s) type concerning the reported consequences for the target(s): \
    Data theft, data theft with doxing, disruption, hijacking without misuse, and hijacking with misuse.",
    target="incident_type_dd_info",
    body=True,
    trigger="hover",
)


initiator_country_popover = dbc.Popover(
    "Describes a) the country of origin of the attributed initiating actor and b) the categorization \
    of the actor. Both terms apply to the incident’s planning and/or executing party. The latter can \
    also be a cyber proxy. The term “country“ – as applied to the selection list – comprises states, \
    provinces, and territories. This designation does not reflect an official position regarding the \
    status of a given country or region.",
    target="initiator_country_dd_info",
    body=True,
    trigger="hover",
)


receiver_country_popover = dbc.Popover(
    "Describes a) the country of origin of the targeted entities and b) the respective actor \
    categorization. The term “country“ – as applied to the selection list – comprises states, \
    provinces, and territories. This designation does not reflect an official position regarding \
    the status of a given country or region.",
    target="receiver_country_dd_info",
    body=True,
    trigger="hover",
)


# Sidebar body
def generate_sidebar():
    sidebar = dbc.Card([
        dbc.CardBody([
            *make_break(1),
            html.Div([
                html.I(
                    className="fa-solid fa-circle-info",
                    style={'text-align': 'center', 'font-size': '25px', 'color': '#CC0130'}
                )
            ], style={'text-align': 'center', 'margin-bottom': '5px'}),
            html.P([
                "This dashboard displays key trends in cyber incidents tracked in our database,  \
                and it is updated daily. Click on the tabs to the right to find statistics covering various aspects: \
                from the evolution of the number of cyber incidents to the main types of incidents, targets, \
                and initiators. On most tabs, clicking on the data points in the graphs will display all related \
                incidents. Using the dropdown menus below, you can select specific combinations of incident types, \
                initiators and targets to update all graphs according to your selection.",
                ], style={'text-align': 'justify'}),
            html.P([
                "Please see our ",
                html.A(href="https://eurepoc.eu/methodology", target="_blank", children="methodology"),
                " section for further information!"
            ], style={'text-align': 'center'}),
            html.Div(
                id="sidebar_text_default",
                children=[
                    html.P(
                        html.B(
                            "Select an incident type, initiator and target country",
                            style={'text-align': 'left', 'font-size': '1rem'}
                        )
                    ),
                ]
            ),
            html.Div(
                id="sidebar_text_network",
                children=[
                    html.P(html.B("Select a country",
                                  style={'text-align': 'left', 'font-size': '1rem'})),
                ]
            ),
            html.Div(
                id='incident_type_dd_div',
                children=[
                    html.Label([
                        html.Span([
                            html.B('Incident type '),
                            html.I(
                                id="incident_type_dd_info",
                                className="fa-regular fa-circle-question",
                                style={
                                    'text-align': 'center',
                                    'font-size': '12px',
                                    'color': '#002C38',
                                    'right': '-14px', 'top': '-2px',
                                    'position': 'absolute'
                                },
                            ),
                            incident_type_popover
                        ], className="position-relative"),
                    ]),
                    dcc.Dropdown(
                        id='incident_type_dd',
                        options=[
                            {"label": "All", "value": "All"},
                            {"label": "Data theft", "value": "Data theft"},
                            {"label": "Data theft & Doxing", "value": "Data theft & Doxing"},
                            {"label": "Disruption", "value": "Disruption"},
                            {"label": "Hijacking with Misuse", "value": "Hijacking with Misuse"},
                            {"label": "Hijacking without Misuse", "value": "Hijacking without Misuse"},
                            {"label": "Ransomware", "value": "Ransomware"},
                        ],
                        value="All",
                        clearable=False,
                        placeholder="All"
                    ),
                    *make_break(1),
                ]
            ),
            html.Div(
                id='initiator_country_dd_div',
                children=[
                    html.Label([
                        html.Span([
                            html.B('Origin country of initiator '),
                            html.I(
                                id="initiator_country_dd_info",
                                className="fa-regular fa-circle-question",
                                style={
                                    'text-align': 'center',
                                    'font-size': '12px',
                                    'color': '#002C38',
                                    'right': '-14px', 'top': '-2px',
                                    'position': 'absolute'
                                },
                            ),
                            initiator_country_popover
                        ], className="position-relative"),
                    ]),
                    dcc.Dropdown(id='initiator_country_dd',
                                 options=initiator_country_dd_options,
                                 value="All countries",
                                 clearable=False,
                                 placeholder="All countries",
                                 ),
                    *make_break(1),
                ]
            ),
            html.Div(id="target_country_div", children=[
                html.Label([
                    html.Span([
                        html.B('Receiver country '),
                        html.I(
                            id="receiver_country_dd_info",
                            className="fa-regular fa-circle-question",
                            style={
                                'text-align': 'center',
                                'font-size': '12px',
                                'color': '#002C38',
                                'right': '-14px', 'top': '-2px',
                                'position': 'absolute'
                            },
                        ),
                        receiver_country_popover
                    ], className="position-relative"),
                ]),
                dcc.Dropdown(id='receiver_country_dd',
                             options=receiver_countries_dd_options,
                             value="Global (states)",
                             clearable=False),
            ]),
            html.Div(
                id='date-picker-range-div',
                children=[
                    *make_break(1),
                    html.Label(html.B('Date of cyber incidents')),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        min_date_allowed=date(2000, 1, 1),
                        max_date_allowed=dt.now().date(),
                        start_date=date(2000, 1, 1),
                        end_date=dt.now().date(),
                        display_format='D/M/YYYY',
                        style={'width': '100%',
                               'color': 'rgb(0, 44, 56)',
                               'font-family': 'var(--bs-font-sans-serif)',
                               'text-align': 'left'
                               },
                        className="dash-bootstrap",
                    ),
                ]
            ),
            html.Div([
                dbc.Button(
                    "Reset selection",
                    id="reset",
                    className="mb-3",
                    n_clicks=0,
                    color="light",
                    style={'width': '100%'}
                )
            ], style={'margin-top': '20px'}),
            *make_break(1),
        ]),
    ], className="h-100")
    return sidebar
