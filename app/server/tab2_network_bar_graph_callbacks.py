from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime as dt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text
import re



def network_bar_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('network-bar-graph', 'figure'),
        Output('network-bar-graph-key-insight', 'children'),
        Input('receiver_country_dd', 'value'),
        Input("network-bar-graph", "clickData"),
    )
    def create_graph(input_receiver_country,
                        clickData,
                        ):

        filtered_df = filter_database_by_output(
            df=df,
            date_start="2000-01-01",
            date_end=str(dt.now().date()),
            receiver_country=input_receiver_country,
            initiator_country=None,
            incident_type=None,
            states_codes=states_codes
        )

        if filtered_df.empty:
            fig = empty_figure(height_value=600)
            text = html.Div(html.P("No cyber incidents corresponding to the selected criteria."))

        else:
            total = filtered_df["ID"].nunique()
            filtered_df['initiator_country'] = filtered_df.apply(
                lambda row: "Unknown"
                if (row['initiator_country'] == 'Not available' and
                    (row['initiator_name'] == 'Not available' or row['initiator_name'] == "Unknown"))
                else row['initiator_country'],
                axis=1)
            grouped_df = filtered_df.groupby(['initiator_country'])["ID"].nunique().reset_index().sort_values(by='ID', ascending=True).tail(10)
            grouped_df['percentage'] = (grouped_df['ID'] / total * 100).round(2)
            grouped_df['text'] = grouped_df.apply(lambda row: f"{row['ID']} ({row['percentage']}%)",
                                                  axis=1)

            if clickData:
                selected_initiator = clickData["points"][0]["label"]

                colors = ['#002C38' if x != selected_initiator else '#cc0130' for x in grouped_df['initiator_country']]

                fig = go.Figure(data=[go.Bar(
                    y=grouped_df['initiator_country'],
                    x=grouped_df['ID'],
                    text=grouped_df['text'],
                    orientation='h',
                    marker=dict(
                        color=colors,
                    ),
                    hovertemplate='%{x} incidents from %{y}<extra></extra>'
                )])

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(showticklabels=False),
                    plot_bgcolor='white',
                    font=dict(
                        family="Lato",
                        color="#002C38",
                        size=14
                    ),
                    margin=dict(l=0, r=0, t=45, b=0, pad=0),
                    height=600,
                    dragmode=False
                )

            else:
                fig = go.Figure(data=[go.Bar(
                    y=grouped_df['initiator_country'],
                    x=grouped_df['ID'],
                    text=grouped_df['text'],
                    orientation='h',
                    marker=dict(
                        color="#002C38",
                    ),
                    hovertemplate='%{x} incidents from %{y}<extra></extra>'
                )])

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    xaxis=dict(showticklabels=False),
                    plot_bgcolor='white',
                    font=dict(
                        family="Lato",
                        color="#002C38",
                        size=14
                    ),
                    margin=dict(l=0, r=0, t=45, b=0, pad=0),
                    height=600,
                    dragmode=False
                )

            if grouped_df.iloc[-1]['initiator_country'] == "Unknown" and input_receiver_country != "Global (states)":
                main_init = f"Most cyber incidents ({grouped_df.iloc[-1]['percentage']}%) against {input_receiver_country} remain unattributed, meaning the country of origin is unknown."
            elif grouped_df.iloc[-1]['initiator_country'] == "Unknown" and input_receiver_country == "Global (states)":
                main_init = f"Most cyber incidents ({grouped_df.iloc[-1]['percentage']}%) remain unattributed, meaning the country of origin is unknown."
            else:
                main_init = f"Most cyber incidents ({grouped_df.iloc[-1]['percentage']}%) against {input_receiver_country} originate from {grouped_df.iloc[-1]['initiator_country']}"

            text = html.Div([
                    html.P([
                        main_init
                    ])
            ])

        return fig, text


def network_bar_text_selection_callback(app):
    @app.callback(
        Output('network-bar-selected', 'children'),
        Input('network-bar-graph', 'clickData'),
        Input(component_id='receiver_country_dd', component_property='value'),
    )
    def display_click_data(
            clickData,
            receiver_country_filter,
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Initiator country selected: ',
                html.Span(f'{clickData["points"][0]["label"]}', style={'font-weight': 'bold'})
            ])
        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                ),
                ' Click on a bar in the graph to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})
        return text


def network_bar_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='network_datatable_graph', component_property='data'),
        Output(component_id='network_datatable_graph', component_property='tooltip_data'),
        Output(component_id="modal_network_graph", component_property='is_open'),
        Output(component_id="modal_network_content_graph", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id="network-bar-graph", component_property="clickData"),
        Input(component_id="network_datatable_graph", component_property="derived_virtual_data"),
        Input(component_id="network_datatable_graph", component_property='active_cell'),
        Input(component_id="network_datatable_graph", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_network_graph", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     clickData,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     metric_values,
                     is_open):

        # Filter data based on inputs
        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=None,
            start_date="2000-01-01",
            end_date=str(dt.now().date()),
            states_codes=states_codes,
            initiators_country_clickdata=clickData,
        )

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime("%Y-%m-%d")

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['ID', 'name', 'start_date', "incident_type"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                        for row in data]

        copied_data_dict = data_dict.copy()
        copied_index = index.copy()
        status, modal = create_modal_text(
            data=copied_data_dict,
            index=copied_index,
            derived_virtual_data=derived_virtual_data,
            active_cell=active_cell,
            page_current=page_current,
            is_open=is_open
        )

        return data, tooltip_data, status, modal
