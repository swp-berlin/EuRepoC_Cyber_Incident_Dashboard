from dash import Dash, Output, Input
import pandas as pd
import geopandas as gpd
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import numpy as np
import pickle
from datetime import datetime as dt
from layout.main_layout import serve_layout
from server.main_callbacks import (
    reset_button_callback, tab_change_callback,
    change_conflict_dyads_tab, change_attributions_tab,
    change_responses_tab
)
from server.common_callbacks import (
    clear_selected_click_data_callback, clear_active_cell_datatables_callback
)
from server.server_functions import filter_datatable
from server.tab1_mapview_callbacks import (
    map_callback, map_title_callback,
    metric_values_callback
)
from server.tab1_inclusion_criteria_callbacks import inclusion_criteria_graph_callback
from server.tab2_network_callbacks import (
    network_title_callback, network_graph_callback,
    style_node_onclick_callback, network_text_selection_callback,
    network_datatable_callback
)
from server.tab2_network_bar_graph_callbacks import (
    network_bar_graph_callback, network_bar_text_selection_callback,
    network_bar_datatable_callback
)
from server.tab3_timeline_callbacks import (
    timeline_graph_callback, timeline_title_callback,
    timeline_datatable_callback, timeline_text_selection_callback
)
from server.tab4_types_callbacks import (
    types_title_callback, types_graph_callback,
    types_text_selection_callback, types_datatable_callback
)
from server.tab5_sectors_callbacks import (
    sectors_title_callback, sectors_graph_callback,
    sectors_text_selection_callback, sectors_datatable_callback
)
from server.tab6_attributions_callbacks import (
    attributions_title_callback, attributions_graph_callback,
    attributions_datatable_callback, attributions_text_selection_callback,
    attributions_question_title
)
from server.tab6_attributions_types_callbacks import (
    attributions_graph_callback_types, attributions_datatable_callback_types,
    attributions_text_selection_callback_types
)
from server.tab7_responses_callbacks import (
    responses_title_callback, responses_graph_callback,
    responses_datatable_callback, responses_question_title
)
from server.tab7_responses_type_callbacks import responses_graph_callback_types, responses_datatable_callback_types
from server.tab8_initiators_callbacks import (
    initiators_title_callback, initiators_graph_callback,
    initiators_text_selection_callback, initiators_datatable_callback
)

# ------------------------------------------------- READ DATA ---------------------------------------------------------


# TABLES
database = pd.read_csv("./data/eurepoc_dataset.csv")
database["start_date"] = pd.to_datetime(database["start_date"])
database["receiver_region"] = database["receiver_region"].fillna("")
database["receiver_country"] = database["receiver_country"].fillna("")
database["initiator_country"] = database["initiator_country"].fillna("")
full_data_dict = pickle.load(open("./data/full_data_dict.pickle", "rb"))
full_data_dict_index_map = pickle.load(open("./data/full_data_dict_index_map.pickle", "rb"))

# MAP
map_data = pd.read_csv("./data/dashboard_map_data.csv")
map_data["weighted_cyber_intensity"] = pd.to_numeric(map_data["weighted_cyber_intensity"])
map_data["start_date"] = pd.to_datetime(map_data["start_date"])

# Map geometry
geometry = gpd.read_file('./data/geojson.json')

# INCLUSION CRITERIA
inclusion_data = pd.read_csv("./data/dashboard_inclusion_data.csv")
inclusion_data["start_date"] = pd.to_datetime(inclusion_data["start_date"])
inclusion_data["receiver_region"] = inclusion_data["receiver_region"].fillna("")

# NETWORK
network = pd.read_csv("./data/dashboard_network_data.csv")
network["receiver_region"] = network["receiver_region"].fillna("")

# TIMELINE
timeline_data = pd.read_csv("./data/dashboard_evolution_data.csv")
timeline_data["start_date"] = pd.to_datetime(timeline_data["start_date"])

# INCIDENT TYPES
types_data = pd.read_csv("./data/dashboard_incident_types_data.csv")
types_data["start_date"] = pd.to_datetime(types_data["start_date"])

# TARGETED SECTORS
sectors_data = pd.read_csv("./data/dashboard_targeted_sectors_data.csv")
sectors_data["start_date"] = pd.to_datetime(sectors_data["start_date"])
sectors_data['receiver_category_subcode'] = sectors_data['receiver_category_subcode'].replace(np.nan, "")

# ATTRIBUTIONS
attributions_data = pd.read_csv("./data/dashboard_attributions_data.csv")
attributions_basis = pd.read_csv("./data/dashboard_attributions_basis_data.csv")
attributions_data["start_date"] = pd.to_datetime(attributions_data["start_date"])
attributions_basis["start_date"] = pd.to_datetime(attributions_basis["start_date"])

# RESPONSES
responses_data = pd.read_csv("./data/dashboard_responses_data.csv")
responses_data["start_date"] = pd.to_datetime(responses_data["start_date"])
responses_details = pd.read_csv("./data/dashboard_responses_details_data.csv")
responses_details["start_date"] = pd.to_datetime(responses_details["start_date"])

# INITIATORS
initiators_data = pd.read_csv("./data/dashboard_initiators_data.csv")
initiators_data["start_date"] = pd.to_datetime(initiators_data["start_date"])


cyto.load_extra_layouts()

states_codes = {
    "Asia (states)": "ASIA",
    "Central America (states)": "CENTAM",
    "Central Asia (states)": "CENTAS",
    "Collective Security Treaty Organization (states)": "CSTO",
    "EU (member states)": "EU",
    "Eastern Asia (states)": "EASIA",
    "Europe (states)": "EUROPE",
    "Gulf Countries (states)": "GULFC",
    "Mena Region (states)": "MENA",
    "Middle East (states)": "MEA",
    "NATO (member states)": "NATO",
    "North Africa (states)": "NAF",
    "Northeast Asia (states)": "NEA",
    "Oceania (states)": "OC",
    "Shanghai Cooperation Organisation (states)": "SCO",
    "South Asia (states)": "SASIA",
    "South China Sea (states)": "SCS",
    "Southeast Asia (states)": "SEA",
    "Sub-Saharan Africa (states)": "SSA",
    "Western Balkans (states)": "WBALKANS",
    "Africa (states)": "AFRICA",
}


# ------------------------------------------------- APP -------------------------------------------------------------
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.icons.FONT_AWESOME]
)


# ------------------ CALLBACKS ------------------

@app.callback(
    Output('modal-status', 'children'),
    Input('close', 'n_clicks'),
)
def close_modal(n):
    if n is not None:
        return "false"
    return "true"


reset_button_callback(app)
tab_change_callback(app)


@app.callback(
    Output('note-start-date', 'style'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_note_visibility(start_date, end_date):
    if start_date == "2000-01-01" and end_date == str(dt.now().date()):
        start_date = None
        end_date = None

    if start_date and end_date:
        return {'font-size': '0.8rem', 'font-style': 'italic', 'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('metric_values', 'data'),
    Input(component_id='receiver_country_dd', component_property='value'),
    Input(component_id='initiator_country_dd', component_property='value'),
    Input(component_id='incident_type_dd', component_property='value'),
    Input(component_id='date-picker-range', component_property='start_date'),
    Input(component_id='date-picker-range', component_property='end_date'),
)
def update_plot(input_receiver_country,
                input_initiator_country,
                input_incident_type,
                start_date_start,
                start_date_end,
                ):

    if input_initiator_country == "All countries":
        input_initiator_country = None
    if input_incident_type == "All":
        input_incident_type = None

    filtered_df = filter_datatable(
        df=database,
        receiver_country_filter=input_receiver_country,
        initiator_country_filter=input_initiator_country,
        incident_type_filter=input_incident_type,
        start_date=start_date_start,
        end_date=start_date_end,
        states_codes=states_codes,
        types_clickdata=None,
        targets_clickdata=None,
        initiators_clickdata=None,
    )

    filtered_df['weighted_cyber_intensity'] = pd.to_numeric(filtered_df['weighted_cyber_intensity'])

    # If the filtered DataFrame is empty indicate 0 incidents and empty map which still shows the selected country
    if filtered_df.empty:
        nb_incidents = 0
        average_intensity = 0

    else:
        nb_incidents = filtered_df['ID'].nunique()
        average_intensity = round(filtered_df['weighted_cyber_intensity'].mean(), 2)

    metric_values = {
        'nb_incidents': nb_incidents,
        'average_intensity': average_intensity
    }

    return metric_values


# TAB 1
map_title_callback(app)
map_callback(app, df=map_data, geometry=geometry)
inclusion_criteria_graph_callback(app, df=inclusion_data, states_codes=states_codes)
metric_values_callback(app)

# TAB 2
change_conflict_dyads_tab(app)
network_title_callback(app)
network_graph_callback(app, df=network, states_codes=states_codes)
style_node_onclick_callback(app)
network_text_selection_callback(app)
network_datatable_callback(
    app,
    df=database,
    data_dict=full_data_dict,
    index=full_data_dict_index_map,
    states_codes=states_codes
)
clear_selected_click_data_callback(
    app,
    output_id="cytoscape-graph",
    output_component_property="tapNode",
    input_id="clear_network_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="network_datatable",
    input_component_property="tapNode",
    input_id="cytoscape-graph"
)

network_bar_graph_callback(app, df=network, states_codes=states_codes)
network_bar_text_selection_callback(app)
network_bar_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="dyads-bar-graph",
    output_component_property="clickData",
    input_id="clear_dyads_bar_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="dyads_bar_datatable",
    input_component_property="clickData",
    input_id="dyads-bar-graph"
)


# TAB 3
timeline_title_callback(app)
timeline_graph_callback(app, df=timeline_data, states_codes=states_codes)
timeline_text_selection_callback(app)
timeline_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="timeline_graph",
    output_component_property="clickData",
    input_id="clear_timeline_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="timeline_datatable",
    input_component_property="clickData",
    input_id="timeline_graph")


# TAB 4
types_title_callback(app)
types_graph_callback(app, df=types_data, states_codes=states_codes)
types_text_selection_callback(app)
types_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="types_graph",
    output_component_property="clickData",
    input_id="clear_types_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="types_datatable",
    input_component_property="clickData",
    input_id="types_graph")


# TAB 5
sectors_title_callback(app)
sectors_graph_callback(app, df=sectors_data, states_codes=states_codes)
sectors_text_selection_callback(app)
sectors_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="sectors_graph",
    output_component_property="clickData",
    input_id="clear_sectors_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="sectors_datatable",
    input_component_property="clickData",
    input_id="sectors_graph")


# TAB 6
change_attributions_tab(app)
attributions_question_title(app)
attributions_title_callback(app)
attributions_graph_callback(app, df=attributions_data, states_codes=states_codes)
attributions_text_selection_callback(app)
attributions_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="attributions_graph",
    output_component_property="clickData",
    input_id="clear_attributions_click_data"
)
clear_active_cell_datatables_callback(
    app,
    output_id="attributions_datatable",
    input_component_property="clickData",
    input_id="attributions_graph")

attributions_graph_callback_types(app, df=attributions_basis, states_codes=states_codes)
attributions_text_selection_callback_types(app)
attributions_datatable_callback_types(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_selected_click_data_callback(
    app,
    output_id="attributions_graph_types",
    output_component_property="clickData",
    input_id="clear_attributions_click_data_types"
)
clear_active_cell_datatables_callback(
    app,
    output_id="attributions_datatable_types",
    input_component_property="clickData",
    input_id="attributions_graph_types")


# TAB 7
responses_question_title(app)
change_responses_tab(app)
responses_title_callback(app)
responses_graph_callback(app, df=responses_data, states_codes=states_codes)
responses_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_active_cell_datatables_callback(
    app,
    output_id="responses_datatable",
    input_component_property="clickData",
    input_id="responses_graph")

responses_graph_callback_types(app, data=responses_details, states_codes=states_codes)
responses_datatable_callback_types(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
clear_active_cell_datatables_callback(
    app,
    output_id="responses_datatable_types",
    input_component_property="clickData",
    input_id="responses_graph_types")


# TAB 8
initiators_title_callback(app)
initiators_graph_callback(app, df=initiators_data, states_codes=states_codes)
initiators_datatable_callback(
    app,
    df=database,
    states_codes=states_codes,
    data_dict=full_data_dict,
    index=full_data_dict_index_map
)
initiators_text_selection_callback(app)
clear_active_cell_datatables_callback(
    app,
    output_id="initiators_datatable",
    input_component_property="clickData",
    input_id="initiators_graph")
clear_selected_click_data_callback(
    app,
    output_id="initiators_graph",
    output_component_property="clickData",
    input_id="clear_initiator_click_data"
)

server = app.server
app.layout = serve_layout
app.title = "EuRepoC Cyber Incident Dashboard"

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
