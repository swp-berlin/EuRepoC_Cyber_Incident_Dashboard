from dash import html, dcc
import dash_bootstrap_components as dbc
from layout.layout_functions import make_break
from layout.sidebar import generate_sidebar


mobile_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Mobile device notice")),
                dbc.ModalBody([
                    "Welcome to our Cyber Incident Dashboard!",
                    html.Br(),
                    "For best results, please view the dashboard on a ",
                    html.B("desktop device"),
                    "."
                ]),
                dbc.ModalFooter(
                    dbc.Button("Continue", id="close", className="ml-auto")
                ),
            ],
            id="mobile_modal",
            centered=True,
            is_open=False,
        ),
        html.Div(id='modal-status', style={'display': 'none'}, children="true")
    ]
)

card_tabs = dbc.Row([
    dbc.Col([
        dbc.Tabs(
            [
                dbc.Tab(label="Overview", tab_id="tab-1", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Conflict dyads", tab_id="tab-2", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Timeline", tab_id="tab-3", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Incident types", tab_id="tab-4", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Targeted sectors", tab_id="tab-5", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Attributions", tab_id="tab-6", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Responses", tab_id="tab-7", tab_style={"marginRight": "auto"}),
                dbc.Tab(label="Initiator types", tab_id="tab-8", tab_style={"marginRight": "auto"}),
            ],
            id="card-tabs",
            active_tab="tab-1",
            className="tab-row"
        ),
        html.Div(id="card-content"),
    ], xxl=12, xl=12, lg=12, md=12, sm=12, xs=12),
], style={"margin": "15px 0px 0px 0px"})

def serve_layout():
    full_layout = dbc.Container(
        children=[
            mobile_modal,
            dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    max_intervals=1
                ),
            dbc.Row([
                dcc.Store(id='metric_values'),
                dcc.Store(id='prev-receiver-country'),
                dcc.Store(id='prev-initiator-country'),
                dcc.Store(id='prev-incident-type'),
                dcc.Store(id='prev-start-date'),
                dcc.Store(id='prev-end-date'),
            ]),

            #*make_break(2),

            dbc.Row([
                dbc.Col([
                    generate_sidebar(),
                ], xxl=3, xl=3, lg=3, md=4, sm=12, xs=12),

                dbc.Col([
                    dbc.Row([
                        card_tabs
                    ]),
                ], xxl=9, xl=9, lg=9, md=8, sm=12, xs=12),
            ]),
        ],
        style={"padding": "10px 35px"}, fluid=True
    )
    return full_layout
