from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd
import plotly.express as px
from datetime import date

today = date(2023,5,10)

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
        if incident_type == "All" or incident_type is None:
            incident_type = "cyber"

        if receiver_country != "Global (states)" and initiator_country:
            return html.Div([
                html.H3(f"Overview of {incident_type.lower()} incidents from {initiator_country} against {receiver_country} between {start_date} and {end_date}")
            ])
        elif receiver_country == "Global (states)" and initiator_country is None:
            return html.Div([
                html.H3(f"Overview of {incident_type.lower()} incidents in the database between {start_date} and {end_date}")
            ])
        elif receiver_country == "Global (states)" and initiator_country:
            return html.Div([
                html.H3(f"Overview of {incident_type.lower()} incidents initiated by actors based in {initiator_country} between {start_date} and {end_date}")
            ])
        elif receiver_country != "Global (states)" and initiator_country is None:
            return html.Div([
                html.H3(f"Overview of {incident_type.lower()} incidents against {receiver_country} between {start_date} and {end_date}")
            ])

def metric_values_callback(app):
    @app.callback(
        Output(component_id='nb_incidents', component_property='children'),
        Output(component_id='average_intensity', component_property='children'),
        Input(component_id="metric_values", component_property="data"),
    )
    def update_metrics(metric_values):

        nb_incidents = metric_values["nb_incidents"]
        average_intensity = metric_values["average_intensity"]

        return nb_incidents, average_intensity

def map_callback(app, df=None, geometry=None):
    @app.callback(
        #Output(component_id='nb_incidents', component_property='children'),
        #Output(component_id='average_intensity', component_property='children'),
        Output(component_id='nb_threat_groups', component_property='children'),
        Output(component_id='map', component_property='figure'),
        Input(component_id='receiver_country_dd', component_property='value'),
        Input(component_id='initiator_country_dd', component_property='value'),
        Input(component_id='incident_type_dd', component_property='value'),
        Input(component_id='date-picker-range', component_property='start_date'),
        Input(component_id='date-picker-range', component_property='end_date'),
    )
    def update_plot(input_receiver_country,
                    input_initiator_country,
                    input_incident_type,
                    start_date_start,
                    start_date_end):

        if input_initiator_country == "All countries":
            input_initiator_country = None
        if input_incident_type == "All":
            input_incident_type = None

        # Ensure the DataFrame is not overwritten
        copied_data = df.copy(deep=True)

        # Convert input dates to datetime
        date_range = pd.date_range(start=start_date_start, end=start_date_end)

        # Define input filters in dictionary
        input_filters = {
            'filter_column': input_receiver_country,
            'initiator_country': input_initiator_country,
            'incident_type': input_incident_type,
        }

        # Filter the data based on input dates and filters
        filtered_df = copied_data.loc[copied_data['start_date'].isin(date_range)]

        for col, val in input_filters.items():
            if val is not None:
                filtered_df = filtered_df.loc[filtered_df[col] == val]

        # If the filtered DataFrame is empty indicate 0 incidents and empty map which still shows the selected country
        if filtered_df.empty:
            filtered_df = copied_data.loc[copied_data['filter_column'] == input_filters['filter_column']]
            #nb_incidents = 0
            #average_intensity = 0
            number_of_groups = 0
            grouped_df = filtered_df.drop(
                columns=["start_date", "initiator_country", "initiator_name", "incident_type", "weighted_cyber_intensity"]).reset_index()
            grouped_df = grouped_df.set_index("ISO_A3")
            grouped_df["ID"] = 0
            if len(grouped_df) > 1:
                grouped_df = grouped_df.head(1)
        else:
            # Count the number of unique incidents and threat groups and calculate the average intensity
            #nb_incidents = filtered_df['ID'].nunique()
            #average_intensity = round(filtered_df['weighted_cyber_intensity'].mean(), 1)
            number_of_groups = filtered_df['initiator_name'].nunique()
            # Group the data by country and count the number of unique incidents per country
            grouped_df = filtered_df.groupby(['ISO_A3', 'receiver_country']).agg({'ID': 'nunique'}).reset_index()
            grouped_df = grouped_df.set_index("ISO_A3")

        # Add the geometry to the filtered DataFrame for plotting the map
        grouped_df = grouped_df.merge(geometry, on="ISO_A3")
        grouped_gdf = gpd.GeoDataFrame(grouped_df, geometry=grouped_df.geometry)

        if input_receiver_country == "Global (states)" \
                and input_initiator_country is None \
                and input_incident_type is None\
                and start_date_start == "2000-01-01"\
                and start_date_end == today.strftime(format="%Y-%m-%d"):
            nb_incidents = copied_data['ID'].nunique() - 1

        # Define the map center and zoom level
        if input_receiver_country == "EU (member states)" or input_receiver_country == "EU (institutions)" \
                or input_receiver_country == "EU (region)":
            map_latitude = 54.525961
            map_longitude = 15.255119
            map_zoom = 2.1
        elif input_receiver_country == "Northern Europe" or input_receiver_country == "Northern Europe":
            map_latitude = 62.278648
            map_longitude = 12.340171
            map_zoom = 1.8
        elif input_receiver_country == "Europe (states)" or input_receiver_country == "Europe (region)":
            map_latitude = 53
            map_longitude = 9
            map_zoom = 1.5
        elif input_receiver_country == "Western Balkans (states)" or input_receiver_country == "Western Balkans (region)":
            map_latitude = 43.945372
            map_longitude = 18.171859
            map_zoom = 3
        elif input_receiver_country == "Africa" or input_receiver_country == "Africa (states)":
            map_latitude = 9.1021
            map_longitude = 18.2812
            map_zoom = 1.5
        elif input_receiver_country == "Asia (region)" or input_receiver_country == "Asia (states)":
            map_latitude = 34.047863
            map_longitude = 100.619655
            map_zoom = 1.3
        elif input_receiver_country == "Central Asia (region)" or input_receiver_country == "Central Asia (states)":
            map_latitude = 45.450688
            map_longitude = 68.831901
            map_zoom = 2
        elif input_receiver_country == "Central America (region)" or input_receiver_country == "Central America (states)":
            map_latitude = 12.769013
            map_longitude = -85.602364
            map_zoom = 3.5
        elif input_receiver_country == "Eastern Asia (region)" or input_receiver_country == "Eastern Asia (states)":
            map_latitude = 38.794595
            map_longitude = 106.534838
            map_zoom = 1.5
        elif input_receiver_country == "Gulf Countries (region)" or input_receiver_country == "Gulf Countries (states)":
            map_latitude = 26.076521
            map_longitude = 52.624512
            map_zoom = 2
        elif input_receiver_country == "Mena Region (region)" or input_receiver_country == "Mena Region (states)":
            map_latitude = 29.2985278
            map_longitude = 42.5509603
            map_zoom = 1.7
        elif input_receiver_country == "Middle East (region)" or input_receiver_country == "Middle East (states)":
            map_latitude = 29.2985278
            map_longitude = 42.5509603
            map_zoom = 2
        elif input_receiver_country == "North Africa (region)" or input_receiver_country == "North Africa (states)":
            map_latitude = 31.268205
            map_longitude = 29.995368
            map_zoom = 2
        elif input_receiver_country == "Northeast Asia (region)" or input_receiver_country == "Northeast Asia (states)":
            map_latitude = 34.047863
            map_longitude = 100.619655
            map_zoom = 2
        elif input_receiver_country == "Oceania (region)" or input_receiver_country == "Oceania (states)":
            map_latitude = -21.453069
            map_longitude = 134.649058
            map_zoom = 2
        elif input_receiver_country == "South America" or input_receiver_country == "South America":
            map_latitude = -16.972741
            map_longitude = -61.522648
            map_zoom = 1.5
        elif input_receiver_country == "Global (states)" or input_receiver_country == "Global (region)" \
                or input_receiver_country == "NATO (region)" or input_receiver_country == "NATO (member states)" \
                or input_receiver_country == "NATO (institutions)" or input_receiver_country == "ISIS":
            map_latitude = 65
            map_longitude = 0
            map_zoom = 0.3
        elif any(text in input_receiver_country for text in ['(states)', '(region)', '(insitutions)']):
            map_latitude = 65
            map_longitude = 0
            map_zoom = 0.3
        elif input_receiver_country == "United States" or input_receiver_country == "International Monetary Fund"\
                or input_receiver_country == "North America" or input_receiver_country == "United Nations":
            map_latitude = grouped_gdf.latitude.max()
            map_longitude = grouped_gdf.longitude.max()
            map_zoom = 1.3
        elif input_receiver_country == "Russia":
            map_latitude = grouped_gdf.latitude.max()
            map_longitude = grouped_gdf.longitude.max()
            map_zoom = 1.2
        elif input_receiver_country == "Eastern Europe":
            map_latitude = grouped_gdf.latitude.max()
            map_longitude = grouped_gdf.longitude.max()
            map_zoom = 1
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
            labels={'ID': 'Number of incidents', "receiver_country": 'Country'},
            hover_name="receiver_country",
            hover_data=["ID"],
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                titleside="top",
                tickmode="array",
                tickvals=[0, 20, 40, 60, 80, 100, 120, 140],
                ticktext=["0", "20", "40", "60", "80", "100", "120", ">140"],
                title="",
            ),
            coloraxis_colorbar_y=-0.2,
            coloraxis_colorbar_x=0,
            coloraxis_colorbar_xanchor='left',
            coloraxis_colorbar_yanchor='bottom',
            coloraxis_colorbar_orientation='h',
        )
        fig.update_layout(mapbox={
            "zoom": map_zoom,
            "center": {"lat": map_latitude, "lon": map_longitude},
        })

        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                          'Number of incidents: %{customdata}'
        )

        return  number_of_groups, fig
    #nb_incidents, average_intensity
