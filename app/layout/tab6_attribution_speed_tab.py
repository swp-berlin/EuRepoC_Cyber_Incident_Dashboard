from dash import dcc
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    CONFIG, generate_intensity_popover,
    generate_text_with_popover_icon, generate_incident_details_modal,
    generate_key_insights_layout, generate_datatable_details_layout
)


modal_attributions = generate_incident_details_modal(
    modal_body_id="modal_attributions_content",
    modal_id="modal_attributions"
)


mean_intensity_attributions_popover = generate_intensity_popover(target_id="mean_intensity_attributions_info")
mean_intensity_attributions_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_attributions_info", popover=mean_intensity_attributions_popover)


attribution_speed_key_insights_layout = generate_key_insights_layout(
    nb_incidents_id="nb_incidents_attributions",
    average_intensity_id="average_intensity_attributions",
    mean_intensity_popover_icon=mean_intensity_attributions_popover_icon,
    description_text_id="attributions_description_text",
    selected_item_id="attributions_selected",
    clear_click_data_id="clear_attributions_click_data",
)


attribution_speed_details_datatable_layout = generate_datatable_details_layout(
    datatable_id="attributions_datatable",
    column_name="number_of_attributions",
    column_label="Number of attributions",
    modal_layout=modal_attributions,
)


attributions_tab_speed = dbc.Row([
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id="attributions_graph",
                    config={
                        **CONFIG,
                    },
                    style={'height': '450px'}
                )
            ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
            *attribution_speed_key_insights_layout,
        ]),
        *attribution_speed_details_datatable_layout,
])
