from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break
import pickle
from datetime import date


today = date.today()


receiver_countries_dd_options = pickle.load(
    open("./data/receiver_countries_dd.pickle", "rb")
)
initiator_country_dd_options = pickle.load(
    open("./data/initiator_country_dd.pickle", "rb")
)


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
            "This dashboard displays key trends in cyber incidents that are tracked as part of our database and \
            is updated daily. Click on the Tabs to the right to find statistics covering aspects from the evolution  \
            in the number of cyber incidents, to main types of incidents, targets, and initiators. On each Tab,  \
            clicking on the datapoints in the graphs displays all related incidents. Using the dropdown menus below,  \
            you can choose specific combitions of initiators and targets to update all graphs according to your selection",
            ], style={'text-align': 'justify'}),
        html.P("Please see our methodology section for further information!", style={'text-align': 'center'}),
        html.Div(
            id="sidebar_text_default",
            children=[
                html.P(
                    html.B("Select intiatitor and target countries", style={'text-align': 'left', 'font-size': '1rem'})
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
            id='initiator_country_dd_div',
            children=[
                html.Label(html.B('Initiator country')),
                dcc.Dropdown(id='initiator_country_dd',
                             options=initiator_country_dd_options),
                *make_break(1),
            ]
        ),
        html.Label(html.B('Target country')),
        dcc.Dropdown(id='receiver_country_dd',
                     options=receiver_countries_dd_options,
                     value="Global (states)",
                     clearable=False),
        html.Div(
            id='incident_type_dd_div',
            children=[
                *make_break(1),
                html.Label(html.B('Incident type')),
                dcc.Dropdown(
                    id='incident_type_dd',
                    options=[
                         "Data theft",
                         "Data theft & Doxing",
                         "Disruption",
                         "Hijacking with Misuse",
                         "Hijacking without Misuse",
                         "Ransomware"
                    ]
                ),
            ]
        ),
        html.Div(
            id='date-picker-range-div',
            children=[
                *make_break(1),
                html.Label(html.B('Date of cyber incidents')),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=date(2000, 1, 1),
                    max_date_allowed=date(today.year, today.month, today.day),
                    start_date=date(2000, 1, 1),
                    end_date=date(today.year, today.month, today.day),
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
        html.Div(
            id='date-picker-range-div_attributions',
            children=[
                *make_break(1),
                html.Label(html.B('Date of cyber incidents')),
                dcc.DatePickerRange(
                    id='date-picker-range_attributions',
                    min_date_allowed=date(2010, 1, 1),
                    max_date_allowed=date(today.year, today.month, today.day),
                    start_date=date(2010, 1, 1),
                    end_date=date(today.year, today.month, today.day),
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
