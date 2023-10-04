from dash.dependencies import Input, Output
from layout.tab1_mapview import map_tab
from layout.tab2_network import network_tab
from layout.tab3_timeline import timeline_tab
from layout.tab4_types import types_tab
from layout.tab5_sectors import sectors_tab
from layout.tab6_attributions import attributions_tab
from layout.tab7_responses import responses_tab
from layout.tab8_initiator_types import initiators_tab
from layout.tab2_network_cyto_tab import network_cyto_tab
from layout.tab2_initiator_bar_tab import network_bar_tab
from layout.tab6_attribution_types_tab import attributions_tab_types
from layout.tab6_attribution_speed_tab import attributions_tab_speed
from layout.tab7_responses_nb_tab import responses_nb_tab
from layout.tab7_responses_types import responses_types_tab
from datetime import date
from datetime import datetime as dt


# reset filter selection button callback
def reset_button_callback(app):
    @app.callback(
        Output('receiver_country_dd', 'value'),
        Output('initiator_country_dd', 'value'),
        Output("incident_type_dd", "value"),
        Output('date-picker-range', 'start_date'),
        Output('date-picker-range', 'end_date'),
        Input("reset", "n_clicks")
    )
    def on_button_click(n_clicks):
        if n_clicks is not None:
            return "Global (states)", \
                None, \
                None, \
                date(2000, 1, 1), \
                dt.now().date()
                #date(2010, 1, 1), \
                #dt.now().date()


# tab change callback
def tab_change_callback(app):
    @app.callback(
        Output("card-content", "children"),
        Output("sidebar_text_default", "style"),
        Output("sidebar_text_network", "style"),
        Output("initiator_country_dd_div", "style"),
        Output("date-picker-range-div", "style"),
        Output("incident_type_dd_div", "style"),
        [Input("card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if active_tab == "tab-1":
            return map_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        elif active_tab == "tab-2":
            return network_tab, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        elif active_tab == "tab-3":
            return timeline_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        elif active_tab == "tab-4":
            return types_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}
        elif active_tab == "tab-5":
            return sectors_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        elif active_tab == "tab-6":
            return attributions_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        elif active_tab == "tab-7":
            return responses_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}
        elif active_tab == "tab-8":
            return initiators_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}


def change_network_tab(app):
    @app.callback(
        Output("network-card-content", "children"),
        [Input("network-card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if active_tab == "network_tab":
            return network_cyto_tab
        else:
            return network_bar_tab


def change_attributions_tab(app):
    @app.callback(
        Output("attributions-card-content", "children"),
        [Input("attributions-card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if active_tab == "timeline_tab":
            return attributions_tab_speed
        else:
            return attributions_tab_types

def change_responses_tab(app):
    @app.callback(
        Output("responses-card-content", "children"),
        [Input("responses-card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if active_tab == "response_number_tab":
            return responses_nb_tab
        else:
            return responses_types_tab
