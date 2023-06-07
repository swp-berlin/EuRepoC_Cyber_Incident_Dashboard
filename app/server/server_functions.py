import pandas as pd
import re


def filter_database_by_output(
        df=None,
        date_start=None,
        date_end=None,
        receiver_country=None,
        initiator_country=None,
        incident_type=None,
        states_codes=None):

    copied_data = df.copy(deep=True)
    date_range = pd.date_range(start=date_start, end=date_end)

    region_filter = None

    if receiver_country == "Global (states)":
        receiver_country = None
        region_filter = None
    elif "(states)" in receiver_country and receiver_country != "Global (states)":
        for key in states_codes.keys():
            if receiver_country == key:
                receiver_country = None
                region_filter = states_codes[key]
    elif receiver_country == "EU (member states)":
        receiver_country = None
        region_filter = "EU\(MS\)"
    elif receiver_country == "NATO (member states)":
        receiver_country = None
        region_filter = "NATO"
    else:
        receiver_country = receiver_country
        region_filter = None

    input_filters = {
        'receiver_country': receiver_country,
        'initiator_country': initiator_country,
        'incident_type': incident_type,
    }

    filtered_df = copied_data.loc[copied_data['start_date'].isin(date_range)]

    if region_filter is not None:
        filtered_df = filtered_df[filtered_df['receiver_region'].str.contains(region_filter)]

    for col, val in input_filters.items():
        if val is not None:
            filtered_df = filtered_df[filtered_df[col] == val]

    return filtered_df


def filter_datatable(
        df=None,
        receiver_country_filter=None,
        initiator_country_filter=None,
        incident_type_filter=None,
        start_date=None,
        end_date=None,
        states_codes=None,
        types_clickdata=None,
        targets_clickdata=None,
        initiators_clickdata=None,
):

    # Copy DataFrame and fill missing values with empty strings
    copied_df = df.copy(deep=True)
    copied_df = copied_df.fillna("").astype(str)
    copied_df['start_date'] = pd.to_datetime(copied_df['start_date'])
    #date_range = pd.date_range(start=start_date, end=end_date)

    # Set region_filter to None
    region_filter = None

    if receiver_country_filter:
        if receiver_country_filter == "Global (states)":
            receiver_country_filter = None
        elif "(states)" in receiver_country_filter and receiver_country_filter != "Global (states)":
            state = receiver_country_filter
            if receiver_country_filter in states_codes:
                region_filter = states_codes[state]
                receiver_country_filter = None
        elif receiver_country_filter == "EU (member states)":
            receiver_country_filter = None
            region_filter = "EU\(MS\)"
        elif receiver_country_filter == "NATO (member states)":
            receiver_country_filter = None
            region_filter = "NATO"
        else:
            receiver_country_filter = receiver_country_filter

    input_filters = {
        'receiver_country': receiver_country_filter,
        'initiator_country': initiator_country_filter,
        'incident_type': incident_type_filter,
    }

    filtered_data = copied_df[
        (copied_df['start_date'] >= start_date) & (copied_df['start_date'] <= end_date)
        ]

    if region_filter is not None:
        filtered_data = filtered_data[filtered_data['receiver_region'].str.contains(region_filter, regex=True)]

    for col, val in input_filters.items():
        if val is not None:
            filtered_data = filtered_data[filtered_data[col].str.contains(val, regex=False)]


    if types_clickdata:
        if types_clickdata['points'][0]['customdata'][0] == "Data theft":
            filtered_data = filtered_data.loc[
                ~filtered_data['incident_type'].str.contains('Data theft & Doxing', regex=False) & filtered_data['incident_type'].str.contains(
                    'Data theft', regex=False)]
        else:
            filtered_data = filtered_data[filtered_data['incident_type'].str.contains(
                types_clickdata['points'][0]['customdata'][0], regex=False)]

    if targets_clickdata:
        point = targets_clickdata["points"][0]["label"]
        filtered_data = filtered_data[filtered_data['receiver_category'].str.contains(point, regex=False) \
                                      | filtered_data['receiver_category_subcode'].str.contains(point, regex=False)]

    if initiators_clickdata:
        point = initiators_clickdata["points"][0]["label"]
        filtered_data = filtered_data[filtered_data['initiator_category'].str.contains(point, regex=False)]

    return filtered_data


import plotly.graph_objs as go


def empty_figure(height_value=400):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor="white",
        height=height_value,
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
                text="<i>No incidents corresponding to your selection</i>",
                showarrow=False,
                font=dict(
                    family="Lato",
                    size=16,
                    color="black"
                )
            )
        ]
    )
    return fig
