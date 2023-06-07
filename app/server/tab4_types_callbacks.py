from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text


def types_title_callback(app):
    @app.callback(
        Output("types_title", "children"),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
    )
    def selection_text_output(receiver_country,
                              initiator_country,
                              start_date_start,
                              start_date_end):

        start_date = pd.to_datetime(start_date_start).strftime('%d-%m-%Y')
        end_date = pd.to_datetime(start_date_end).strftime('%d-%m-%Y')

        if initiator_country == "All countries":
            initiator_country = None

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(
                html.B(f"Types of cyber incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}")
            )
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(
                html.B(f"Types of cyber incidents across all countries between {start_date} and {end_date}")
            )
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(
                html.B(f"Types of cyber incidents initiated by actors based in {initiator_country} between {start_date} and {end_date}")
            )
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(
                html.B(f"Types of cyber incidents against {receiver_country} between {start_date} and {end_date}")
            )


# types_data
def types_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('types_graph', 'figure'),
        Output("types_description_text", "children"),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        start_date_start,
                        start_date_end):

        if input_initiator_country == "All countries":
            input_initiator_country = None

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=input_receiver_country,
            initiator_country=input_initiator_country,
            states_codes=states_codes
        )

        if filtered_df.empty:
            fig = empty_figure(height_value=450)
            key_text = html.P("There are no incidents matching the selected filters.")
        else:
            grouped_data = filtered_df.groupby(["incident_type"]).agg(
                {'ID': 'nunique', "weighted_cyber_intensity": "mean"}
            ).reset_index()
            grouped_data['bubble_size'] = grouped_data['ID'] * grouped_data['weighted_cyber_intensity']
            grouped_data['bubble_size'] = grouped_data['bubble_size'].fillna(1)
            grouped_data = grouped_data[grouped_data['incident_type'] != 'Not available']
            max_id_freq = grouped_data["ID"].idxmax()
            max_type_freq = grouped_data.loc[max_id_freq, "incident_type"].capitalize()
            max_id_intense = grouped_data["weighted_cyber_intensity"].idxmax()
            max_type_intense = grouped_data.loc[max_id_intense, "incident_type"].lower()
            max_id_combined = grouped_data["bubble_size"].idxmax()
            max_type_combined = grouped_data.loc[max_id_combined, "incident_type"].capitalize()

            if grouped_data.empty:
                key_text = html.Div([html.P("No cyber incidents for the selected options")])
            elif max_type_freq == max_type_intense == max_type_combined:
                key_text = html.Div([html.Span(f"Only "),
                                     html.Span(f"{max_type_freq} ", style={"font-weight": "bold"}),
                                     html.Span("incidents occurred for the selected options")]),
            elif max_type_freq == max_type_combined != max_type_intense:
                key_text = html.Div([html.Span(f"{max_type_freq} ", style={"font-weight": "bold"}),
                                     html.Span("incidents combine both high frequency and high intensity, however, "),
                                     html.Span(f"{max_type_intense}", style={"font-weight": "bold"}),
                                     html.Span(" is the most intense type of incident for the selected options"),
                                     html.Span(f" ({round(grouped_data['weighted_cyber_intensity'].max(),1)} intensity).")])
            else:
                key_text = html.Div([
                    html.P([
                        html.Span(f"{max_type_freq}", style={"font-weight": "bold"}),
                        html.Span(" is the most frequent type of incident for the selected options "),
                        html.Span(f"({grouped_data['ID'].max()} incidents)"),
                        html.Span(", while "), html.Span(f"{max_type_intense}", style={"font-weight": "bold"}),
                        html.Span(" is the most intense "),
                        html.Span(f"({round(grouped_data['weighted_cyber_intensity'].max(),1)} intensity). "),
                        html.Span(f"{max_type_combined}", style={"font-weight": "bold"}),
                        html.Span(" incidents combine high frequency and high intensity.")
                    ])
                ])

            fig = px.scatter(grouped_data, x="ID", y="weighted_cyber_intensity", color="incident_type",
                             size="bubble_size", size_max=60,
                             color_discrete_sequence=['#CC0130', '#002C38', '#89BD9E', '#847E89', '#F4B942', "#79443B"],
                             hover_name="incident_type",
                             hover_data=["ID", "weighted_cyber_intensity", "incident_type"],
                             )

            fig.update_traces(textfont=dict(color='black'),
                              marker=dict(line_width=3))

            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Total incidents: %{x}<br>Average intensity: %{y:.2f}<extra></extra>')

            fig.update_layout(xaxis_title="Number of incidents",
                              yaxis_title="Average intensity",
                              legend_title="",
                              hovermode='closest',
                              hoverlabel=dict(
                                    bgcolor="#002C38",
                                    font_family="Lato",
                                ),
                              showlegend=False,
                              legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.4,
                                ),
                              font=dict(
                                  family="Lato",
                                  color="#002C38",
                                  size=14
                              ),
                              xaxis=dict(
                                  range=[0, grouped_data['ID'].max() + grouped_data['ID'].max()*0.1],
                                  gridcolor='rgba(0, 0, 0, 0.1)',
                                  zerolinecolor='rgba(0, 44, 56, 0.5)',
                                  zerolinewidth=0.5,
                                  showline=True,
                                  linecolor='rgba(0, 44, 56, 0.5)',
                                  linewidth=0.5,
                              ),
                              yaxis=dict(
                                  range=[0, None],
                                  gridcolor='rgba(0, 0, 0, 0.1)',
                                  showline=True,
                                  linecolor='rgba(0, 44, 56, 0.5)',
                                  linewidth=0.5,
                              ),
                              margin=dict(l=0, r=0, t=25, b=0, pad=0),
                              plot_bgcolor='white',
                              dragmode=False
                              )

        """fig.add_shape(type='line',
                      x0=grouped_data['ID'].median(),
                      y0=grouped_data['weighted_cyber_intensity'].min(),
                      x1=grouped_data['ID'].median(),
                      y1=grouped_data['weighted_cyber_intensity'].max(),
                      line=dict(color='lightgrey', width=2, dash='dot'))

        fig.add_shape(type='line',
                      x0=grouped_data['ID'].min(),
                      y0=grouped_data['weighted_cyber_intensity'].median(),
                      x1=grouped_data['ID'].max(),
                      y1=grouped_data['weighted_cyber_intensity'].median(),
                      line=dict(color='lightgrey', width=2, dash='dot'))"""

        return fig, key_text


def types_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='types_datatable', component_property='data'),
        Output(component_id='types_datatable', component_property='tooltip_data'),
        Output(component_id="modal_types", component_property='is_open'),
        Output(component_id="modal_types_content", component_property='children'),
        Output(component_id="nb_incidents_types", component_property='children'),
        Output(component_id="average_intensity_types", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="types_graph", component_property="clickData"),
        Input(component_id="types_datatable", component_property="derived_virtual_data"),
        Input(component_id="types_datatable", component_property='active_cell'),
        Input(component_id="types_datatable", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_types", component_property="is_open"),
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
            types_clickdata=clickData,
        )

        if clickData:
            nb_incidents = len(filtered_data)
            average_intensity = round(pd.to_numeric(filtered_data["weighted_cyber_intensity"]).mean(), 2)
        else:
            nb_incidents = metric_values["nb_incidents"]
            average_intensity = metric_values["average_intensity"]

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime("%Y-%m-%d")

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['ID', 'name', 'start_date', "weighted_cyber_intensity"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                        for row in data]

        status, modal = create_modal_text(
            data=data_dict,
            index=index,
            derived_virtual_data=derived_virtual_data,
            active_cell=active_cell,
            page_current=page_current,
            is_open=is_open
        )

        return data, tooltip_data, status, modal, nb_incidents, average_intensity


def types_text_selection_callback(app):
    @app.callback(
        Output('types_selected', 'children'),
        Input('types_graph', 'clickData'),
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
                'Type of incident selected: ',
                html.Span(f'{clickData["points"][0]["customdata"][0]}', style={'font-weight': 'bold'})
            ])
        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                ),
                ' Click on a bubble in the graph to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})
        return text
