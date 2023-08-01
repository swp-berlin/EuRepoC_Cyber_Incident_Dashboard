from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from server.server_functions import filter_database_by_output, empty_figure


def inclusion_criteria_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('inclusion_graph', 'figure'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
    )
    def update_inclusion_graph(receiver_country_filter,
                               initiator_country_filter,
                               incident_type_filter,
                               start_date_start,
                               start_date_end):

        if initiator_country_filter == "All countries":
            initiator_country_filter = None
        if incident_type_filter == "All":
            incident_type_filter = None

        filtered_df = filter_database_by_output(
            df=df,
            date_start=start_date_start,
            date_end=start_date_end,
            receiver_country=receiver_country_filter,
            initiator_country=initiator_country_filter,
            incident_type=incident_type_filter,
            states_codes=states_codes
        )

        if filtered_df.empty:
            fig = empty_figure()

        else:

            inclusion_grouped = filtered_df.groupby(["inclusion_criteria"]).agg({'ID': 'nunique'}).reset_index()
            inclusion_sub_grouped = filtered_df.groupby(["inclusion_criteria_subcode"]).agg(
                {'ID': 'nunique'}).reset_index()
            inclusion_sub_grouped = inclusion_sub_grouped.sort_values(by="ID", ascending=True).reset_index(drop=True)
            inclusion_sub_grouped = inclusion_sub_grouped.rename(columns={"inclusion_criteria_subcode": "inclusion_criteria"})
            inclusion_grouped = pd.concat([inclusion_grouped, inclusion_sub_grouped])

            try:
                attacks_non_state = inclusion_grouped.loc[
                    inclusion_grouped['inclusion_criteria'] == 'Attack conducted by<br>non-state actors with political goals',
                    'ID'
                ].values[0]
                attacks_state = inclusion_grouped.loc[
                    inclusion_grouped['inclusion_criteria'] == 'Attack conducted by<br>a state-affiliated group',
                    'ID'
                ].values[0]

            except IndexError:
                attacks_non_state = None
                attacks_state = None

            if attacks_state:
                mask = inclusion_grouped['inclusion_criteria'] == 'Attack conducted by<br>non-state actors with political goals'
                inclusion_grouped.loc[mask, 'ID'] = attacks_non_state - attacks_state
            inclusion_grouped = inclusion_grouped.sort_values(by="ID", ascending=True).reset_index(drop=True)
            inclusion_grouped = inclusion_grouped[~inclusion_grouped['inclusion_criteria'].str.contains('Not available')]

            fig = px.bar(
                inclusion_grouped,
                x="ID",
                y="inclusion_criteria",
                orientation='h',
                color_discrete_sequence=['#002C38'],
                text="ID",
                hover_data={'ID': False, 'inclusion_criteria': False},
                hover_name=None
            )
            fig.update_layout(
                title="",
                xaxis_title="",
                yaxis_title="",

                xaxis=dict(showticklabels=False),
                plot_bgcolor='white',
                font=dict(
                    family="Lato",
                    color="#002C38",
                    size=14
                ),
                margin=dict(l=0, r=0, t=25, b=0, pad=0),
                height=480,
                dragmode=False
            )

        return fig
