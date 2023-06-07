from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.subplots as sp
import plotly.graph_objs as go
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text


## ajouter plusieurs options; pour varié le genre de choses qui peuvent être choisi 

def responses_title_callback(app):
    @app.callback(
        Output("responses_text", "children"),
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
            type = "Cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.P(html.B(f"{type.lower()} incidents from {initiator_country} against {receiver_country} with political or legal responses \
            between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.P(html.B(f"{type.lower()} incidents with political or legal responses between {start_date} and {end_date}"))
        elif receiver_country == "Global (states)" and initiator_country:
            return html.P(html.B(f"{type.lower()} incidents with political or legal responses from initiators based in {initiator_country} \
            between {start_date} and {end_date}"))
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.P(html.B(f"{type.lower()} incidents against {receiver_country} with political or legal responses \
            between {start_date} and {end_date}"))


def responses_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('responses_graph', 'figure'),
        Output('responses_graph_2', 'figure'),
        Output('responses_description_text', 'children'),
        Output('responses_donut_annotation', 'children'),
        Output('responses_scatter_annotation', 'children'),
        Output(component_id="nb_incidents_responses", component_property='children'),
        Output(component_id="average_intensity_responses", component_property='children'),
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
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=input_receiver_country,
            initiator_country=input_initiator_country,
            incident_type=incident_type,
            states_codes=states_codes
        )

        responses_grouped = filtered_df.groupby(['ID']).agg({
            "response": "sum",
            "political_response": "sum",
            "legal_response": "sum",
        }).reset_index()

        responses_grouped["response"] = responses_grouped["response"].apply(lambda x: 1 if x > 0 else 0)
        responses_grouped["political_response"] = responses_grouped["political_response"].apply(
            lambda x: 1 if x > 0 else 0)
        responses_grouped["legal_response"] = responses_grouped["legal_response"].apply(lambda x: 1 if x > 0 else 0)

        pie_data = {
            "total_responses": [
                responses_grouped.ID.nunique() - responses_grouped.response.sum(),
                responses_grouped.response.sum()
            ],
            "total_political_responses": [
                responses_grouped.ID.nunique() - responses_grouped.political_response.sum(),
                responses_grouped.political_response.sum()

            ],
            "total_legal_responses": [
                responses_grouped.ID.nunique() - responses_grouped.legal_response.sum(),
                responses_grouped.legal_response.sum()
            ],
            #"text_total": [
             #   "",
              #  f"<b>{round(responses_grouped.response.sum() / responses_grouped.ID.nunique() * 100, 2)}%</b>"
           # ],
            "text_political": [
                "",
                f"<b>{round(responses_grouped.political_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%</b>"
            ],
            "text_legal": [
                "",
                f"<b>{round(responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%</b>"
            ],
        }

        pie_df = pd.DataFrame(pie_data)

        filtered_df["weighted_cyber_intensity"] = pd.to_numeric(filtered_df["weighted_cyber_intensity"])

        responses_grouped_2 = filtered_df.groupby(['weighted_cyber_intensity']).agg({
            'ID': 'nunique',
            "response": "sum",
            "political_response": "sum",
            "legal_response": "sum",
        }).reset_index()

        responses_grouped_2["percent_all"] = responses_grouped_2["response"] / responses_grouped_2["ID"]
        responses_grouped_2["percent_political"] = responses_grouped_2["political_response"] / responses_grouped_2["ID"]
        responses_grouped_2["percent_legal"] = responses_grouped_2["legal_response"] / responses_grouped_2["ID"]

        min_size = 10
        max_size = 25
        normalized_size_pol = min_size + (responses_grouped_2['political_response'] - np.min(responses_grouped_2['political_response'])) * \
                          (max_size - min_size) / (np.max(responses_grouped_2['political_response']) - np.min(responses_grouped_2['political_response']))

        normalized_size_leg = min_size + (
                    responses_grouped_2['legal_response'] - np.min(responses_grouped_2['legal_response'])) * \
                              (max_size - min_size) / (np.max(responses_grouped_2['legal_response']) - np.min(
            responses_grouped_2['legal_response']))

        if all(normalized_size_pol.isna()):
            normalized_size_pol = 10
        if all(normalized_size_leg.isna()):
            normalized_size_leg = 10

        total_nb_responses = int(pie_df.loc[1, "total_responses"])

        if filtered_df.empty:
            responses_plot = empty_figure(height_value=300)
            responses_plot_2 = empty_figure(height_value=300)
            responses_description_text = html.P("There are no incidents matching the selected filters.")
            responses_donut_annotation = ""
            responses_scatter_annotation = html.I("")

        elif total_nb_responses == 0:

            responses_description_text = html.P("None of the incidents matching the selected filters have a political or legal response.")
            responses_donut_annotation = html.I("Note: one incident can have both legal and political responses")
            responses_scatter_annotation = html.I("")

            responses_plot = sp.make_subplots(rows=1, cols=2,
                                              specs=[[{'type': 'domain'}, {'type': 'domain'}]])

            #colors_all = ['#e6eaeb', '#002C38']  ['#e6eaeb', '#89bd9e']
            colors_pol = ['#e6eaeb', '#002C38']
            colors_leg = ['#e6eaeb', '#cc0130']
            #responses_plot.add_trace(go.Pie(
             #   labels=['Incidents <b>without</b> response', 'Incidents <b>with</b> response'],
              #  values=pie_df['total_responses'],
               # marker=dict(colors=colors_all),
                #text=pie_df['text_total'],
                #textinfo='text',
                #hovertemplate="%{label}: %{value} <br>(%{percent})",
                #name='Total', hole=0.4), 1, 1)
            responses_plot.add_trace(go.Pie(
                labels=['Incidents <b>without</b> political response', 'Incidents <b>with</b> political response'],
                values=pie_df['total_political_responses'],
                marker=dict(colors=colors_pol),
                text=pie_df['text_political'],
                textinfo='text',
                hovertemplate="%{label}:<br> %{value} (%{percent})<extra></extra>",
                name='Political', hole=0.4), 1, 1)
            responses_plot.add_trace(go.Pie(
                labels=['Incidents <b>without</b> legal response', 'Incidents <b>with</b> legal response'],
                values=pie_df['total_legal_responses'],
                marker=dict(colors=colors_leg),
                text=pie_df['text_legal'],
                textinfo='text',
                hovertemplate="%{label}:<br> %{value} (%{percent})<extra></extra>",
                name='Legal', hole=0.4), 1, 2)

            responses_plot.update_layout(
                title='',
                plot_bgcolor='white',
                height=300,
                margin=dict(l=0, r=0, t=25, b=0),
                showlegend=False,
                font=dict(
                    size=14,
                    family="Lato",
                ),
                annotations=[
                    #dict(text=f'<b>Both</b><br>{pie_df.loc[1, "total_responses"]}', x=0.126, y=0.5, showarrow=False, font=dict(size=12)),
                    dict(text=f'<b>Political</b><br>responses<br>{pie_df.loc[1, "total_political_responses"]}', x=0.185, y=0.5, showarrow=False, font=dict(size=12)),
                    dict(text=f'<b>Legal</b><br>responses<br>{pie_df.loc[1, "total_legal_responses"]}', x=0.815, y=0.5, showarrow=False, font=dict(size=12))
                ],
                dragmode=False
            )

            responses_plot_2 = go.Figure()
            responses_plot_2.update_layout(
                plot_bgcolor="white",
                height=100,
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=False,
                    zeroline=False,
                ),
                yaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=False,
                    zeroline=False,
                ),
                annotations=[
                    go.layout.Annotation(
                        x=2,
                        y=2,
                        text="<i>No political or legal responses</i>",
                        showarrow=False,
                        font=dict(
                            family="Lato",
                            size=16,
                            color="black"
                        )
                    )
                ],
                dragmode=False
            )
        else:
            responses_plot = sp.make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])

            #colors_all = ['#e6eaeb', '#002C38'] ['#e6eaeb', '#89bd9e']
            colors_pol = ['#e6eaeb', '#002C38']
            colors_leg = ['#e6eaeb', '#cc0130']
            #responses_plot.add_trace(go.Pie(
                #labels=['Incidents <b>without</b> response', 'Incidents <b>with</b> response'],
               # values=pie_df['total_responses'],
               # marker=dict(colors=colors_all),
               # text=pie_df['text_total'],
                #textinfo='text',
               # hovertemplate="%{label}: %{value} <br>(%{percent})",
               # name='Total', hole=0.4), 1, 1)
            responses_plot.add_trace(go.Pie(
                labels=['Incidents <b>without</b> political response', 'Incidents <b>with</b> political response'],
                values=pie_df['total_political_responses'],
                marker=dict(colors=colors_pol),
                text=pie_df['text_political'],
                textinfo='text',
                hovertemplate="%{label}:<br> %{value} (%{percent})<extra></extra>",
                name='Political', hole=0.4), 1, 1)
            responses_plot.add_trace(go.Pie(
                labels=['Incidents <b>without</b> legal response', 'Incidents <b>with</b> legal response'],
                values=pie_df['total_legal_responses'],
                marker=dict(colors=colors_leg),
                text=pie_df['text_legal'],
                textinfo='text',
                hovertemplate="%{label}:<br> %{value} (%{percent})<extra></extra>",
                name='Legal', hole=0.4), 1, 2)

            responses_plot.update_layout(
                title='',
                plot_bgcolor='white',
                height=300,
                margin=dict(l=0, r=0, t=25, b=0),
                showlegend=False,
                font=dict(
                    size=14,
                    family="Lato",
                ),
                annotations=[
                    #dict(text=f'<b>Both</b><br>{pie_df.loc[1, "total_responses"]}', x=0.126, y=0.5, showarrow=False, font=dict(size=12)),
                    dict(text=f'<b>Political</b><br>responses<br>{pie_df.loc[1, "total_political_responses"]}', x=0.185, y=0.5, showarrow=False, font=dict(size=12)),
                    dict(text=f'<b>Legal</b><br>responses<br>{pie_df.loc[1, "total_legal_responses"]}', x=0.815, y=0.5, showarrow=False, font=dict(size=12))
                ],
                dragmode=False
            )

            responses_plot_2 = go.Figure()

            responses_plot_2.add_trace(go.Scatter(
                x=responses_grouped_2['weighted_cyber_intensity'],
                y=responses_grouped_2['percent_political'],
                marker=dict(
                    size=normalized_size_pol,
                    color='#002C38'
                ),
                text=responses_grouped_2['political_response'],
                hovertemplate='Intensity score: %{x}\
                <br>Incidents with political response: %{text}\
                <br>Percentage: %{y:.1%}<extra></extra>',
                name='Political', mode='markers'))

            responses_plot_2.add_trace(go.Scatter(
                x=responses_grouped_2['weighted_cyber_intensity'],
                marker=dict(
                    size=normalized_size_leg,
                    color='#cc0130'
                ),
                text=responses_grouped_2['legal_response'],
                hovertemplate='Intensity score: %{x}\
                            <br>Incidents with a legal response: %{text}\
                            <br>Percentage: %{y:.1%}<extra></extra>',
                y=responses_grouped_2['percent_legal'],
                name='Legal', mode='markers'))

            responses_plot_2.update_layout(
            title='',
            plot_bgcolor='white',
            height=300,
            margin=dict(l=0, r=0, t=25, b=0),
            showlegend=False,
            font=dict(
                size=14,
                family="Lato",
            ),
            xaxis=dict(
                title='Intensity of incidents',
                showgrid=True,
                showticklabels=True,
                gridcolor='rgba(0, 0, 0, 0.1)',
            ),
            yaxis=dict(
                title='',
                showgrid=True,
                showticklabels=True,
                tickformat='.0%',
                gridcolor='rgba(0, 0, 0, 0.1)',
                zerolinecolor='rgba(0, 44, 56, 0.5)',
                zerolinewidth=0.5,
            ),
           dragmode=False
        )

            if responses_grouped.political_response.sum() / responses_grouped.ID.nunique() < 0.5 \
                    and responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() < 0.5:
                responses_description_text = html.P([
                    "Only ",
                    html.B(f"{round(responses_grouped.political_response.sum() / responses_grouped.ID.nunique()*100,2)}%"),
                    " of cyber incidents were met with a political response, and only ",
                    html.B(f"{round(responses_grouped.legal_response.sum() / responses_grouped.ID.nunique()*100,2)}%"),
                    " were met with a legal response. A higher proportion of cyber incidents with a high-intensity score received political or legal responses. \
                    However, the most intense cyber incidents in our database were often not met with a response."])
            elif responses_grouped.political_response.sum() / responses_grouped.ID.nunique() < 0.5 \
                    and responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() >= 0.5:
                responses_description_text = html.P([
                    "Only ",
                    html.B(
                        f"{round(responses_grouped.political_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%"),
                    " of cyber incidents were met with a political response, while ",
                    html.B(
                        f"{round(responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%"),
                    " were met with a legal response. A higher proportion of cyber incidents with a high-intensity score received political or legal responses. \
                    However, the most intense cyber incidents in our database were often not met with a response."])
            elif responses_grouped.political_response.sum() / responses_grouped.ID.nunique() >= 0.5 \
                    and responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() < 0.5:
                responses_description_text = html.P([
                    html.B(
                        f"{round(responses_grouped.political_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%"),
                    " of cyber incidents were met with a political response, while only ",
                    html.B(
                        f"{round(responses_grouped.legal_response.sum() / responses_grouped.ID.nunique() * 100, 2)}%"),
                    " were met with a legal response. A higher proportion of cyber incidents with a high-intensity score received political or legal responses. \
                    However, the most intense cyber incidents in our database were often not met with a response."])
            else:
                responses_description_text = html.P([
                    html.B(f"{round(responses_grouped.response.sum() / responses_grouped.ID.nunique() * 100, 2)}%"),
                    " of incidents were met with a political or legal response. \
                    A higher proportion of cyber incidents with a high-intensity score received political or legal responses. \
                    However, the most intense cyber incidents in our database were often not met with a response."
                ])

            responses_donut_annotation = html.I("Note: one incident can have both legal and political responses")
            responses_scatter_annotation = html.I("Note: the size of the points represents the number of incidents")

        nb_incidents = metric_values["nb_incidents"]
        average_intensity = metric_values["average_intensity"]

        return responses_plot, \
            responses_plot_2, \
            responses_description_text, \
            responses_donut_annotation, \
            responses_scatter_annotation, nb_incidents, average_intensity


def responses_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='responses_datatable', component_property='data'),
        Output(component_id='responses_datatable', component_property='tooltip_data'),
        Output(component_id="modal_responses", component_property='is_open'),
        Output(component_id="modal_responses_content", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id="incident_type_dd", component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
        Input(component_id="responses_datatable", component_property='derived_virtual_data'),
        Input(component_id="responses_datatable", component_property='active_cell'),
        Input(component_id="responses_datatable", component_property='page_current'),
        State(component_id="modal_responses", component_property="is_open"),
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

        status, modal = create_modal_text(
            data=data_dict,
            index=index,
            derived_virtual_data=derived_virtual_data,
            active_cell=active_cell,
            page_current=page_current,
            is_open=is_open
        )

        return data, tooltip_data, status, modal
