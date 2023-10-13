from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    CONFIG, generate_intensity_popover,
    generate_text_with_popover_icon, generate_incident_details_modal,
    generate_datatable_details_layout, generate_key_insights_layout,
)


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


timeline_key_insights = generate_key_insights_layout(
    nb_incidents_id="nb_incidents_timeline",
    average_intensity_id="average_intensity_timeline",
    mean_intensity_popover_icon=mean_intensity_timeline_popover_icon,
    description_text_id="timeline_description_text",
    selected_item_id="timeline_selected",
    clear_click_data_id="clear_timeline_click_data",
)


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
            *timeline_key_insights
        ]),
        *timeline_datatable_layout
    ])
)
