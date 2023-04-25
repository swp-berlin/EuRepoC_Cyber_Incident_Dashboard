import pandas as pd


def filter_database_by_output(
        df=None,
        date_start=None,
        date_end=None,
        receiver_country=None,
        initiator_country=None,
        states_codes=None
):

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
