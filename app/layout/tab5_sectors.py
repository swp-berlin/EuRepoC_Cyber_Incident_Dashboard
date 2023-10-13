from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    CONFIG, generate_intensity_popover, generate_text_with_popover_icon,
    generate_incident_details_modal, generate_key_insights_layout, generate_datatable_details_layout)


modal_sectors = generate_incident_details_modal(modal_body_id="modal_sectors_content", modal_id="modal_sectors")


mean_intensity_sectors_popover = generate_intensity_popover(target_id="mean_intensity_sectors_info")
mean_intensity_sectors_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_sectors_info", popover=mean_intensity_sectors_popover)


sectors_key_insights_layout = generate_key_insights_layout(
    nb_incidents_id="nb_incidents_sectors",
    average_intensity_id="average_intensity_sectors",
    mean_intensity_popover_icon=mean_intensity_sectors_popover_icon,
    description_text_id="sectors_description_text",
    selected_item_id="sectors_selected",
    clear_click_data_id="clear_sectors_click_data",
)


sectors_details_datatable_layout = generate_datatable_details_layout(
    datatable_id="sectors_datatable",
    column_name="incident_type",
    column_label="Incident type",
    modal_layout=modal_sectors,
)


sectors_tab = dbc.Container([
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("What are the most frequently targeted sectors?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="sectors_title", style={"font-size": "1rem"}),
                        dcc.Graph(
                            id='sectors_graph',
                            config={
                                **CONFIG,
                            },
                            style={'height': '500px'}
                        ),
                        dcc.Store(id='top_sector_store'),
                        dcc.Store(id='top_sector_value_store'),
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.I(
                            "Note as of 01/02/2023, the EuRepoC expanded its inclusion criteria to \
                            additional types of critical infrastructure, including chemicals, water, food, \
                            critical manufacturing, waste management and space.",
                            style={"font-weight": "italics"}
                        )
                    ], style={"margin-top": "10px"})
                ]),
            ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
            *sectors_key_insights_layout,
        ]),
        *sectors_details_datatable_layout,
    ])
])
