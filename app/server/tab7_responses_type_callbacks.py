from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text



def responses_graph_callback_types(app, data=None, states_codes=None):
    @app.callback(
        Output('responses_graph_types', 'figure'),
        Output('responses_graph_2_types', 'figure'),
        Output('responses_description_text_types', 'children'),
        Output(component_id="nb_incidents_responses_types", component_property='children'),
        Output(component_id="average_intensity_responses_types", component_property='children'),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('metric_values', 'data'),
    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        incident_type,
                        start_date_start,
                        start_date_end,
                        metric_values):

        if input_initiator_country == "All countries":
            input_initiator_country = None
        if incident_type == "All":
            incident_type = None

        filtered_df = filter_database_by_output(
            df=data,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=input_receiver_country,
            initiator_country=input_initiator_country,
            incident_type=incident_type,
            states_codes=states_codes
        )

        filtered_df["country_type_response"].replace("State Actors", "Non-EU states", inplace=True)

        filtered_df_pol = filtered_df[filtered_df["political_response"]==1]
        filtered_df_leg = filtered_df[filtered_df["legal_response"]==1]


        if filtered_df_pol.empty and filtered_df_leg.empty:
            responses_plot = empty_figure(height_value=300)
            responses_plot_2 = empty_figure(height_value=300)
            responses_description_text = html.P("There are no incidents matching the selected filters.")

            nb_incidents = 0
            average_intensity = 0

        elif not filtered_df_pol.empty and filtered_df_leg.empty:
            responses_plot_2 = empty_figure(height_value=300)

            nb_incidents = filtered_df_pol.ID.nunique()
            average_intensity = 0

            filtered_df_pol_group = filtered_df_pol.groupby(['country_type_response', 'response_type']).agg(
                count=('ID', 'nunique')
            ).reset_index()

            total_pol_types = filtered_df_pol_group.groupby('response_type')['count'].sum().reset_index()
            total_pol_types = total_pol_types.rename(columns={'count': 'total'})
            filtered_df_pol_group = filtered_df_pol_group.merge(total_pol_types, on='response_type')
            filtered_df_pol_group = filtered_df_pol_group.sort_values(by='total', ascending=True).reset_index(drop=True)

            colors = {'Non-EU states': '#002C38', 'EU member states': '#cc0130', 'EU': '#89bd9e',
                      'International organizations': '#ccd5d7'}

            responses_plot = go.Figure()

            for country_type in filtered_df_pol_group['country_type_response'].unique():
                df = filtered_df_pol_group[filtered_df_pol_group['country_type_response'] == country_type]
                responses_plot.add_trace(
                    go.Bar(
                        y=df['response_type'],
                        x=df['count'],
                        name=country_type,
                        orientation='h',
                        marker_color=colors[country_type],
                        text=df['count'],
                        hovertemplate="%{text} %{y} from %{name}<extra></extra>"
                    )
                )
            responses_plot.update_layout(
                title="<b>Types of political responses</b>",
                title_font_size=14,
                barmode='stack',
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
                height=300,
                dragmode=False
            )

            responses_description_text = html.P([
                html.Span("For your selection, most political responses are "),
                html.Span(f"{filtered_df_pol_group.iloc[-1]['response_type'].lower()} ({filtered_df_pol_group.iloc[-1]['total']})", style={"font-weight": "bold"}),
                ". There are no legal responses. Note that one incident can have multiple responses."])

        elif filtered_df_pol.empty and not filtered_df_leg.empty:
            responses_plot = empty_figure(height_value=300)

            nb_incidents = 0
            average_intensity = filtered_df_leg.ID.nunique()

            filtered_df_leg_group = filtered_df_leg.groupby(['legal_response_type_clean']).agg(
                count=('ID', 'nunique')
            ).reset_index().sort_values(by='count', ascending=True).reset_index(drop=True)

            responses_plot_2 = go.Figure(data=[go.Bar(
                    y=filtered_df_leg_group['legal_response_type_clean'],
                    x=filtered_df_leg_group['count'],
                    orientation='h',
                    marker=dict(
                        color='#002C38',
                    ),
                    hoverinfo='none',
                    text=filtered_df_leg_group['count'],
                )])
            responses_plot_2.update_layout(
                    title="<b>Types of legal responses</b>",
                    title_font_size=14,
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
                    height=300,
                    dragmode=False
                )

            responses_description_text = html.P([
                html.Span("For your selection, most legal responses are "),
                html.Span(
                    f"{filtered_df_leg_group.iloc[-1]['legal_response_type_clean'].lower()} ({filtered_df_leg_group.iloc[-1]['count']})",
                    style={"font-weight": "bold"}),
                ". There are no political responses. Note that one incident can have multiple responses."])


        else:
            filtered_df_pol_group = filtered_df_pol.groupby(['country_type_response', 'response_type']).agg(
                count=('ID', 'nunique')
            ).reset_index()

            total_pol_types = filtered_df_pol_group.groupby('response_type')['count'].sum().reset_index()
            total_pol_types = total_pol_types.rename(columns={'count': 'total'})
            filtered_df_pol_group = filtered_df_pol_group.merge(total_pol_types, on='response_type')
            filtered_df_pol_group = filtered_df_pol_group.sort_values(by='total', ascending=True).reset_index(drop=True)

            colors = {'Non-EU states': '#002C38', 'EU member states': '#cc0130', 'EU': '#89bd9e',
                      'International organizations': '#ccd5d7'}
            responses_plot = go.Figure()

            for country_type in filtered_df_pol_group['country_type_response'].unique():
                df = filtered_df_pol_group[filtered_df_pol_group['country_type_response'] == country_type]
                responses_plot.add_trace(
                    go.Bar(
                        y=df['response_type'],
                        x=df['count'],
                        name=country_type,
                        orientation='h',
                        marker_color=colors[country_type],
                        text=df['count'],
                        customdata=df['country_type_response'],
                        hovertemplate="%{text} %{y} from %{customdata}<extra></extra>"
                    )
                )

            responses_plot.update_layout(
                title="<b>Types of political responses</b>",
                title_font_size=14,
                barmode='stack',
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
                height=300,
                dragmode=False
            )

            filtered_df_leg_group = filtered_df_leg.groupby(['legal_response_type_clean']).agg(
                count=('ID', 'nunique')
            ).reset_index().sort_values(by='count', ascending=True).reset_index(drop=True)

            responses_plot_2 = go.Figure(data=[go.Bar(
                y=filtered_df_leg_group['legal_response_type_clean'],
                x=filtered_df_leg_group['count'],
                orientation='h',
                marker=dict(
                    color='#002C38',
                ),
                hoverinfo='none',
                text=filtered_df_leg_group['count'],
            )])
            responses_plot_2.update_layout(
                title="<b>Types of legal responses</b>",
                title_font_size=14,
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
                height=300,
                dragmode=False
            )

            responses_description_text = html.P([
                html.Span("For your selection, most political responses were "),
                html.Span(
                    f"{filtered_df_pol_group.iloc[-1]['response_type'].lower()} ({filtered_df_pol_group.iloc[-1]['total']})",
                    style={"font-weight": "bold"}),
                ". Most legal responses were ",
                html.Span(f"{filtered_df_leg_group.iloc[-1]['legal_response_type_clean'].lower()} ({filtered_df_leg_group.iloc[-1]['count']})", style={"font-weight": "bold"}),
                ". Note that one incident can have multiple responses."
            ])

            nb_incidents = filtered_df_pol.ID.nunique()
            average_intensity = filtered_df_leg.ID.nunique()


        return responses_plot, \
            responses_plot_2, \
            responses_description_text, \
            nb_incidents, average_intensity


def responses_datatable_callback_types(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='responses_datatable_types', component_property='data'),
        Output(component_id='responses_datatable_types', component_property='tooltip_data'),
        Output(component_id="modal_responses_types", component_property='is_open'),
        Output(component_id="modal_responses_content_types", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id="incident_type_dd", component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="responses_datatable_types", component_property='derived_virtual_data'),
        Input(component_id="responses_datatable_types", component_property='active_cell'),
        Input(component_id="responses_datatable_types", component_property='page_current'),
        State(component_id="modal_responses_types", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     initiator_country_filter,
                     incident_type_filter,
                     start_date_start,
                     start_date_end,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     is_open):

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

        filtered_data["number_of_political_responses"] = pd.to_numeric(filtered_data["number_of_political_responses"])
        filtered_data["number_of_legal_responses"] = pd.to_numeric(filtered_data["number_of_legal_responses"])

        filtered_data = filtered_data[
            (filtered_data["number_of_political_responses"] > 0) | (filtered_data["number_of_legal_responses"] > 0)]

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime('%Y-%m-%d')

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[[
            'ID', 'name', 'start_date', "number_of_political_responses", "number_of_legal_responses", "weighted_cyber_intensity"
        ]].to_dict('records')
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
