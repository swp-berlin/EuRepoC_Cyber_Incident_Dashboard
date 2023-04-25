from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output


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


#types_data
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

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=input_receiver_country,
            initiator_country=input_initiator_country,
            states_codes=states_codes
        )

        grouped_data = filtered_df.groupby(["incident_type"]).agg(
            {'ID': 'nunique', "weighted_cyber_intensity": "mean"}
        ).reset_index()
        grouped_data['bubble_size'] = grouped_data['ID'] * grouped_data['weighted_cyber_intensity']
        grouped_data = grouped_data[grouped_data['incident_type'] != 'Not available']
        max_id_freq = grouped_data["ID"].idxmax()
        max_type_freq = grouped_data.loc[max_id_freq, "incident_type"]
        max_id_intense = grouped_data["weighted_cyber_intensity"].idxmax()
        max_type_intense = grouped_data.loc[max_id_intense, "incident_type"]
        max_id_combined = grouped_data["bubble_size"].idxmax()
        max_type_combined = grouped_data.loc[max_id_combined, "incident_type"]

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
                   html.Span(
                       " is the most intense "),
                   html.Span(f"({round(grouped_data['weighted_cyber_intensity'].max(),1)} intensity). But "),
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
                          legend_title="Incident type",
                          hovermode='closest',
                          hoverlabel=dict(
                                bgcolor="#002C38",
                                font_size=12,
                                font_family="sans-serif",
                            ),
                          legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.29,
                            ),
                            font=dict(
                                family="sans-serif",
                                color="#002C38",
                            ),
                          xaxis=dict(
                              range=[0, grouped_data['ID'].max() + grouped_data['ID'].max()*0.1],
                          ),
                          yaxis=dict(
                              range=[0, None],
                          ),
                          margin=dict(l=0, r=0, t=25, b=0, pad=0),
                          plot_bgcolor='rgba (0, 44, 56, 0.05)',
                          )

        fig.add_shape(type='line',
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
                      line=dict(color='lightgrey', width=2, dash='dot'))

        return fig, key_text

def types_datatable_callback(app, df=None, states_codes=None):
    @app.callback(
        Output(component_id='types_datatable', component_property='data'),
        Output(component_id='types_datatable', component_property='tooltip_data'),
        Output(component_id="types_datatable_store", component_property="data"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input("types_graph", "clickData")
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     start_date_start,
                     start_date_end,
                     clickData):

        # Check if start and end dates have changed
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        # Filter data based on inputs
        filtered_data = df.copy(deep=True)
        filtered_data["receiver_country"] = filtered_data["receiver_country"].fillna("").astype(str)
        filtered_data["initiator_country"] = filtered_data["initiator_country"].fillna("").astype(str)
        filtered_data["incident_type"] = filtered_data["incident_type"].fillna("").astype(str)

        region_filter = None

        if receiver_country_filter == "Global (states)":
            receiver_country_filter = None
            region_filter = None
        elif "(states)" in receiver_country_filter and receiver_country_filter != "Global (states)":
            for key in states_codes.keys():
                if receiver_country_filter == key:
                    receiver_country_filter = None
                    region_filter = states_codes[key]
        elif receiver_country_filter == "EU (member states)":
            receiver_country_filter = None
            region_filter = r"\bEU\b|\bEU[;\s]|[;\s]EU[;\s]"
        elif receiver_country_filter == "NATO (member states)":
            receiver_country_filter = None
            region_filter = "NATO"
        else:
            receiver_country_filter = receiver_country_filter
            region_filter = None

        if receiver_country_filter and receiver_country_filter != 'Global (states)':
            filtered_data = filtered_data[filtered_data['receiver_country'].str.contains(receiver_country_filter)]
        if region_filter:
            filtered_data = filtered_data[filtered_data['receiver_region'].str.contains(region_filter, regex=True)]
        if initiator_country_filter:
            filtered_data = filtered_data[filtered_data['initiator_country'].str.contains(initiator_country_filter)]
        if clickData:
            filtered_data = filtered_data[filtered_data['incident_type'].str.contains(clickData['points'][0]['customdata'][0])]
        start_date = pd.to_datetime(start_date_start).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(start_date_end).strftime('%Y-%m-%d')
        filtered_data = filtered_data[
            (filtered_data['start_date'] >= start_date) & (filtered_data['start_date'] <= end_date)]

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['name', 'start_date', "weighted_cyber_intensity"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                        for row in data]

        return data, tooltip_data, filtered_data.to_dict('records')

def types_text_selection_callback(app):
    @app.callback(Output('types_selected', 'children'),
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
            text = html.P(f'No bubble selected', style={'font-style': 'italic'})
        return text
