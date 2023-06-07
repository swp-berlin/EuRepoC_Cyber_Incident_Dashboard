from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from dash import callback_context as ctx
from dateutil.relativedelta import relativedelta
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text



def calculate_cagr(start_value, end_value, periods):
    if periods and periods != 0:
        return (end_value / start_value) ** (1/periods) - 1
    else:
        return 0


cagr_popover = dbc.Popover(
    "The Compound Annual Growth Rate (CAGR) is a metric that provides the mean annual growth rate of cyber incidents \
    over a specified period of time. It's calculated under the assumption that the incidents increase at a steady rate \
    every year, which offers a smooth and single-figure snapshot of growth that might actually be volatile from year \
    to year. Essentially, it helps understand the average yearly rate at which cyber incidents have increased.",
    target="cagr_info",
    body=True,
    trigger="hover",
)

def timeline_title_callback(app):
    @app.callback(
        Output("timeline_text", "children"),
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
            inc_type = incident_type
        else:
            inc_type = "cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(html.B(f"Number of {inc_type.lower()} incidents from {initiator_country} against {receiver_country} \
            between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of {inc_type.lower()} incidents across all countries between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Number of {inc_type.lower()} incidents initiated by actors based in {initiator_country} \
            between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of {inc_type.lower()} incidents against {receiver_country} \
            between {start_date} and {end_date}"))


def timeline_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('timeline_graph', 'figure'),
        Output('timeline_description_text', 'children'),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        incident_type,
                        start_date_start,
                        start_date_end):

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

        date_range = pd.date_range(start=start_date_start, end=start_date_end)

        if filtered_df.empty:
            overall_evolution_plot = empty_figure(height_value=450)
            timeline_description_text = html.P("There are no incidents matching the selected filters.")

        else:
            if len(date_range) > 2 * 365:

                evolution_grouped = filtered_df.groupby(["year"]).agg({'ID': 'nunique'}).reset_index()
                evolution_grouped = evolution_grouped.rename(columns={"ID": "Number of incidents"})

                if evolution_grouped.empty is False:
                    min_year = evolution_grouped['year'].min()
                    max_year = evolution_grouped['year'].max()
                    periods = max_year - min_year

                    start_year = evolution_grouped.query(f"year == {min_year}")["Number of incidents"].values[0]
                    end_year = evolution_grouped.query(f"year == {max_year}")["Number of incidents"].values[0]

                    cagr = calculate_cagr(start_year, end_year, periods)

                    change = "increased" if end_year > start_year else "decreased" if end_year < start_year else \
                        "remained constant" if end_year == start_year else None

                    sentence_2 = f" - going from {start_year} incidents \
                    in {int(min_year)} to {end_year} incidents in {int(max_year)}. \
                    This " if end_year > start_year or end_year < start_year else " overall." \
                        if end_year == start_year else None
                    change_2 = "increase represents a Compound Annual Growth Rate (CAGR)" if cagr > 0 else "decrease represents a Compound Annual Growth Rate (CAGR)"
                    sentence_3 = f'{change_2} ' if cagr > 0 or cagr < 0 else ""
                    sentence_4 = f' of {round(cagr*100, 1)}% ' if cagr > 0 or cagr < 0 else ""
                    sentence_5 = f" since {int(min_year)}." if cagr > 0 or cagr < 0 else ""

                    timeline_description_text = html.Div([
                        html.P([
                            f"For the selected filters, the number of cyber incidents has ",
                            html.Span(f"{change}", style={'font-weight': 'bold'}),
                            html.Span(f"{sentence_2}"),
                            html.Span(f'{sentence_3}', style={'font-weight': 'bold'}),
                            html.Span(
                                html.I(
                                    id="cagr_info",
                                    className="fa-regular fa-circle-question",
                                    style={'text-align': 'center', 'font-size': '12px', 'color': '#002C38'})
                                if cagr > 0 or cagr < 0 else ""
                            ),
                            html.Span(f'{sentence_4}'),
                            html.Span(f'{sentence_5}'),
                        ]),
                        cagr_popover
                    ])
                else:
                    timeline_description_text = html.Div([
                        html.P([
                            f"There are no cyber incidents in the selected period."
                        ]),
                    ])

                overall_evolution_plot = go.Figure()
                overall_evolution_plot.add_trace(
                    go.Scatter(
                        x=evolution_grouped["year"],
                        y=evolution_grouped["Number of incidents"],
                        mode='lines+markers',
                        line=dict(color='#002C38'),
                        marker=dict(color="#002C38"),
                        name='Number of cyber incidents',
                    ),
                )

                overall_evolution_plot.update_layout(
                    showlegend=False,
                    plot_bgcolor='white',
                    yaxis=dict(
                        rangemode='tozero',
                        range=[0, None],
                        gridcolor='rgba(0, 0, 0, 0.1)',
                        zerolinecolor='rgba(0, 44, 56, 0.5)',
                        zerolinewidth=0.5,
                    ),
                    xaxis=dict(
                        type='date',
                        tickformat='%Y',
                        gridcolor='rgba(0, 0, 0, 0.1)',
                    ),
                    font=dict(
                        family="Lato",
                        size=14,
                        color="#002C38",
                    ),
                    margin=dict(l=0, r=0, t=25, b=0, pad=0),
                    height=400,
                    dragmode=False
                )
            else:

                evolution_grouped = filtered_df.groupby(["year", "month"]).agg({'ID': 'nunique'}).reset_index()
                evolution_grouped = evolution_grouped.rename(columns={"ID": "Number of incidents"})
                evolution_grouped["date"] = evolution_grouped["year"].astype(str) + "-" + evolution_grouped["month"].astype(str).str.zfill(2)
                evolution_grouped["date"] = pd.to_datetime(evolution_grouped["date"], format="%Y.0-%m.0")

                if evolution_grouped.empty is False:
                    evolution_grouped['pct_change'] = evolution_grouped['Number of incidents'].pct_change()
                    min_month = pd.to_datetime(evolution_grouped['date'].min())
                    max_month = pd.to_datetime(evolution_grouped['date'].max(), format="%Y.0-%m.0")
                    periods = max_month - min_month
                    periods_months = int(periods.days / 30)

                    start_month = evolution_grouped.query(f"date == '{min_month.strftime('%Y-%m-%d')}'")["Number of incidents"].values[0]
                    end_month = evolution_grouped.query(f"date == '{max_month.strftime('%Y-%m-%d')}'")["Number of incidents"].values[0]

                    cagr = calculate_cagr(start_month, end_month, periods_months)

                    change = "increased" if end_month > start_month else "decreased" if end_month < start_month else "remained constant" if end_month == start_month else None
                    sentence_2 = f" - going from {start_month} incidents in {min_month.strftime('%B %Y')} to {end_month} incidents in {max_month.strftime('%B %Y')}. This " if end_month > start_month or end_month < start_month else " overall." if end_month == start_month else ""
                    change_2 = "increase represents a Compound Monthly Growth Rate (CMGR)" if cagr > 0 else "decrease represents a Compound Monthly Growth Rate (CMGR)"
                    sentence_3 = f'{change_2} of {round(cagr*100,1)}%' if cagr > 0 or cagr < 0 else ""
                    sentence_4 = f" since {min_month.strftime('%B %Y')}." if cagr > 0 or cagr < 0 else ""

                    timeline_description_text = html.Div([
                        html.P([
                            f"For the selected filters, the number of cyber incidents has ",
                            html.Span(f"{change}", style={'font-weight': 'bold'}),
                            html.Span(f"{sentence_2}"),
                            html.Span(f'{sentence_3}', style={'font-weight': 'bold'}),
                            html.Span(f'{sentence_4}')
                        ]),
                    ])
                else:
                    timeline_description_text = html.Div([
                        html.P([
                            f"There are no cyber incidents in the selected period."
                        ]),
                    ])

                overall_evolution_plot = go.Figure()
                overall_evolution_plot.add_trace(
                    go.Scatter(
                        x=evolution_grouped["date"],
                        y=evolution_grouped["Number of incidents"],
                        mode='lines+markers',
                        line=dict(color='#002C38'),
                        marker=dict(color="#002C38"),
                        name='Number of cyber incidents',
                    ),
                )

                overall_evolution_plot.update_layout(
                    showlegend=False,
                    plot_bgcolor='white',
                    yaxis=dict(
                        rangemode='tozero',
                        range=[0, None],
                        gridcolor='rgba(0, 0, 0, 0.1)',
                        zerolinecolor='rgba(0, 44, 56, 0.5)',
                        zerolinewidth=0.5,
                    ),
                    xaxis=dict(
                        tickformat='%b-%Y',
                        dtick="M1",
                        gridcolor='rgba(0, 0, 0, 0.1)',
                    ),
                    font=dict(
                        family="Lato",
                        color="#002C38",
                        size=14,
                    ),
                    margin=dict(l=0, r=0, t=25, b=0, pad=0),
                    height=400,
                    dragmode=False
                )

        return overall_evolution_plot, timeline_description_text


def timeline_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='timeline_datatable', component_property='data'),
        Output(component_id='timeline_datatable', component_property='tooltip_data'),
        Output(component_id="modal_timeline", component_property='is_open'),
        Output(component_id="modal_timeline_content", component_property='children'),
        Output(component_id="nb_incidents_timeline", component_property='children'),
        Output(component_id="average_intensity_timeline", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="timeline_graph", component_property="clickData"),
        Input(component_id="timeline_datatable", component_property='derived_virtual_data'),
        Input(component_id="timeline_datatable", component_property='active_cell'),
        Input(component_id="timeline_datatable", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_timeline", component_property="is_open"),
    )
    def update_table(
            receiver_country_filter,
            initiator_country_filter,
            incident_type_filter,
            start_date_start,
            start_date_end,
            clickData,
            derived_virtual_data,
            active_cell,
            page_current,
            metric_values,
            is_open,
    ):

        if initiator_country_filter == "All countries":
            initiator_country_filter = None
        if incident_type_filter == "All":
            incident_type_filter = None

        # Filter data based on inputs
        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=initiator_country_filter,
            incident_type_filter=incident_type_filter,
            start_date=start_date_start,
            end_date=start_date_end,
            states_codes=states_codes)

        date_range = pd.date_range(start=start_date_start, end=start_date_end)

        if clickData is None:
            filtered_data = filtered_data
            nb_incidents = metric_values["nb_incidents"]
            average_intensity = metric_values["average_intensity"]
        else:
            point = clickData["points"][0]["x"]
            first_day = pd.to_datetime(str(point))
            if len(date_range) > 2 * 365:
                last_day = first_day + relativedelta(day=31, month=12)
            else:
                last_day = first_day + relativedelta(day=31)

            first_day = first_day.strftime('%Y-%m-%d')
            last_day = last_day.strftime('%Y-%m-%d')

            filtered_data = filtered_data.query('start_date >= @first_day and start_date <= @last_day')

            nb_incidents = len(filtered_data)
            average_intensity = round(pd.to_numeric(filtered_data["weighted_cyber_intensity"]).mean(), 2)

        filtered_data.loc[:, "start_date"] = filtered_data["start_date"].dt.strftime('%Y-%m-%d')

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

        return data, tooltip_data, status, modal, nb_incidents, average_intensity


def timeline_text_selection_callback(app):
    @app.callback(
        Output(component_id='timeline_selected', component_property='children'),
        Input(component_id="timeline_graph", component_property="clickData"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date')
    )
    def update_table(clickData,
                     receiver_country_filter,
                     initiator_country_filter,
                     incident_type_filter,
                     start_date_start,
                     start_date_end):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'incident_type_dd.value':
            clickData = None

        # Filter data based on inputs
        if clickData:
            date_range = pd.date_range(start=start_date_start, end=start_date_end)
            if len(date_range) > 2 * 365:
                selected = datetime.strptime(clickData["points"][0]["x"], "%Y-%m-%d").strftime("%Y")
            else:
                selected = datetime.strptime(clickData["points"][0]["x"], "%Y-%m-%d").strftime("%b-%Y")

            text = html.P([
                'Current graph selection: incidents in ',
                html.Span(f'{selected}',
                          style={'font-weight': 'bold'})
            ])
        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '12px', 'color': '#cc0130'},
                ),
                ' Click on a point in the graph to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})

        return text
