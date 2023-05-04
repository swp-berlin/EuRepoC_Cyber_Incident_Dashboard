from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable
from server.common_callbacks import create_modal_text


def sectors_title_callback(app):
    @app.callback(
        Output("sectors_title", "children"),
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

        if incident_type:
            type = incident_type
        else:
            type = "cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(html.B(f"Top sectors targeted by {type} incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top sectors targeted by {type} incidents between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Top sectors targeted by {type} incidents from actors based in {initiator_country} between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top sectors targeted by {type} incidents in {receiver_country} between {start_date} and {end_date}"))


def sectors_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output("sectors_graph", "figure"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
    )
    def update_main_targets(
            receiver_country_filter,
            initiator_country,
            incident_type,
            start_date_start,
            start_date_end
    ):

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=receiver_country_filter,
            initiator_country=initiator_country,
            incident_type=incident_type,
            states_codes=states_codes
        )

        values_data = filtered_df.groupby(["receiver_category"])["ID"].nunique().reset_index()
        grouped_data = filtered_df.groupby(["receiver_category", "receiver_category_subcode"])["ID"].nunique().reset_index()
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
                                "Science": "#79443B",
                                "End user(s) / specially protected groups": "#0094BD",
                                "International / supranational organization": "#99abaf",
                                "Unknown": "#fdf1d9",
                                "Other": "f3f2f3",
                                },
        )
        sectors_plot.update_traces(
            hovertemplate='<b>%{label}</b>\
                          <br>Incidents: %{value}\
                          <br>Percentage of total: %{percentRoot:.2%}\
                          <br>Percentage of sub-sector %{parent}: %{percentParent:.2%}'
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
                family="Lato",
                color="#002C38",
                size=14
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
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'incident_type_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Selected sector: ',
                html.Span(f'{clickData["points"][0]["label"]}', style={'font-weight': 'bold'})
            ])
        else:
            text = html.P(f'No data point selected', style={'font-style': 'italic'})
        return text


def sectors_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='sectors_datatable', component_property='data'),
        Output(component_id='sectors_datatable', component_property='tooltip_data'),
        Output(component_id="modal_sectors", component_property='is_open'),
        Output(component_id="modal_sectors_content", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="sectors_graph", component_property="clickData"),
        Input(component_id="sectors_datatable", component_property='derived_virtual_data'),
        Input(component_id="sectors_datatable", component_property='active_cell'),
        Input(component_id="sectors_datatable", component_property='page_current'),
        State(component_id="modal_sectors", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     incident_type_filter,
                     start_date_start,
                     start_date_end,
                     graph_targets,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     is_open):
        # Check if start and end dates have changed
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'incident_type_dd.value':
            graph_targets = None

        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=initiator_country_filter,
            incident_type_filter=incident_type_filter,
            start_date=start_date_start,
            end_date=start_date_end,
            states_codes=states_codes,
            targets_clickdata=graph_targets,
        )

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime("%Y-%m-%d")

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['ID', 'name', 'start_date', "incident_type"]].to_dict('records')
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

        return data, tooltip_data, status, modal
