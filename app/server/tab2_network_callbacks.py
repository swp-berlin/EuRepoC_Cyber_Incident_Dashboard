from dash import html
from dash.dependencies import Input, Output, State
from dash import callback_context as ctx
from server.common_callbacks import create_modal_text
import pandas as pd
import numpy as np
import pickle
import re


country_flags = pickle.load(open("./data/country_flags.pickle", "rb"))


def construct_details(edge_type, node, text):
    node_details = html.Div([])
    if len(edge_type) > 0:
        for edge in edge_type:
            list_items = html.Ul([
                html.Li("Number of incidents: " + str(edge["nb_incidents"])),
                html.Li("Average cyber intensity: " + str(edge["cyber_intensity"])),
                html.Li("Main threat group: " + str(edge["initiator_name"])),
                html.Li("Main type of initiators: " + str(edge["initiator_category"])),
                html.Li(f"Main cyber issue: {edge['cyber_conflict_issue']}"),
            ])

        node_details = html.Div([
            html.B(f"Incidents {text} {node['data']['id']}"),
            list_items
        ], style={'padding-top': '10px'})

    return node_details


def network_title_callback(app):
    @app.callback(Output("network_title", 'children'),
                  [Input('receiver_country_dd', 'value')])
    def update_network_title(receiver_country):
        if receiver_country == "Global (states)":
            return html.Div([html.B("Main cyber conflict dyads across all countries")])
        else:
            return html.Div([
                html.B(
                    f"Main countries of origin of incidents against {receiver_country} and main countries targeted by initators in {receiver_country}"
                )
            ])


def network_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('cytoscape-graph', 'elements'),
        Output("nodes_graph", 'data'),
        Input('receiver_country_dd', 'value')
    )
    def network_graph(receiver_country):

        filtered_data = df.copy(deep=True)
        region_filter = None

        if receiver_country == "Global (states)":
            receiver_country = None
            region_filter = None
            head = 25
        elif "(states)" in receiver_country and receiver_country != "Global (states)":
            for key in states_codes.keys():
                if receiver_country == key:
                    receiver_country = None
                    region_filter = states_codes[key]
                    head = 25
        elif receiver_country == "EU (member states)":
            receiver_country = None
            region_filter = "EU\(MS\)"
            head = 25
        elif receiver_country == "NATO (member states)":
            receiver_country = None
            region_filter = "NATO"
            head = 25
        else:
            receiver_country = receiver_country
            region_filter = None
            head = 12

        def get_network_data(df1, df2, column_name):
            merged_df = pd.merge(df1, df2, on=['receiver_country', 'initiator_country'])
            merged_df['ID_y'] = merged_df.groupby(['receiver_country', 'initiator_country'])['ID_y'].transform('max')
            merged_df.drop_duplicates(subset=['receiver_country', 'initiator_country'], keep='first', inplace=True)
            merged_df = merged_df.rename(columns={"ID_y": "ID"})
            merged_df = merged_df.drop(columns=[column_name])
            merged_df = merged_df.merge(df2, how="left",
                                        on=["initiator_country", "receiver_country", "ID"])
            merged_df_with_list = merged_df.groupby(
                ["initiator_country", "receiver_country", "weighted_cyber_intensity", "ID_x", "ID"]).agg(
                {
                    column_name: lambda x: list(x)
                }
            ).reset_index()
            return merged_df_with_list

        def prep_network_data(data, country_type, country, filtered_region, table_head):
            if country is None and filtered_region is None:
                network_filtered_full = data.drop_duplicates()
            elif filtered_region:
                network_filtered_full = data.loc[(data["receiver_region"].str.contains(filtered_region, regex=True))].drop_duplicates()
            elif country:
                network_filtered_full = data.loc[(data[country_type] == country)].drop_duplicates()

            network_grouped = network_filtered_full.groupby(["receiver_country", "initiator_country"]).agg(
                {'ID': 'nunique', 'weighted_cyber_intensity': 'mean'}).reset_index()
            network_group_top_names = network_filtered_full.groupby(
                ["receiver_country", "initiator_country", "initiator_name"]).agg({'ID': 'nunique'}).reset_index()
            network_group_top_categories = network_filtered_full.groupby(
                ["receiver_country", "initiator_country", "initiator_category"]).agg({'ID': 'nunique'}).reset_index()
            network_grouped_top_issues = network_filtered_full.groupby(
                ["receiver_country", "initiator_country", "cyber_conflict_issue"]).agg({'ID': 'nunique'}).reset_index()
            top_names = get_network_data(network_grouped, network_group_top_names, "initiator_name")
            top_categories = get_network_data(network_grouped, network_group_top_categories, "initiator_category")
            top_issues = get_network_data(network_grouped, network_grouped_top_issues, "cyber_conflict_issue")

            full_network = top_names.merge(
                top_categories,
                how="outer",
                on=["initiator_country", "receiver_country", "weighted_cyber_intensity", "ID_x"],
                suffixes=("_initiator", "_actor")
            )

            full_network = full_network.merge(
                top_issues,
                how="outer",
                on=["initiator_country", "receiver_country", "weighted_cyber_intensity", "ID_x"],
                suffixes=("_initiator", "_actor")
            )

            full_network["weight"] = (np.sqrt(full_network["ID_x"]) * full_network["weighted_cyber_intensity"])/2
            full_network = full_network.sort_values(by="weight", ascending=False).head(table_head)
            full_network = full_network.sort_values(by="ID_x", ascending=False)

            return full_network

        received_network = prep_network_data(filtered_data, "receiver_country", receiver_country, region_filter, head)
        initiated_network = prep_network_data(filtered_data, "initiator_country", receiver_country, region_filter, head)

        network_full = pd.concat([received_network, initiated_network])
        network_full['initiator_name'] = network_full['initiator_name'].apply(
            lambda x: '; '.join(x) if isinstance(x, (list, tuple)) else x)
        network_full['initiator_category'] = network_full['initiator_category'].apply(
            lambda x: '; '.join(x) if isinstance(x, (list, tuple)) else x)
        network_full['cyber_conflict_issue'] = network_full['cyber_conflict_issue'].apply(
            lambda x: '; '.join(x) if isinstance(x, (list, tuple)) else x)
        network_full = network_full.drop_duplicates()

        all_nodes = list(
            set(
                network_full["initiator_country"].unique().tolist() + network_full["receiver_country"].unique().tolist()
            )
        )
        flags = []
        for node in all_nodes:
            for i in range(len(country_flags["country_name"])):
                if node == country_flags["country_name"][i]:
                    flags.append(country_flags["flag"][i])

        nodes = []
        for i in range(len(all_nodes)):
            nodes.append({"data": {"id": all_nodes[i], "flag": flags[i]}})

        edges = []
        for index, row in network_full.iterrows():
            edges.append({"data": {
                "source": row["initiator_country"],
                "target": row["receiver_country"],
                "weight": row["weight"],
                "nb_incidents": str(row["ID_x"]),
                "cyber_intensity": str(round(row["weighted_cyber_intensity"], 2)),
                "initiator_name": row["initiator_name"],
                "initiator_category": row["initiator_category"],
                "cyber_conflict_issue": row["cyber_conflict_issue"],
            }})

        elements = nodes + edges

        return elements, all_nodes


def style_node_onclick_callback(app):
    @app.callback(
        Output('cytoscape-graph', 'stylesheet'),
        Output("cytoscape-tapNodeData-output-title", "children"),
        Output('cytoscape-tapNodeData-output', 'children'),
        [Input('cytoscape-graph', 'tapNode'),
         Input('receiver_country_dd', 'value')],
    )
    def generate_stylesheet(node, selected_country):

        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            node = None

        if not node:
            empty_card = html.Div([
                html.P(
                    html.I("Click on a country (circle) to see details"),
                    style={"text-align": "center", "vertical-align": "middle"}
                ),
            ], style={'padding-top': '10px', 'padding-bottom': '2px'})

            if selected_country == "Global (states)":
                title_card = html.B(f"Main conflict dyads")
            else:
                title_card = html.B(f"Incidents against and from {selected_country}")

            no_node_stylesheet = [
                {
                    "selector": 'node',
                    'style': {
                        'label': 'data(flag)',
                        'background-color': '#002C38',
                        'width': '30px',
                        'height': '30px',
                        'font-family': 'Lato',
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'line-color': 'rgb(230, 234, 235)',
                        'target-arrow-color': 'rgb(230, 234, 235)',
                        'arrow-shape': 'triangle',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'width': 'data(weight)',
                        'min-width': '1px',
                        'max-width': '5px',
                    }
                },
                {
                    "selector": 'edge[source = "{}"]'.format(selected_country),
                    "style": {
                        'line-color': '#335660',
                        'target-arrow-color': '#335660',
                    }
                },
                {
                    "selector": 'edge[target = "{}"]'.format(selected_country),
                    "style": {
                        'line-color': '#d63459',
                        'target-arrow-color': '#d63459',
                    }
                },
            ]

            return no_node_stylesheet, title_card, empty_card

        stylesheet = [
            {
                "selector": 'node',
                'style': {
                    'label': 'data(flag)',
                    'background-color': '#002C38',
                    'width': '30px',
                    'height': '30px',
                    'font-family': 'Lato',
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': 'rgb(230, 234, 235)',
                    'target-arrow-color': 'rgb(230, 234, 235)',
                    'arrow-shape': 'triangle',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'width': 'data(weight)',
                    'min-width': '1px',
                    'max-width': '5px',
                }
            },
            {
                "selector": 'node[id = "{}"]'.format(node['data']['id']),
                "style": {
                    'background-color': '#CC0130',
                }
            }
        ]

        edge_colors = {
            "source": {
                "line-color": "#335660",
                "target-arrow-color": "#335660",
            },
            "target": {
                "line-color": "#d63459",
                "target-arrow-color": "#d63459",
            },
        }

        for direction in ["source", "target"]:
            edge_selector = 'edge[{} = "{}"]'.format(direction, selected_country)
            edge_style = edge_colors[direction]

            stylesheet.append({
                "selector": edge_selector,
                "style": edge_style,
            })

        edges_for_selected_target = [edge for edge in node["edgesData"] if edge["target"] == node["data"]["id"]]
        edges_for_selected_source = [edge for edge in node["edgesData"] if edge["source"] == node["data"]["id"]]

        if selected_country == "Global (states)" or selected_country == node['data']['id']:

            title_card = html.B(f"{node['data']['id']}")

            node_details_1 = html.Div([])
            if len(edges_for_selected_target) > 0:
                list_items = html.Ul([
                    html.Li(
                        edge["source"] + ": " + str(edge["nb_incidents"]) + " incidents",
                        style={"margin": "0.2rem 0"})for edge in edges_for_selected_target])

                node_details_1 = html.Div([
                    html.B("Main country of origin of incidents"),
                    list_items
                ], style={'padding-top': '10px'})

            node_details_2 = html.Div([])
            if len(edges_for_selected_source) > 0:
                list_items = html.Ul([
                    html.Li(
                        edge["target"] + ": " + str(edge["nb_incidents"]) + " incidents",
                        style={"margin": "0.2rem 0"}) for edge in edges_for_selected_source])

                node_details_2 = html.Div([
                    html.B("Main countries targeted by national initiators"),
                    list_items
                ], style={'padding-top': '10px'})

            combined = [node_details_1, node_details_2]
            node_details = html.Div(combined)

        else:
            title_card = html.B([
                f"{node['data']['id']}", html.Span(" ⇄ ", style={'font-size': '15px'}), f"{selected_country}"
            ])

            node_details_1 = construct_details(edges_for_selected_source, node, "from")
            node_details_2 = construct_details(edges_for_selected_target, node, "initiated against")

            combined = [node_details_1, node_details_2]
            node_details = html.Div(combined)

        return stylesheet, title_card, node_details


def network_text_selection_callback(app):
    @app.callback(
        Output("network_selected", "children"),
        Input('cytoscape-graph', 'tapNode'),
        Input('receiver_country_dd', 'value'),
    )
    def display_click_data(
            clickData,
            receiver_country_filter,
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Selected data point: ',
                html.Span(f"{clickData['data']['flag']}",
                          style={'font-weight': 'bold'})
            ])
        else:
            text = html.P(f'No data point selected', style={'font-style': 'italic'})
        return text


def network_datatable_callback(app, df=None, data_dict=None, index=None):
    @app.callback(
        Output('network_datatable', 'data'),
        Output('network_datatable', 'tooltip_data'),
        Output("modal_network", 'is_open'),
        Output("modal_network_content", 'children'),
        Input('cytoscape-graph', 'tapNode'),
        Input('receiver_country_dd', 'value'),
        Input("nodes_graph", "data"),
        Input("network_datatable", "derived_virtual_data"),
        Input("network_datatable", 'active_cell'),
        Input("network_datatable", 'page_current'),
        State("modal_network", "is_open"),
    )
    # DataTable
    def update_table(node, receiver_country_filter, nodes_present, derived_virtual_data, active_cell, page_current, is_open):
        # Filter data based on inputs
        copied_data = df.copy(deep=True)
        copied_data['start_date'] = copied_data['start_date'].dt.date
        copied_data['receiver_country'] = copied_data['receiver_country'].fillna('')
        copied_data['initiator_country'] = copied_data['initiator_country'].fillna('')

        if receiver_country_filter == 'Global (states)':
            match_regex = '|'.join(nodes_present)
            filtered_data = copied_data[copied_data['receiver_country'].str.contains(match_regex, flags=re.IGNORECASE)]
            if node:
                received = copied_data[copied_data['initiator_country'].str.contains(node['data']['id']) & copied_data[
                    'receiver_country'].str.contains(match_regex, flags=re.IGNORECASE)]
                initiated = copied_data[copied_data['receiver_country'].str.contains(node['data']['id']) & copied_data[
                    'initiator_country'].str.contains(match_regex, flags=re.IGNORECASE)]
                filtered_data = pd.concat([received, initiated])
                filtered_data = filtered_data.drop_duplicates()
        else:
            if node and node['data']['id'] == receiver_country_filter:
                received = copied_data[copied_data['receiver_country'].str.contains(receiver_country_filter)]
                initiated = copied_data[copied_data['initiator_country'].str.contains(receiver_country_filter)]
                filtered_data = pd.concat([received, initiated])
                filtered_data = filtered_data.drop_duplicates()
            elif node and node['data']['id'] != receiver_country_filter:
                received = copied_data[copied_data['initiator_country'].str.contains(node['data']['id']) & copied_data[
                    'receiver_country'].str.contains(receiver_country_filter)]
                initiated = copied_data[copied_data['receiver_country'].str.contains(node['data']['id']) & copied_data[
                    'initiator_country'].str.contains(receiver_country_filter)]
                filtered_data = pd.concat([received, initiated])
                filtered_data = filtered_data.drop_duplicates()
            else:
                received = copied_data[copied_data['receiver_country'].str.contains(receiver_country_filter)]
                initiated = copied_data[copied_data['initiator_country'].str.contains(receiver_country_filter)]
                filtered_data = pd.concat([received, initiated])
                filtered_data = filtered_data.drop_duplicates()

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[
            ['ID', 'name', 'start_date', "initiator_country", "initiator_category", "receiver_country", "incident_type"]
        ].to_dict('records')

        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()} for row in data]

        #filtered_data = filtered_data.fillna("Not available")
        #filtered_data["attribution_date"] = filtered_data["attribution_date"].replace(" 00:00:00","")

        status, modal = create_modal_text(
            data=data_dict,
            index=index,
            derived_virtual_data=derived_virtual_data,
            active_cell=active_cell,
            page_current=page_current,
            is_open=is_open
        )

        return data, tooltip_data, status, modal
