from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text


def attributions_graph_callback_types(app, df=None, states_codes=None):
    @app.callback(
        Output('attributions_graph_types', 'figure'),
        Output('attributions_description_text_types', 'children'),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input("attributions_graph_types", "clickData"),
    )
    def update_timeline(input_receiver_country,
                        input_initiator_country,
                        incident_type,
                        start_date_start,
                        start_date_end,
                        clickData):

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
            fig = empty_figure(height_value=450)
            attributions_description_text = html.P("There are no incidents matching the selected filters.")

        else:
            total_attributions = filtered_df["attribution_ID"].nunique()
            grouped_df = filtered_df.groupby(['attribution_basis_clean']).agg(
                nb_attributions=('attribution_ID', 'nunique'),
            ).reset_index().sort_values(by='nb_attributions', ascending=True)
            grouped_df['percentage'] = (grouped_df['nb_attributions'] / total_attributions * 100).round(2)
            grouped_df['text'] = grouped_df.apply(lambda row: f"{row['nb_attributions']} ({row['percentage']}%)",
                                                  axis=1)

            if clickData:
                selected_attribution_type = clickData["points"][0]["label"]

                colors = ['#002C38' if x != selected_attribution_type else '#cc0130' for x in grouped_df['attribution_basis_clean']]

                fig = go.Figure(data=[go.Bar(
                    y=grouped_df['attribution_basis_clean'],
                    x=grouped_df['nb_attributions'],
                    text=grouped_df['text'],
                    orientation='h',
                    marker=dict(
                        color=colors,
                    ),
                    hovertemplate='%{x} attributions<extra></extra>'
                )])

                fig.update_layout(
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
                    height=450,
                    dragmode=False
                )

            else:
                fig = go.Figure(data=[go.Bar(
                    y=grouped_df['attribution_basis_clean'],
                    x=grouped_df['nb_attributions'],
                    text=grouped_df['text'],
                    orientation='h',
                    marker=dict(
                        color="#002C38",
                    ),
                    hovertemplate='%{x} attributions<extra></extra>'
                )])

                fig.update_layout(
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
                    height=450,
                    dragmode=False
                )

            if grouped_df.iloc[-1]['attribution_basis_clean'] == "Attacker confirms":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by the ",
                    html.Span("attacker themselves",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            elif grouped_df.iloc[-1]['attribution_basis_clean'] == "Industry attribution":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by the ",
                    html.Span("IT-security community",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            elif grouped_df.iloc[-1]['attribution_basis_clean'] == "Political attribution":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by the ",
                    html.Span("the receiver government(s)/state entity(ies) or international organisations",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            elif grouped_df.iloc[-1]['attribution_basis_clean'] == "Attribution by third-party":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by ",
                    html.Span("third-parties",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            elif grouped_df.iloc[-1]['attribution_basis_clean'] == "Receiver attributes attacker":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by ",
                    html.Span("receiver organisation",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            elif grouped_df.iloc[-1]['attribution_basis_clean'] == "Media-based attribution":
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by ",
                    html.Span("the media",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])
            else:
                attributions_description_text = html.P([
                    f"For the incidents that meet your filter selection, the majority of attributions ({grouped_df.iloc[-1]['percentage']}%) were by ",
                    html.Span("other entities",
                              style={'font-weight': 'bold'}),
                    ". Note that one incident can have multiple attributions."
                ])

        return fig, attributions_description_text


def attributions_datatable_callback_types(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='attributions_datatable_types', component_property='data'),
        Output(component_id='attributions_datatable_types', component_property='tooltip_data'),
        Output(component_id="modal_attributions_types", component_property='is_open'),
        Output(component_id="modal_attributions_content_types", component_property='children'),
        Output(component_id="nb_incidents_attributions_types", component_property='children'),
        Output(component_id="average_intensity_attributions_types", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id="incident_type_dd", component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="attributions_graph_types", component_property="clickData"),
        Input(component_id="attributions_datatable_types", component_property='derived_virtual_data'),
        Input(component_id="attributions_datatable_types", component_property='active_cell'),
        Input(component_id="attributions_datatable_types", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_attributions_types", component_property="is_open"),
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
                     metric_values,
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

        if clickData is None:
            filtered_data = filtered_data
            nb_incidents = metric_values["nb_incidents"]
            average_intensity = metric_values["average_intensity"]
        else:
            point = clickData["points"][0]["label"]
            if point == "Industry attribution":
                point = "IT-security community attributes attacker"
            if point == "Political attribution":
                point = r"Attribution by receiver government / state entity|Attribution by EU institution/agency|Attribution by international organization"

            filtered_data = filtered_data[filtered_data["attribution_basis"].str.contains(point)]

            nb_incidents = len(filtered_data)
            average_intensity = round(pd.to_numeric(filtered_data["weighted_cyber_intensity"]).mean(), 2)

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime('%Y-%m-%d')

        # Convert data to pandas DataFrame and format tooltip_data
        data = filtered_data[['ID', 'name', 'start_date', "number_of_attributions"]].to_dict('records')
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


def attributions_text_selection_callback_types(app):
    @app.callback(
        Output(component_id='attributions_selected_types', component_property='children'),
        Input(component_id="attributions_graph_types", component_property="clickData"),
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

        if clickData:
            selected = clickData["points"][0]["label"]

            text = html.P([
                'Current graph selection: ',
                html.Span(f'{selected}',
                            style={'font-weight': 'bold'}),
            ])
        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                ),
                ' Click on a point in the graph to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})

        return text
