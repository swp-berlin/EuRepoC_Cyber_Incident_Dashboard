from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output


def timeline_title_callback(app):
    @app.callback(
        Output("timeline_text", "children"),
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
            return html.P(html.B(f"Number of cyber incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of cyber incidents across all countries between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Number of cyber incidents initiated by actors based in {initiator_country} between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Number of cyber incidents against {receiver_country} between {start_date} and {end_date}"))


def timeline_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('timeline_graph', 'figure'),
        Output('timeline_description_text', 'children'),
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

        date_range = pd.date_range(start=start_date_start, end=start_date_end)

        if len(date_range) > 2 * 365:

            evolution_grouped = filtered_df.groupby(["year"]).agg({'ID': 'nunique'}).reset_index()
            evolution_grouped = evolution_grouped.rename(columns={"ID": "Number of incidents"})

            if evolution_grouped.empty is False:
                evolution_grouped['pct_change'] = evolution_grouped['Number of incidents'].pct_change()
                min_year = evolution_grouped['year'].min()
                max_year = evolution_grouped['year'].max()

                start_year = evolution_grouped.query(f"year == {min_year}")["Number of incidents"].values[0]
                end_year = evolution_grouped.query(f"year == {max_year}")["Number of incidents"].values[0]
                avg_pct_change = round(evolution_grouped['pct_change'].mean() * 100, 0)
                change = "increased" if end_year > start_year else "decreased" if end_year < start_year else "remained constant" if end_year == start_year else None
                sentence_2 = f" over selected period - going from {start_year} incidents in {int(min_year)} to {end_year} incidents in {int(max_year)}. There has been " if end_year > start_year or end_year < start_year else " over the selected period." if end_year == start_year else None
                change_2 = "an increase" if avg_pct_change > 0 else "a decrease"
                sentence_3 = f'{change_2} by {avg_pct_change}% on average per year' if avg_pct_change > 0 or avg_pct_change < 0 else ""
                sentence_4 = f" since {int(min_year)}." if avg_pct_change > 0 or avg_pct_change < 0 else ""

                timeline_description_text = html.Div([
                    html.P([
                        f"The number of cyber incidents has ",
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
                    x=evolution_grouped["year"],
                    y=evolution_grouped["Number of incidents"],
                    mode='lines+markers',
                    line=dict(color='#002C38'),
                    name='Number of cyber incidents',
                ),
            )

            overall_evolution_plot.update_layout(
                showlegend=False,
                plot_bgcolor='rgba (0, 44, 56, 0.05)',
                yaxis=dict(range=[0, None]),
                xaxis=dict(tickformat='%Y', dtick=1),
                font=dict(
                    family="sans-serif",
                    color="#002C38",
                ),
                margin=dict(l=0, r=0, t=25, b=0, pad=0),
                height=400,
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

                start_month = evolution_grouped.query(f"date == '{min_month.strftime('%Y-%m-%d')}'")["Number of incidents"].values[0]
                end_month = evolution_grouped.query(f"date == '{max_month.strftime('%Y-%m-%d')}'")["Number of incidents"].values[0]
                avg_pct_change = round(evolution_grouped['pct_change'].mean() * 100, 0)
                change = "increased" if end_month > start_month else "decreased" if end_month < start_month else "remained constant" if end_month == start_month else None
                sentence_2 = f" over selected period - going from {start_month} incidents in {min_month.strftime('%B %Y')} to {end_month} incidents in {max_month.strftime('%B %Y')}. There has been " if end_month > start_month or end_month < start_month else " over the selected period." if end_month == start_month else ""
                change_2 = "an increase" if avg_pct_change > 0 else "a decrease"
                sentence_3 = f'{change_2} by {avg_pct_change}% on average per month' if avg_pct_change > 0 or avg_pct_change < 0 else ""
                sentence_4 = f" since {min_month.strftime('%B %Y')}." if avg_pct_change > 0 or avg_pct_change < 0 else ""

                timeline_description_text = html.Div([
                    html.P([
                        f"The number of cyber incidents has ",
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
                    name='Number of cyber incidents',
                ),
            )

            overall_evolution_plot.update_layout(
                showlegend=False,
                plot_bgcolor='rgba (0, 44, 56, 0.05)',
                yaxis=dict(range=[0, None]),
                xaxis=dict(tickformat='%b-%Y', dtick="M1"),
                font=dict(
                    family="sans-serif",
                    color="#002C38",
                ),
                margin=dict(l=0, r=0, t=25, b=0, pad=0),
                height=400,
            )

        return overall_evolution_plot, timeline_description_text


def timeline_datatable_callback(app, df=None, states_codes=None):
    @app.callback(
        Output(component_id='timeline_datatable', component_property='data'),
        Output(component_id='timeline_datatable', component_property='tooltip_data'),
        Output("timeline_datatable_store", "data"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input("timeline_graph", "clickData")
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     start_date_start,
                     start_date_end,
                     clickData):

        # Check if start and end dates have changed and reset clickdata
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

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

        # Filter data based on inputs
        filtered_data = df.copy(deep=True)
        if receiver_country_filter and receiver_country_filter != 'Global (states)':
            filtered_data = filtered_data[filtered_data['receiver_country'].str.contains(receiver_country_filter)]
        if region_filter:
            filtered_data = filtered_data[filtered_data['receiver_region'].str.contains(region_filter, regex=True)]
        if initiator_country_filter:
            filtered_data = filtered_data[filtered_data['initiator_country'].str.contains(initiator_country_filter)]
        start_date = pd.to_datetime(start_date_start).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(start_date_end).strftime('%Y-%m-%d')
        filtered_data = filtered_data[
            (filtered_data['start_date'] >= start_date) & (filtered_data['start_date'] <= end_date)]

        # Update data further based on clickData
        if clickData:
            point = clickData["points"][0]["x"]
            if isinstance(point, int):
                first_day = pd.to_datetime(str(point))
                last_day = first_day + pd.offsets.YearEnd(0)
                first_day = first_day.strftime('%Y-%m-%d')
                last_day = last_day.strftime('%Y-%m-%d')
            else:
                first_day = pd.to_datetime(str(point))
                last_day = first_day + pd.offsets.MonthEnd(0)
                first_day = pd.to_datetime(first_day).strftime('%Y-%m-%d')
                last_day = pd.to_datetime(last_day).strftime('%Y-%m-%d')

            filtered_data = filtered_data[
                (filtered_data['start_date'] >= first_day) & (filtered_data['start_date'] <= last_day)]

            text = html.P(f'Currently selected: {point}')

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['name', 'start_date', "incident_type"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                        for row in data]

        return data, tooltip_data, filtered_data.to_dict('records')


def timeline_text_selection_callback(app):
    @app.callback(
        Output(component_id='timeline_selected', component_property='children'),
        Input(component_id="timeline_graph", component_property="clickData"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date')
    )
    def update_table(clickData,
                     receiver_country_filter,
                     initiator_country_filter,
                     start_date_start,
                     start_date_end):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.P([
                'Current graph selection: incidents in ',
                html.Span(f'{clickData["points"][0]["x"]}',
                          style={'font-weight': 'bold'})
            ])
        else:
            text = html.P(f'No graph data point selected', style={'font-style': 'italic'})

        return text
