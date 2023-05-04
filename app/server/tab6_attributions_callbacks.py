from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable
from server.common_callbacks import create_modal_text


def attributions_title_callback(app):
    @app.callback(
        Output("attributions_text", "children"),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range_attributions', 'start_date'),
        Input('date-picker-range_attributions', 'end_date'),
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
            return html.P(html.B(f"Average number of months needed to attribute the initiators of {type} incidents from {initiator_country} against {receiver_country}  \
            between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Average number of months needed to attribute the initiators of {type} incidents between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"Average number of months needed to attribute initiators of {type} incidents based in {initiator_country} \
            between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"Average number of months needed to attribute initiators of {type} incidents against {receiver_country} \
            between {start_date} and {end_date}"))


def attributions_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('attributions_graph', 'figure'),
        Output('attributions_description_text', 'children'),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range_attributions', 'start_date'),
        Input('date-picker-range_attributions', 'end_date'),
    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        incident_type,
                        start_date_start,
                        start_date_end):

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

        if len(date_range) > 2 * 365:

            attributions_grouped = filtered_df.groupby(pd.Grouper(key='start_date', freq='Y')).agg({
                "date_difference_ind_months": "mean",
                "date_difference_pol_months": "mean",
                "date_difference_att_months": "mean",
                "date_difference_third_months": "mean",
                "date_difference_other_months": "mean",
                "average_overall": "mean"
            }).reset_index()

            attributions_grouped["year"] = attributions_grouped["start_date"].dt.year
            for col in attributions_grouped.columns:
                if col != "year" and col != "start_date":
                    attributions_grouped[col] = attributions_grouped[col].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)

            if attributions_grouped.empty:
                attributions_description_text = html.Div([
                    html.P([
                        f"There are no cyber incidents with valid data on the date of attribution with your selected options."
                    ]),
                ])
                overall_attributions_plot = go.Figure()
            elif attributions_grouped["average_overall"].isna().all():
                attributions_description_text = html.Div([
                    html.P([
                        f"There are no cyber incidents with valid data on the date of attribution with your selected options."
                    ]),
                ])
                overall_attributions_plot = go.Figure()
            else:
                first_non_null = attributions_grouped[attributions_grouped['average_overall'].notnull()].iloc[0]
                min_year = first_non_null['start_date'].year
                start_year = first_non_null['average_overall']

                last_non_null = attributions_grouped[attributions_grouped['average_overall'].notnull()].iloc[-1]
                max_year = last_non_null['start_date'].year
                end_year = last_non_null['average_overall']

                # loop through the values in attributions_grouped["average_overall"] in reverse order
                if start_year > end_year:
                    change = "decreased"
                elif start_year < end_year:
                    change = "increased"
                else:
                    change = "remained the same"


                attributions_description_text = html.Div([
                    html.P([
                        f"On average the time needed to attribute the initiators of cyber incidents has ",
                        html.Span(f"{change}", style={'font-weight': 'bold'}),
                        html.Span(f" for your selection. Going from {round(start_year, 1)} months in {min_year} to "),
                        html.Span(f'{round(end_year, 1)} months in {max_year}.'),
                    ]),
                ])

                overall_attributions_plot = go.Figure()
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_ind_months"],
                    x=attributions_grouped["year"],
                    marker=dict(color="#002C38"),
                    mode="markers+lines",
                    name="Industry attribution",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_pol_months"],
                    x=attributions_grouped["year"],
                    marker=dict(color="#cc0130"),
                    mode="markers+lines",
                    name="Political attribution",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_att_months"],
                    x=attributions_grouped["year"],
                    marker=dict(color="rgba(137,189,158, 0.7)"),
                    mode="markers+lines",
                    name="Attacker confirms",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_third_months"],
                    x=attributions_grouped["year"],
                    marker=dict(color="rgba(153,171,175, 0.5)"),
                    mode="markers+lines",
                    name="Attribution by third-party",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_other_months"],
                    x=attributions_grouped["year"],
                    marker=dict(color="rgba(204,213,215, 0.5)"),
                    mode="markers+lines",
                    line=dict(dash='dot'),
                    name="Other attribution basis",
                    connectgaps=True
                ))
                overall_attributions_plot.update_layout(
                    title="",
                    yaxis_title="Average number of months",
                    xaxis_title="Initial access year",
                    plot_bgcolor='white',
                    xaxis=dict(
                        tickformat='%Y',
                        showgrid=True,
                        gridcolor='rgba(0, 0, 0, 0.1)',
                    ),
                    yaxis=dict(
                        range=[0, None],
                        gridcolor='rgba(0, 0, 0, 0.1)',
                        zerolinecolor='rgba(0, 44, 56, 0.5)',
                        zerolinewidth=0.5,
                    ),
                    font=dict(
                        family="Lato",
                        size=14,
                        color="#002C38",
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.4,
                    ),
                    margin=dict(l=0, r=0, t=25, b=0, pad=0),
                    height=400,
                )
        else:
            attributions_grouped = filtered_df.groupby(pd.Grouper(key='start_date', freq='MS', closed='left')).agg({
                "date_difference_ind_months": "mean",
                "date_difference_pol_months": "mean",
                "date_difference_att_months": "mean",
                "date_difference_third_months": "mean",
                "date_difference_other_months": "mean",
                "average_overall": "mean"
            }).reset_index()

            for col in attributions_grouped.columns:
                if col != "date" and col != "start_date":
                    attributions_grouped[col] = attributions_grouped[col].apply(
                        lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)

            if attributions_grouped.empty:
                attributions_description_text = html.Div([
                    html.P([
                        f"There are no cyber incidents with valid data on the date of attribution with your selected options."
                    ]),
                ])
                overall_attributions_plot = go.Figure()
            elif attributions_grouped["average_overall"].isna().all():
                attributions_description_text = html.Div([
                    html.P([
                        f"There are no cyber incidents with valid data on the date of attribution with your selected options."
                    ]),
                ])
                overall_attributions_plot = go.Figure()
            else:
                first_non_null = attributions_grouped[attributions_grouped['average_overall'].notnull()].iloc[0]
                min_month = first_non_null['start_date']
                start_month = first_non_null['average_overall']

                last_non_null = attributions_grouped[attributions_grouped['average_overall'].notnull()].iloc[-1]
                max_month = last_non_null['start_date']
                end_month = last_non_null['average_overall']

                if start_month > end_month:
                    change = "decreased"
                elif start_month < end_month:
                    change = "increased"
                else:
                    change = "remained the same"

                attributions_description_text = html.Div([
                    html.P([
                        f"On average the time needed to attribute the initiators of cyber incidents has ",
                        html.Span(f"{change}", style={'font-weight': 'bold'}),
                        html.Span(f" for your selection. Going from {round(start_month, 1)} months in {min_month.strftime('%B %Y')} to "),
                        html.Span(f"{round(end_month, 1)} months in {max_month.strftime('%B %Y')}."),
                    ]),
                ])

                overall_attributions_plot = go.Figure()
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_ind_months"],
                    x=attributions_grouped["start_date"],
                    marker=dict(color="#002C38"),
                    mode="markers+lines",
                    name="Industry attribution",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_pol_months"],
                    x=attributions_grouped["start_date"],
                    marker=dict(color="#cc0130"),
                    mode="markers+lines",
                    name="Political attribution",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_att_months"],
                    x=attributions_grouped["start_date"],
                    marker=dict(color="rgba(137,189,158, 0.7)"),
                    mode="markers+lines",
                    name="Attacker confirms",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_third_months"],
                    x=attributions_grouped["start_date"],
                    marker=dict(color="rgba(153,171,175, 0.5)"),
                    mode="markers+lines",
                    name="Attribution by third-party",
                    connectgaps=True
                ))
                overall_attributions_plot.add_trace(go.Scatter(
                    y=attributions_grouped["date_difference_other_months"],
                    x=attributions_grouped["start_date"],
                    marker=dict(color="rgba(204,213,215, 0.5)"),
                    mode="markers+lines",
                    line=dict(dash='dot'),
                    name="Other attribution basis",
                    connectgaps=True
                ))
                overall_attributions_plot.update_layout(
                    title="",
                    yaxis_title="Average number of months",
                    xaxis_title="Initial access year",
                    plot_bgcolor='white',
                    xaxis=dict(
                        dtick="M1",
                        showgrid=True,
                        gridcolor='rgba(0, 0, 0, 0.1)',
                    ),
                    yaxis=dict(
                        rangemode='tozero',
                        range=[0, None],
                        gridcolor='rgba(0, 0, 0, 0.1)',
                        zerolinecolor='rgba(0, 44, 56, 0.5)',
                        zerolinewidth=0.5,
                    ),
                    font=dict(
                        family="Lato",
                        size=14,
                        color="#002C38",
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="auto",
                        y=1.02,
                        xanchor="auto",
                        x=1,
                    ),
                    margin=dict(l=0, r=0, t=25, b=0, pad=0),
                    height=400,
                )



        return overall_attributions_plot, attributions_description_text


def attributions_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='attributions_datatable', component_property='data'),
        Output(component_id='attributions_datatable', component_property='tooltip_data'),
        Output(component_id="modal_attributions", component_property='is_open'),
        Output(component_id="modal_attributions_content", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id="incident_type_dd", component_property='value'),
        Input(component_id='date-picker-range_attributions', component_property='start_date'),
        Input(component_id='date-picker-range_attributions', component_property='end_date'),
        Input(component_id="attributions_graph", component_property="clickData"),
        Input(component_id="attributions_datatable", component_property='derived_virtual_data'),
        Input(component_id="attributions_datatable", component_property='active_cell'),
        Input(component_id="attributions_datatable", component_property='page_current'),
        State(component_id="modal_attributions", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     incident_type_filter,
                     start_date_start,
                     start_date_end,
                     clickData,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     is_open):

        # Check if start and end dates have changed and reset clickdata
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range_attributions.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range_attributions.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'incident_type_dd.value':
            clickData = None

        # Filter data based on inputs
        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=initiator_country_filter,
            incident_type_filter=incident_type_filter,
            start_date=start_date_start,
            end_date=start_date_end,
            states_codes=states_codes)

        # Update data further based on clickData
        if clickData:
            point = clickData["points"][0]["x"]
            if isinstance(point, int):
                first_day = pd.to_datetime(str(point), format='%Y')
                last_day = first_day + pd.offsets.YearEnd(0)
                first_day = first_day.strftime('%Y-%m-%d')
                last_day = last_day.strftime('%Y-%m-%d')
            else:
                first_day = pd.to_datetime(str(point), format='%Y-%m-%d')
                last_day = first_day + pd.offsets.MonthEnd(0)
                first_day = pd.to_datetime(first_day).strftime('%Y-%m-%d')
                last_day = pd.to_datetime(last_day).strftime('%Y-%m-%d')

            filtered_data = filtered_data[
                (filtered_data['start_date'] >= first_day) & (filtered_data['start_date'] <= last_day)]

            attribution = int(clickData["points"][0]["curveNumber"])
            if attribution == 0:
                filtered_data = filtered_data[filtered_data["attribution_basis_clean"].str.contains(r"\bIndustry attribution\b")]
            elif attribution == 1:
                filtered_data = filtered_data[filtered_data["attribution_basis_clean"].str.contains(r"\bPolitical attribution\b")]
            elif attribution == 2:
                filtered_data = filtered_data[filtered_data["attribution_basis_clean"].str.contains(r"\bAttacker confirms\b")]
            elif attribution == 3:
                filtered_data = filtered_data[filtered_data["attribution_basis_clean"].str.contains(r"\bAttribution by third-party\b")]
            elif attribution == 4:
                filtered_data = filtered_data[filtered_data["attribution_basis_clean"].str.contains(r"\bOther attribution basis\b")]
            else:
                filtered_data = filtered_data

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['ID', 'name', 'start_date', "number_of_attributions"]].to_dict('records')
        tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                         for column, value in row.items()}
                        for row in data]

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


def attributions_text_selection_callback(app):
    @app.callback(
        Output(component_id='attributions_selected', component_property='children'),
        Input(component_id="attributions_graph", component_property="clickData"),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range_attributions', component_property='start_date'),
        Input(component_id='date-picker-range_attributions', component_property='end_date')
    )
    def update_table(clickData,
                     receiver_country_filter,
                     initiator_country_filter,
                     incident_type_filter,
                     start_date_start,
                     start_date_end):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'date-picker-range_attributions.start_date' \
                or ctx.triggered[0]['prop_id'] == 'date-picker-range_attributions.end_date' \
                or ctx.triggered[0]['prop_id'] == 'initiator_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value' \
                or ctx.triggered[0]['prop_id'] == 'incident_type_dd.value':
            clickData = None

        if clickData:

            date_range = pd.date_range(start=start_date_start, end=start_date_end)
            if len(date_range) > 2 * 365:
                selected = clickData["points"][0]["x"]
            else:
                selected = datetime.strptime(str(clickData["points"][0]["x"]), "%Y-%m-%d").strftime("%b-%Y")

            if clickData["points"][0]['curveNumber'] == 0:
                attr = 'industry attributions'
            elif clickData["points"][0]['curveNumber'] == 1:
                attr = 'political attributions'
            elif clickData["points"][0]['curveNumber'] == 2:
                attr = 'attributions by the attacker'
            elif clickData["points"][0]['curveNumber'] == 3:
                attr = 'attributions by third-parties'
            elif clickData["points"][0]['curveNumber'] == 4:
                attr = 'other attributions'

            text = html.P([
                'Current graph selection: ',
                html.Span(f'{attr}',
                          style={'font-weight': 'bold'}),
                ' in ',
                html.Span(f'{selected}',
                            style={'font-weight': 'bold'}),
            ])
        else:
            text = html.P(f'No graph data point selected', style={'font-style': 'italic'})

        return text
