from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
import plotly.express as px


# Define color scale for map using variations of the project's red color -- different levels of opacity
color_scale = [
    (0.00, 'rgba (137, 189, 158, 0.0)'), (0.01, 'rgba (137, 189, 158, 0.0)'),
    (0.01, 'rgba (137, 189, 158, 0.4)'), (0.125, 'rgba (137, 189, 158, 0.4)'),
    (0.125, 'rgba (137, 189, 158, 0.6)'), (0.25, 'rgba (137, 189, 158, 0.6)'),
    (0.25, 'rgba (137, 189, 158, 0.8)'), (0.375, 'rgba (137, 189, 158, 0.8)'),
    (0.375, 'rgba (137, 189, 158, 0.9)'), (0.5, 'rgba (137, 189, 158, 0.9)'),
    (0.5, 'rgba (0, 44, 56, 0.6)'), (0.625, 'rgba (0, 44, 56, 0.6)'),
    (0.625, 'rgba (0, 44, 56, 0.8)'), (0.75, 'rgba (0, 44, 56, 0.8)'),
    (0.75, 'rgba (0, 44, 56, 0.9)'), (0.875, 'rgba (0, 44, 56, 0.9)'),
    (0.875, 'rgba (0, 44, 56, 1)'), (1.0, 'rgba (0, 44, 56, 1)'),
]


def map_title_callback(app):
    @app.callback(
        Output("selected_options_text", "children"),
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
            return html.Div([
                html.H3(f"Overview of incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}")
            ])
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.Div([
                html.H3(f"Overview of incidents in the database between {start_date} and {end_date}")
            ])
        elif receiver_country == "Global (states)" and initiator_country:
            return html.Div([
                html.H3(f"Overview of incidents initiated by actors based in {initiator_country} between {start_date} and {end_date}")
            ])
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.Div([
                html.H3(f"Overview of incidents against {receiver_country} between {start_date} and {end_date}")
            ])


def map_callback(app, df=None, geometry=None):
    @app.callback(
        Output(component_id='nb_incidents', component_property='children'),
        Output(component_id='average_intensity', component_property='children'),
        Output(component_id='nb_threat_groups', component_property='children'),
        Output(component_id='map', component_property='figure'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
    )
    def update_plot(input_receiver_country,
                    input_initiator_country,
                    start_date_start,
                    start_date_end):

        # Ensure the DataFrame is not overwritten
        copied_data = df.copy(deep=True)

        # Convert input dates to datetime
        date_range = pd.date_range(start=start_date_start, end=start_date_end)

        # Define input filters in dictionary
        input_filters = {
            'filter_column': input_receiver_country,
            'initiator_country': input_initiator_country,
        }

        # Filter the data based on input dates and filters
        filtered_df = copied_data.loc[copied_data['start_date'].isin(date_range)]

        for col, val in input_filters.items():
            if val is not None:
                filtered_df = filtered_df.loc[filtered_df[col] == val]

        # If the filtered DataFrame is empty indicate 0 incidents and empty map which still shows the selected country
        if filtered_df.empty:
            filtered_df = copied_data.loc[copied_data['filter_column'] == input_filters['filter_column']]
            nb_incidents = 0
            average_intensity = 0
            number_of_groups = 0
            grouped_df = filtered_df.drop(
                columns=["start_date", "initiator_country", "initiator_name", "weighted_cyber_intensity"]).reset_index()
            grouped_df = grouped_df.set_index("ISO_A3")
            grouped_df["ID"] = 0
            if len(grouped_df) > 1:
                grouped_df = grouped_df.head(1)
        else:
            # Count the number of unique incidents and threat groups and calculate the average intensity
            nb_incidents = filtered_df['ID'].nunique()
            average_intensity = round(filtered_df['weighted_cyber_intensity'].mean(), 1)
            number_of_groups = filtered_df['initiator_name'].nunique()
            # Group the data by country and count the number of unique incidents per country
            grouped_df = filtered_df.groupby(['ISO_A3', 'receiver_country']).agg({'ID': 'nunique'}).reset_index()
            grouped_df = grouped_df.set_index("ISO_A3")

        # Add the geometry to the filtered DataFrame for plotting the map
        grouped_df = grouped_df.merge(geometry, on="ISO_A3")
        grouped_gdf = gpd.GeoDataFrame(grouped_df, geometry=grouped_df.geometry)

        # Define the map center and zoom level
        if any(text in input_receiver_country for text in ['(states)', '(member states)', '(region)', '(insitutions)']):
            map_latitude = 65
            map_longitude = 0
            map_zoom = 0.1
        else:
            map_latitude = grouped_gdf.latitude.max()
            map_longitude = grouped_gdf.longitude.max()
            map_zoom = 3

        # Create the choropleth map
        fig = px.choropleth_mapbox(
            grouped_gdf,
            geojson=grouped_gdf.geometry,
            locations=grouped_gdf.index,
            range_color=(0, 150),
            color='ID',
            color_continuous_scale=color_scale,
            mapbox_style="carto-positron",
            opacity=0.9,
            labels={'ID': ''},
                                   )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                titleside="top",
                tickmode="array",
                tickvals=[0, 20, 40, 60, 80, 100, 120, 140],
                ticktext=["0", "20", "40", "60", "80", "100", "120", ">140"],
                title="Number of <br> cyber incidents",
            ),
            coloraxis_colorbar_y=-0.2,
            coloraxis_colorbar_x=0,
            coloraxis_colorbar_xanchor='left',
            coloraxis_colorbar_yanchor='bottom',
            coloraxis_colorbar_orientation='h',
        )
        fig.update_layout(mapbox={
            "zoom": map_zoom,
            "center": {"lat": map_latitude, "lon": map_longitude}
        })

        return nb_incidents, average_intensity, number_of_groups, fig
