from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    CONFIG, generate_intensity_popover,
    generate_text_with_popover_icon, generate_incident_details_modal,
    generate_key_insights_layout, generate_datatable_details_layout
)


modal_responses = generate_incident_details_modal(modal_body_id="modal_responses_content", modal_id="modal_responses")


mean_intensity_responses_popover = generate_intensity_popover(target_id="mean_intensity_responses_info")
mean_intensity_responses_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_responses_info", popover=mean_intensity_responses_popover)


responses_key_insights_layout = generate_key_insights_layout(
    nb_incidents_id="nb_incidents_responses",
    average_intensity_id="average_intensity_responses",
    mean_intensity_popover_icon=mean_intensity_responses_popover_icon,
    description_text_id="responses_description_text",
    response_tab=True
)


responses_details_datatable_layout = generate_datatable_details_layout(
    datatable_id="responses_datatable",
    column_name="number_of_political_responses",
    column_label="Number of political responses",
    column_name_2="number_of_legal_responses",
    column_label_2="Number of legal responses",
    column_name_3="weighted_cyber_intensity",
    column_label_3="Weighted cyber intensity",
    modal_layout=modal_responses,
)


responses_nb_tab = dbc.Row([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id="responses_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px'}
                        ),
                        html.Div(
                            id="responses_donut_annotation",
                            style={
                                "font-size": "0.7rem",
                                "margin-bottom": "15px"
                            }
                        )
                    ], sm=12, xs=12, lg=12, xl=12, xxl=12, md=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            html.B("Percentage of incidents with a political or legal response by intensity score"),
                            style={"font-size": "1rem"}),
                        dcc.Graph(
                            id="responses_graph_2",
                            config={
                                **CONFIG,
                            },
                            style={'height': '300px'}
                        ),
                        html.Div(id="responses_scatter_annotation", style={"font-size": "0.7rem", "margin-top": "10px"})
                    ], sm=12, xs=12, lg=12, xl=12, xxl=12, md=12),
                ]),
            ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
            *responses_key_insights_layout,
        ]),
        *responses_details_datatable_layout,
])
