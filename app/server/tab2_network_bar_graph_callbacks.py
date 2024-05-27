from dash import html
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import plotly.express as px
from dash import callback_context as ctx
from server.server_functions import filter_database_by_output, filter_datatable, empty_figure
from server.common_callbacks import create_modal_text



def network_bar_graph_callback(app, df=None, states_codes=None):
    @app.callback(
        Output('dyads-bar-graph', 'figure'),
        Output('dyads-bar-graph-key-insight', 'children'),
        Input('receiver_country_dd', 'value'),
        Input("dyads-bar-graph", "clickData"),
    )
    def create_graph(input_receiver_country,
                        clickData,
                        ):

        filtered_df = filter_database_by_output(
            df=df,
            date_start="2000-01-01",
            date_end=str(dt.now().date()),
            receiver_country=input_receiver_country,
            initiator_country=None,
            incident_type=None,
            states_codes=states_codes
        )

        if filtered_df.empty:
            fig = empty_figure(height_value=600)
            text = html.Div(html.P("No cyber incidents corresponding to the selected criteria."))

        else:
            total = filtered_df["ID"].nunique()
            filtered_df["initiator_category"] = filtered_df["initiator_category"].replace("Not available", "Unknown")
            filtered_df["initiator_category"] = filtered_df["initiator_category"].replace("Unknown - not attributed", "Unknown")
            filtered_df["initiator_category"] = filtered_df["initiator_category"].replace("Non-state actor, state-affiliation suggested", "State-affiliated actor")
            filtered_df["initiator_category"] = filtered_df["initiator_category"].replace("State", "State actor")

            df_grouped = filtered_df.groupby(["initiator_country", "initiator_category"]).agg(
                {"ID": "nunique"}
            ).reset_index().rename(columns={"ID": "count"})
            df_total_per_country = filtered_df.groupby("initiator_country").agg(
                {"ID": "nunique"}
            ).reset_index().rename(columns={"ID": "total"})
            df_total_per_country = df_total_per_country.sort_values(by="total", ascending=False).head(10)

            df_total_per_country["percentage"] = (df_total_per_country['total'] / total * 100).round(1)
            df_total_per_country['text'] = df_total_per_country.apply(lambda row: f"{row['total']}<br><i>{row['percentage']}%</i>",
                                                  axis=1)

            df_grouped = df_grouped.merge(df_total_per_country, on="initiator_country", how="left")
            df_grouped = df_grouped.sort_values(by=["total"], ascending=[False]).dropna(subset="total")
            df_grouped['percentage'] = (df_grouped['total'] / total * 100).round(1)
            df_grouped['text'] = df_grouped.apply(lambda row: f"{row['total']}<br><i>{row['percentage']}%</i>",
                                                  axis=1)

            country_order = df_grouped['initiator_country'].unique()

            color_map = {
                "State-affiliated actor": "#6e977e",
                "Non-state-group": "#cc0130",
                "Not attributed": "#847e89",
                "Unknown": "#cecbd0",
                "Individual hacker(s)": "#e06783",
                "State actor": "#002C38",
            }

            fig = px.bar(
                df_grouped,
                x='count',
                y='initiator_country',
                color='initiator_category',
                orientation='h',
                custom_data=['initiator_category'],
                color_discrete_map=color_map,
                category_orders={'initiator_country': country_order},
            )

            fig.update_layout(
                xaxis_title="",
                yaxis_title="",
                legend_title="",
                plot_bgcolor="white",
                barmode='stack',
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=False,
                    zeroline=False,
                ),
                height=600,
                font=dict(
                    family="Lato",
                    color="#002C38",
                    size=14
                ),
                margin=dict(l=0, r=0, t=45, b=0, pad=0),
                dragmode=False
            )

            for i, row in df_total_per_country.iterrows():
                fig.add_annotation(
                    x=row['total'],
                    y=row['initiator_country'],
                    text=str(row['text']),
                    showarrow=False,
                    xshift=37  # Shifts the text to the right
                )

            if df_grouped.iloc[0]['initiator_country'] == "Not attributed" and input_receiver_country != "Global (states)":
                main_init = f"Most cyber incidents ({df_grouped.iloc[0]['percentage']}%) against {input_receiver_country} remain unattributed, meaning the initiator is unknown."
            elif df_grouped.iloc[0]['initiator_country'] == "Not attributed" and input_receiver_country == "Global (states)":
                main_init = f"Most cyber incidents ({df_grouped.iloc[0]['percentage']}%) remain unattributed, meaning the initiator is unknown."
            elif df_grouped.iloc[0]['initiator_country'] == "Unknown" and input_receiver_country != "Global (states)":
                main_init = f"Most cyber incidents ({df_grouped.iloc[0]['percentage']}%) against {input_receiver_country} originate from actors from unknown countries, mainly non-state-groups."
            elif df_grouped.iloc[0]['initiator_country'] == "Unknown" and input_receiver_country == "Global (states)":
                main_init = f"Most cyber incidents ({df_grouped.iloc[0]['percentage']}%) originate from actors from unknown countries, mainly non-state-groups."
            else:
                if input_receiver_country == "Global (states)":
                    receiver_country_text = ""
                else:
                    receiver_country_text = input_receiver_country
                main_init = f"Most cyber incidents ({df_grouped.iloc[0]['percentage']}%) against {receiver_country_text} originate from actors based in {df_grouped.iloc[0]['initiator_country']}"

            text = html.Div([
                    html.P([
                        main_init
                    ])
            ])

        return fig, text


def network_bar_text_selection_callback(app):
    @app.callback(
        Output('dyads-bar-selected', 'children'),
        Input('dyads-bar-graph', 'clickData'),
        Input(component_id='receiver_country_dd', component_property='value'),
    )
    def display_click_data(
            clickData,
            receiver_country_filter,
    ):
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'receiver_country_dd.value':
            clickData = None

        if clickData:
            text = html.Div([
                html.Span([
                    'Initiator country selected: ', html.Br(),
                    html.Span(f'{clickData["points"][0]["label"]}', style={'font-weight': 'bold'}),
                ]),
                html.Br(),
                html.Span([
                    'Initiator category selected: ', html.Br(),
                    html.Span(f'{clickData["points"][0]["customdata"][0]}', style={'font-weight': 'bold'}),
                ], style={"padding-top": "10px"}),
                html.Br(),
                html.Span([
                    'Total: ', html.Br(),
                    html.Span(f'{clickData["points"][0]["x"]}', style={'font-weight': 'bold'})
                ], style={"padding-top": "10px"}),
                html.Br(),
            ])
        else:
            text = html.P([
                html.I(
                    className="fa-solid fa-arrow-pointer",
                    style={'text-align': 'center', 'font-size': '15px', 'color': '#cc0130'},
                ),
                ' Click on a bar in the graph to see corresponding incidents in the table below'
            ], style={'font-style': 'italic'})
        return text


def network_bar_datatable_callback(app, df=None, states_codes=None, data_dict=None, index=None):
    @app.callback(
        Output(component_id='dyads_bar_datatable', component_property='data'),
        Output(component_id='dyads_bar_datatable', component_property='tooltip_data'),
        Output(component_id="modal_conflict_dyads_bar", component_property='is_open'),
        Output(component_id="modal_conflict_dyads_bar_content", component_property='children'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id="dyads-bar-graph", component_property="clickData"),
        Input(component_id="dyads_bar_datatable", component_property="derived_virtual_data"),
        Input(component_id="dyads_bar_datatable", component_property='active_cell'),
        Input(component_id="dyads_bar_datatable", component_property='page_current'),
        Input(component_id="metric_values", component_property="data"),
        State(component_id="modal_conflict_dyads_bar", component_property="is_open"),
    )
    def update_table(receiver_country_filter,
                     clickData,
                     derived_virtual_data,
                     active_cell,
                     page_current,
                     metric_values,
                     is_open):

        # Filter data based on inputs
        filtered_data = filter_datatable(
            df=df,
            receiver_country_filter=receiver_country_filter,
            initiator_country_filter=None,
            start_date="2000-01-01",
            end_date=str(dt.now().date()),
            states_codes=states_codes,
            initiators_country_clickdata=clickData,
        )

        filtered_data["start_date"] = filtered_data["start_date"].dt.strftime("%Y-%m-%d")

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

        return data, tooltip_data, status, modal
