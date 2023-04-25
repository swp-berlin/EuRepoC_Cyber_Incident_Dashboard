from dash import Dash
import pandas as pd
import geopandas as gpd
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import numpy as np
from layout.layout import full_layout
from server.tab1_mapview_callbacks import map_callback, map_title_callback
from server.main_callbacks import reset_button_callback, tab_change_callback
from server.common_callbacks import clear_selected_click_data_callback, \
    clear_active_cell_datatables_callback
from server.tab1_inclusion_criteria_callbacks import inclusion_criteria_graph_callback
from server.tab3_timeline_callbacks import timeline_graph_callback, timeline_title_callback, \
    timeline_datatable_callback, timeline_text_selection_callback
from server.tab2_network_callbacks import network_title_callback, \
    network_graph_callback, style_node_onclick_callback, network_text_selection_callback, network_datatable_callback
from server.tab4_types_callbacks import types_title_callback, types_graph_callback, \
    types_text_selection_callback, types_datatable_callback
from server.tab5_sectors_callbacks import sectors_title_callback, sectors_graph_callback, \
    sectors_text_selection_callback, sectors_datatable_callback

# ------------------------------------------------- READ DATA ---------------------------------------------------------
# TABLES
database = pd.read_csv("./data/eurepoc_dataset.csv")
database["start_date"] = pd.to_datetime(database["start_date"])
database["receiver_region"] = database["receiver_region"].fillna("")
database["receiver_country"] = database["receiver_country"].fillna("")
database["initiator_country"] = database["initiator_country"].fillna("")

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
cyto.load_extra_layouts()
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
    "Western Balkans (states)": "WBALKANS"
}


# ------------------------------------------------- APP -------------------------------------------------------------
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.icons.FONT_AWESOME]
)


# ------------------ CALLBACKS ------------------
reset_button_callback(app)
tab_change_callback(app)


# TAB 1
map_title_callback(app)
map_callback(app, df=map_data, geometry=geometry)
inclusion_criteria_graph_callback(app, df=inclusion_data, states_codes=states_codes)


# TAB 2
network_title_callback(app)
network_graph_callback(app, df=network, states_codes=states_codes)
style_node_onclick_callback(app)
network_text_selection_callback(app)
network_datatable_callback(app, df=database)
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


# TAB 3
timeline_title_callback(app)
timeline_graph_callback(app, df=timeline_data, states_codes=states_codes)
timeline_text_selection_callback(app)
timeline_datatable_callback(app, df=database, states_codes=states_codes)
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
types_datatable_callback(app, df=database, states_codes=states_codes)
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
sectors_datatable_callback(app, df=database, states_codes=states_codes)
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


server = app.server
app.layout = full_layout


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=True)
