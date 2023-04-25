from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output


def sectors_title_callback(app):
    @app.callback(
        Output("sectors_title", "children"),
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
            return html.P(html.B(f"Top targeted sectors by {initiator_country} in {receiver_country} between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top targeted sectors by cyber incidents between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Top targeted sectors by actors based in {initiator_country} between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top targeted sectors in {receiver_country} between {start_date} and {end_date}"))


def sectors_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output("sectors_graph", "figure"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
    )
    def update_main_targets(
            receiver_country_filter,
            initiator_country,
            start_date_start,
            start_date_end
    ):

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=receiver_country_filter,
            initiator_country=initiator_country,
            states_codes=states_codes
        )

        grouped_data = filtered_df.groupby(["receiver_category", "receiver_category_subcode"])["ID"].count().reset_index()
        grouped_data = grouped_data.sort_values(by="receiver_category", ascending=True).reset_index(drop=True)

        sectors_plot = px.sunburst(
            grouped_data,
            path=['receiver_category', 'receiver_category_subcode'],
            values='ID',
            color="receiver_category",
            color_discrete_map={"Corporate Targets": "#89BD9E",
                                "Critical infrastructure": "#CC0130",
                                "State institutions / political system": "#002C38",
                                "Social groups": "#847E89",
                                "Media": "#F4B942",
                                "Science": "#446E68",
                                "End user(s) / specially protected groups": "#863300",
                                "International / supranational organization": "#D8C537",
                                "Unknown": "#E06492",
                                "Other": "lightgrey",
                                },
        )
        sectors_plot.update_traces(
            hovertemplate='<b>%{label}</b>\
                          <br>Value: %{value} targets\
                          <br>Percentage of total targets: %{percentRoot:.2%}\
                          <br>Percentage of %{parent}: %{percentParent:.2%}'
        )
        marker_colors = list(sectors_plot.data[0].marker['colors'])
        marker_labels = list(sectors_plot.data[0]['labels'])
        new_marker_colors = ["rgba(0,0,0,0)" if label == "" else color for (color, label) in
                             zip(marker_colors, marker_labels)]
        marker_colors = new_marker_colors
        sectors_plot.data[0].marker['colors'] = marker_colors
        sectors_plot.update_layout(
            title="",
            font=dict(
                family="sans-serif",
                color="#002C38"
            ),
            margin=dict(l=0, r=0, t=25, b=0, pad=0),
            height=500,
        )

        return sectors_plot


def sectors_text_selection_callback(app):
    @app.callback(
        Output("sectors_selected", "children"),
        Input("sectors_graph", "clickData"),
    )
    def display_click_data(
            clickData
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Selected sector: ',
                html.Span(f'{clickData["points"][0]["label"]}', style={'font-weight': 'bold'})
            ])
        else:
            text = html.P(f'No data point selected', style={'font-style': 'italic'})
        return text


def sectors_datatable_callback(app, df=None, states_codes=None):
    @app.callback(
        Output(component_id='sectors_datatable', component_property='data'),
        Output(component_id='sectors_datatable', component_property='tooltip_data'),
        Output(component_id='sectors_datatable_store', component_property='data'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input("sectors_graph", "clickData")
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     start_date_start,
                     start_date_end,
                     graph_targets):

        # Filter data based on inputs
        filtered_data = df.copy(deep=True)

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
        if graph_targets:
            point = graph_targets["points"][0]["label"]
            filtered_data = filtered_data[
                filtered_data['receiver_category'].str.contains(point) | filtered_data[
                    'receiver_category_subcode'].str.contains(point)
                ]
        start_date = pd.to_datetime(start_date_start).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(start_date_end).strftime('%Y-%m-%d')
        filtered_data = filtered_data[
            (filtered_data['start_date'] >= start_date) & (filtered_data['start_date'] <= end_date)]

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['name', 'start_date', "incident_type"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                         for row in data]

        return data, tooltip_data, filtered_data.to_dict('records')
