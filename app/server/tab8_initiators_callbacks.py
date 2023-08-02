from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text
import re


def initiators_title_callback(app):
    @app.callback(
        Output("initiators_text", "children"),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
    )
    def selection_text_output(receiver_country,
                              initiator_country,
                              incident_type,
                              start_date_start,
                              start_date_end):

        start_date = pd.to_datetime(start_date_start).strftime('%d-%m-%Y')
        end_date = pd.to_datetime(start_date_end).strftime('%d-%m-%Y')

        if initiator_country == "All countries":
            initiator_country = None
        if incident_type == "All":
            incident_type = None

        if incident_type:
            type = incident_type
        else:
            type = "cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(html.B(f"Number of {type.lower()} incidents by type of initiator from {initiator_country} against {receiver_country} \
            between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of {type.lower()} incidents by type of initiator between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Number of {type.lower()} incidents by type of initiator from {initiator_country} \
            between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of {type.lower()} incidents by type of initiator against {receiver_country} \
            between {start_date} and {end_date}"))


def initiators_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('initiators_graph', 'figure'),
        Output('initiators_graph_2', 'figure'),
        Output('initiators_description_text', 'children'),
        Output("nb_threat_groups_initiators", 'children'),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input("initiators_graph", "clickData"),
        Input("nb_threat_groups_data", "data"),

    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        incident_type,
                        start_date_start,
                        start_date_end,
                        clickData,
                        nb_threat_groups
                        ):

        if input_initiator_country == "All countries":
            input_initiator_country = None
        if incident_type == "All":
            incident_type = None

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=input_receiver_country,
            initiator_country=input_initiator_country,
            incident_type=incident_type,
            states_codes=states_codes
        )

        if filtered_df.empty:
            fig = empty_figure(height_value=300)
            fig_2 = empty_figure(height_value=300)
            text = html.Div(html.P("No cyber incidents corresponding to the selected criteria."))
            number_of_groups = 0

        else:
            grouped_df = filtered_df.groupby(['initiator_category'])["ID"].nunique().reset_index()
            grouped_df = grouped_df.sort_values(by=['ID'], ascending=True)
            grouped_df_2 = filtered_df.groupby(['initiator_category', "initiator_name"])["ID"].nunique().reset_index()
            grouped_df_2['initiator_name'] = grouped_df_2['initiator_name'].apply(
                lambda x: re.match(r'([^/]*/[^/]*)/.*', x).group(1) if re.match(r'([^/]*/[^/]*)/.*', x) else x)
            top5_initiators = grouped_df_2.groupby('initiator_category').apply(
                lambda x: x.nlargest(10, 'ID')).reset_index(drop=True)

            number_of_groups = nb_threat_groups

            if clickData:
                selected_type = clickData["points"][0]["label"]

                number_of_groups = filtered_df[filtered_df['initiator_category'] == selected_type]['initiator_name'].nunique()

                colors = ['#002C38' if x != selected_type else '#cc0130' for x in grouped_df['initiator_category']]

                fig = go.Figure(data=[go.Bar(
                    y=grouped_df['initiator_category'],
                    x=grouped_df['ID'],
                    text=grouped_df['ID'],
                    orientation='h',
                    marker=dict(
                        color=colors,
                    ),
                    hoverinfo='none'
                )])

                fig.update_layout(
                    title="Initiator types",
                    title_font=dict(
                        size=14,
                    ),
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
                    height=459,
                    dragmode=False
                )

                top5_initiators_filtered = top5_initiators[top5_initiators["initiator_category"] == selected_type]

                fig_2 = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=['Initiator name', 'Number of incidents'],
                                fill_color='#002C38',
                                align='left',
                                font=dict(
                                    family="Lato",
                                    color="white",
                                    size=14
                                ),
                                height=30
                            ),
                            cells=dict(
                                values=[top5_initiators_filtered["initiator_name"], top5_initiators_filtered["ID"]],
                                fill_color='#F2F2F2',
                                align='left',
                                font=dict(
                                    family="Lato",
                                    color="#002C38",
                                    size=14
                                ),
                                height=30
                            )
                        )
                    ]
                )
                fig_2.update_layout(
                    title=f"Top 10 <b>{selected_type.lower()}</b> initiators",
                    plot_bgcolor='white',
                    font=dict(
                        family="Lato",
                        color="#002C38",
                        size=11,
                    ),
                    margin=dict(l=0, r=0, t=45, b=0, pad=0),
                    height=459,
                    dragmode=False
                )
            else:
                fig = px.bar(
                    grouped_df,
                    x="ID",
                    y="initiator_category",
                    orientation='h',
                    color_discrete_sequence=['#002C38'],
                    text="ID",
                    hover_data={'ID': False, 'initiator_category': False},
                    hover_name=None
                )
                fig.update_layout(
                    title="Initiator types",
                    title_font=dict(
                        size=16,
                    ),
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
                    height=459,
                    dragmode=False
                )

                top_10_data = grouped_df_2.groupby('initiator_name')["ID"].sum().reset_index()
                top_10_data = top_10_data.sort_values(by=['ID'], ascending=False).head(10)

                fig_2 = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=['Initiator name', 'Number of incidents'],
                                fill_color='#002C38',
                                align='left',
                                font=dict(
                                    family="Lato",
                                    color="white",
                                    size=14
                                ),
                                height=30
                            ),
                            cells=dict(
                                values=[top_10_data["initiator_name"], top_10_data["ID"]],
                                fill_color='#F2F2F2',
                                align='left',
                                font=dict(
                                    family="Lato",
                                    color="#002C38",
                                    size=14
                                ),
                                height=30
                            )
                        )
                    ]
                )

                fig_2.update_layout(
                    title=f"Top 10 initiator groups/actors",
                    plot_bgcolor='white',
                    font=dict(
                        family="Lato",
                        color="#002C38",
                        size=11,
                    ),
                    margin=dict(l=0, r=0, t=45, b=0, pad=0),
                    height=459,
                    dragmode=False
                )

            text = html.Div([
                    html.P([
                        html.Span("For the selected filters, the actors categorised as "),
                        html.Span(f""""{grouped_df.iloc[-1]['initiator_category'].lower()}", """, style={"font-weight": "bold"}),
                        html.Span(f" are the most common type of initiators of cyber incidents, with a total of {grouped_df.iloc[-1]['ID']} incident(s).")
                    ])
            ])

        return fig, fig_2, text, number_of_groups


def initiators_text_selection_callback(app):
    @app.callback(
        Output('initiator_selected', 'children'),
        Input('initiators_graph', 'clickData'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date')
    )
    def display_click_data(
            clickData,
            receiver_country_filter,
            initiator_country_filter,
            start_date_start,
            start_date_end
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Type of initiator selected: ',
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


def initiators_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='initiators_datatable', component_property='data'),
        Output(component_id='initiators_datatable', component_property='tooltip_data'),
        Output(component_id="modal_initiators", component_property='is_open'),
        Output(component_id="modal_initiators_content", component_property='children'),
        Output(component_id="nb_incidents_initiators", component_property='children'),
        Output(component_id="average_intensity_initiators", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="initiators_graph", component_property="clickData"),
        Input(component_id="initiators_datatable", component_property="derived_virtual_data"),
        Input(component_id="initiators_datatable", component_property='active_cell'),
        Input(component_id="initiators_datatable", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_initiators", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     start_date_start,
                     start_date_end,
                     clickData,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     metric_values,
                     is_open):

        if initiator_country_filter == "All countries":
            initiator_country_filter = None

        # Filter data based on inputs
        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=initiator_country_filter,
            start_date=start_date_start,
            end_date=start_date_end,
            states_codes=states_codes,
            initiators_clickdata=clickData,
        )

        if clickData:
            nb_incidents = len(filtered_data)
            average_intensity = round(pd.to_numeric(filtered_data["weighted_cyber_intensity"]).mean(), 2)
        else:
            nb_incidents = metric_values["nb_incidents"]
            average_intensity = metric_values["average_intensity"]

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

        return data, tooltip_data, status, modal, nb_incidents, average_intensity
