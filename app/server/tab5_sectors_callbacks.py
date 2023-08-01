from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
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

        if initiator_country == "All countries":
            initiator_country = None
        if incident_type == "All":
            incident_type = None

        if incident_type:
            type = incident_type
        else:
            type = "cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(html.B(f"Top sectors targeted by {type.lower()} incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top sectors targeted by {type.lower()} incidents between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Top sectors targeted by {type.lower()} incidents from actors based in {initiator_country} between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Top sectors targeted by {type.lower()} incidents in {receiver_country} between {start_date} and {end_date}"))


def sectors_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output("sectors_graph", "figure"),
        Output("top_sector_store", "data"),
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

        if initiator_country == "All countries":
            initiator_country = None
        if incident_type == "All":
            incident_type = None

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=receiver_country_filter,
            initiator_country=initiator_country,
            incident_type=incident_type,
            states_codes=states_codes
        )

        print(filtered_df.head(10))

        if filtered_df.empty:
            fig = empty_figure(height_value=500)
            return fig, {}

        else:

            values_data = filtered_df.groupby(["receiver_category"])["ID"].nunique().reset_index()
            grouped_data = filtered_df.groupby(["receiver_category", "receiver_category_subcode"])["ID"].nunique().reset_index()
            grouped_data = grouped_data.sort_values(by="receiver_category", ascending=True).reset_index(drop=True)

            idx = grouped_data["ID"].idxmax()
            top_sector = grouped_data.loc[idx, "receiver_category"]

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
                                    "End user(s) / specially protected groups": "#335660",
                                    "International / supranational organization": "#99abaf",
                                    "Unknown": "#668088",
                                    "Other": "#ccd5d7",
                                    "Education": "#e6eaeb",
                                    },
            )
            sectors_plot.update_traces(
                hovertemplate='<b>%{label}</b>'
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

        return sectors_plot, top_sector


def sectors_text_selection_callback(app):
    @app.callback(
        Output("sectors_selected", "children"),
        Input("sectors_graph", "clickData"),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('initiator_country_dd', 'value'),
        Input('receiver_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
    )
    def display_click_data(
            clickData, start_date, end_date, initiator_country_dd, receiver_country_dd, incident_type_dd
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] in {
            'date-picker-range.start_date',
            'date-picker-range.end_date',
            'initiator_country_dd.value',
            'receiver_country_dd.value',
            'incident_type_dd.value',
        }:
            clickData = None

        if clickData:
            text = html.P([
                'Selected sector: ',
                html.Span(f'{clickData["points"][0]["label"]}', style={'font-weight': 'bold'})
            ])
            return text

        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                ),
                ' Click on the pie sections to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})
            return text


def sectors_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='sectors_datatable', component_property='data'),
        Output(component_id='sectors_datatable', component_property='tooltip_data'),
        Output(component_id="modal_sectors", component_property='is_open'),
        Output(component_id="modal_sectors_content", component_property='children'),
        Output(component_id="nb_incidents_sectors", component_property='children'),
        Output(component_id="average_intensity_sectors", component_property='children'),
        Output(component_id="sectors_description_text", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="sectors_graph", component_property="clickData"),
        Input(component_id="sectors_datatable", component_property='derived_virtual_data'),
        Input(component_id="sectors_datatable", component_property='active_cell'),
        Input(component_id="sectors_datatable", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        Input(component_id="top_sector_store", component_property="data"),
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
                     metric_values,
                     top_sector,
                     is_open):

        if initiator_country_filter == "All countries":
            initiator_country_filter = None
        if incident_type_filter == "All":
            incident_type_filter = None

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

        copied_df = df.copy()

        if filtered_data.empty:
            text = html.P(["No cyber incidents corresponding to the selected criteria."])
            nb_incidents = 0
            average_intensity = 0

        elif graph_targets:
            nb_incidents = len(filtered_data)
            total_incidents = metric_values["nb_incidents"]
            average_intensity = round(pd.to_numeric(filtered_data["weighted_cyber_intensity"]).mean(), 2)
            sector_value = len(filtered_data[filtered_data['receiver_category'].str.contains(graph_targets['points'][0]['label'], regex=False)])
            parent_sector_value = len(copied_df[copied_df['receiver_category'].fillna("").str.contains(graph_targets['points'][0]['parent'], regex=False)])

            if graph_targets["points"][0]["currentPath"] == "/":
                text = html.P([
                    "For your selected filters, ",
                    html.Span(f"{round((sector_value/total_incidents)*100, 2)}", style={'font-weight': 'bold'}),
                    "% (",
                    html.Span(f"{sector_value}", style={'font-weight': 'bold'}),
                    f") of all incidents targeted the ",
                    html.Span(f"{graph_targets['points'][0]['label'].lower()}", style={'font-weight': 'bold'}),
                    " sector."
                ])
            else:
                text = html.P([
                    "For your selected filters, ",
                    html.Span(f"{round((nb_incidents/total_incidents)*100, 2)}", style={'font-weight': 'bold'}),
                    "% (",
                    html.Span(f"{nb_incidents}", style={'font-weight': 'bold'}),
                    f") of all incidents targeted the ",
                    html.Span(f"{graph_targets['points'][0]['label'].lower()}", style={'font-weight': 'bold'}),
                    " sector. This represents ",
                    html.Span(f"{round((nb_incidents/parent_sector_value)*100, 1)}", style={'font-weight': 'bold'}),
                    f"% of all incidents targeting {graph_targets['points'][0]['parent'].lower()}.",
                ])

        else:
            nb_incidents = metric_values["nb_incidents"]
            average_intensity = metric_values["average_intensity"]
            top_sector_value = len(filtered_data[filtered_data['receiver_category'].str.contains(top_sector, regex=False)])
            text = html.P([
                "For your selected filters, ",
                html.Span(f'{top_sector.lower()}', style={'font-weight': 'bold'}),
                " was the most commonly targeted sector, representing ",
                html.Span(f'{round((top_sector_value/nb_incidents)*100, 2)}', style={'font-weight': 'bold'}),
                "% (",
                html.Span(f'{top_sector_value}', style={'font-weight': 'bold'}),
                ") of all incidents."
            ])

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

        return data, tooltip_data, status, modal, nb_incidents, average_intensity, text
