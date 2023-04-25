import pandas as pd
import re


def filter_database_by_output(
        df=None,
        date_start=None,
        date_end=None,
        receiver_country=None,
        initiator_country=None,
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
        region_filter = "EU"
    elif receiver_country == "NATO (member states)":
        receiver_country = None
        region_filter = "NATO"
    else:
        receiver_country = receiver_country
        region_filter = None

    input_filters = {
        'receiver_country': receiver_country,
        'initiator_country': initiator_country,
    }

    filtered_df = copied_data.loc[copied_data['start_date'].isin(date_range)]

    if region_filter is not None:
        filtered_df = filtered_df[filtered_df['receiver_region'].str.contains(f"\'{region_filter}\'")]

    for col, val in input_filters.items():
        if val is not None:
            filtered_df = filtered_df[filtered_df[col] == val]

    return filtered_df


def filter_datatable(
        df=None,
        receiver_country_filter=None,
        initiator_country_filter=None,
        start_date=None,
        end_date=None,
        states_codes=None,
        types_clickdata=None,
        targets_clickdata=None
):

    # Copy DataFrame and fill missing values with empty strings
    filtered_data = df.copy(deep=True)
    filtered_data = filtered_data.fillna("").astype(str)

    # Set region_filter to None
    region_filter = None

    if receiver_country_filter:
        if receiver_country_filter == "Global (states)":
            receiver_country_filter = None
        elif "(states)" in receiver_country_filter and receiver_country_filter != "Global (states)":
            state = receiver_country_filter.split(" ")[0]
            if state in states_codes:
                region_filter = states_codes[state]
                receiver_country_filter = None
        elif receiver_country_filter == "EU (member states)":
            receiver_country_filter = None
            region_filter = re.compile(r"\bEU\b|\bEU[;\s]|[;\s]EU[;\s]")
        elif receiver_country_filter == "NATO (member states)":
            receiver_country_filter = None
            region_filter = "NATO"
        else:
            receiver_country_filter = receiver_country_filter

    input_filters = {
        'receiver_country': receiver_country_filter,
        'initiator_country': initiator_country_filter,
        'receiver_region': region_filter
    }

    for col, val in input_filters.items():
        if val is not None:
            if col == 'receiver_region':
                filtered_data = filtered_data[filtered_data['receiver_region'].str.contains(val, regex=True)]
            else:
                filtered_data = filtered_data[filtered_data[col].str.contains(val)]

    filtered_data = filtered_data[filtered_data['start_date'].between(start_date, end_date)]

    if types_clickdata:
        filtered_data = filtered_data[filtered_data['incident_type'].str.contains(types_clickdata['points'][0]['customdata'][0])]

    if targets_clickdata:
        point = targets_clickdata["points"][0]["label"]
        filtered_data = filtered_data[filtered_data['receiver_category'].str.contains(point) | filtered_data['receiver_category_subcode'].str.contains(point)]

    return filtered_data
