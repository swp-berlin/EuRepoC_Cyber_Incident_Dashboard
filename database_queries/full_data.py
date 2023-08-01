from EuRepoC.query_database import query_database, QueryDatabase, get_token
from EuRepoC.cleaning_functions import clean_incidents, clean_incidents_dict
from EuRepoC.tables import TablesAll
import pandas as pd
import pickle
import numpy as np


TOKEN = get_token("/Users/camille/Sync/PycharmProjects/stats_dashboard/database_queries/API_token.txt")

all_incidents = query_database(
    query_class=QueryDatabase(),
    token=TOKEN,
    status_type="status",
    status="Sent to database",
    )

incidents_sent_to_tracker = query_database(
    query_class=QueryDatabase(),
    token=TOKEN,
    status_type="tracker_status",
    status="Sent to tracker",
    )

# Clean data
all_database_incidents_clean = clean_incidents(all_incidents)
all_tracker_incidents_clean = clean_incidents(incidents_sent_to_tracker)

all_incidents_clean = all_database_incidents_clean
for incident in all_tracker_incidents_clean:
    if incident not in all_incidents_clean:
        all_incidents_clean.append(incident)

for incident in all_incidents_clean:
    for region_list in incident["receiver_region"]:
        for i, region in enumerate(region_list):
            if region == "EU":
                region_list[i] = "EU(MS)"

for incident in all_incidents_clean:
    for i in range(len(incident["receiver_country"])):
        if incident["receiver_country"][i] == "EU (region)" and i < len(incident["receiver_category"]) and "International / supranational organization" in incident["receiver_category"][i]:
            incident["receiver_country"][i] = "EU (institutions)"


for incident in all_incidents_clean:
    for i in range(len(incident["receiver_country"])):
        if incident["receiver_country"][i] == "NATO (region)" and i < len(incident["receiver_category"]) and "International / supranational organization" in incident["receiver_category"][i]:
            incident["receiver_country"][i] = "NATO (institutions)"


# Clean data
all_database_incidents_clean_dict = clean_incidents_dict(all_incidents)
all_tracker_incidents_clean_dict = clean_incidents_dict(incidents_sent_to_tracker)

all_incidents_clean_dict = all_database_incidents_clean_dict
for incident in all_tracker_incidents_clean_dict:
    if incident not in all_incidents_clean_dict:
        all_incidents_clean_dict.append(incident)

for incident in all_incidents_clean_dict:
    for receiver in incident["receivers"]:
        if receiver["receiver_country"] == "EU (region)" and "International / supranational organization" in receiver["receiver_category"]:
            receiver["receiver_country"] = "EU (institutions)"



for incident in all_incidents_clean_dict:
    for receiver in incident["receivers"]:
        if receiver["receiver_country"] == "NATO (region)" and "International / supranational organization" in receiver["receiver_category"]:
            receiver["receiver_country"] = "NATO (institutions)"


for incident in all_incidents_clean_dict:
    if incident["number_of_attributions"] > 0:
        for attribution in incident["attributions"]:
            attribution_full_date = []
            year = attribution.get("attribution_year")
            month = attribution.get("attribution_month")
            day = attribution.get("attribution_day")
            if all(v is None for v in [year, month, day]):
                attribution_full_date.append("Not available")
            elif year == 0:
                attribution_full_date.append("Not available")
            elif month is None or month == 0:
                attribution_full_date.append(str(year))
            elif day is None or day == 0:
                attribution_full_date.append(f"{year}-{month}")
            else:
                attribution_full_date.append(f"{year}-{month}-{day}")
            attribution["attribution_full_date"] = attribution_full_date


for incident in all_incidents_clean_dict:
    if incident["number_of_political_responses"] > 0:
        for response in incident["political_responses"]:
            response_full_date = []
            year = response.get("political_response_year")
            month = response.get("political_response_month")
            day = response.get("political_response_day")
            if all(v is None for v in [year, month, day]):
                response_full_date.append("Not available")
            elif year == 0:
                response_full_date.append("Not available")
            elif month is None or month == 0:
                response_full_date.append(str(year))
            elif day is None or day == 0:
                response_full_date.append(f"{year}-{month}")
            else:
                response_full_date.append(f"{year}-{month}-{day}")
            response["political_response_full_date"] = response_full_date

for incident in all_incidents_clean_dict:
    if incident["number_of_legal_responses"] > 0:
        for response in incident["legal_responses"]:
            response_full_date = []
            year = response.get("legal_response_year")
            month = response.get("legal_response_month")
            day = response.get("legal_response_day")
            if all(v is None for v in [year, month, day]):
                response_full_date.append("Not available")
            elif year == 0:
                response_full_date.append("Not available")
            elif month is None or month == 0:
                response_full_date.append(str(year))
            elif day is None or day == 0:
                response_full_date.append(f"{year}-{month}")
            else:
                response_full_date.append(f"{year}-{month}-{day}")
            response["legal_response_full_date"] = response_full_date

def replace_empty_strings(data):
    if isinstance(data, list):
        if len(data) == 0:
            return ["Not available"]
        return [replace_empty_strings(item) for item in data]
    elif isinstance(data, dict):
        return {k: replace_empty_strings(v) for k, v in data.items()}
    elif data == "":
        return "Not available"
    else:
        return data

all_incidents_clean_dict = replace_empty_strings(all_incidents_clean_dict)


df = pd.DataFrame(all_incidents_clean)
tables = TablesAll(all_incidents_clean)
tables.get_all_tables()

start_date = tables.start_date.copy(deep=True)
weighted_cyber_intensity = tables.weighted_cyber_intensity.copy(deep=True)
impact_indicator_value = tables.impact_indicator_value.copy(deep=True)
offline_conflict_intensity = tables.offline_conflict_intensity_subcode.copy(deep=True)
offline_conflict_intensity["offline_conflict_intensity_subcode"] = offline_conflict_intensity["offline_conflict_intensity_subcode"].str.replace("HIIK ", "")
attribution_date = tables.attributions_full_df.copy(deep=True)
attribution_date = attribution_date.drop(columns=["attribution_ID", "attribution_type", "attributing_country", "attributing_actor", "attribution_basis", "Settled"])
attribution_date = attribution_date.drop_duplicates()
number_of_political_responses = tables.number_of_political_responses.copy(deep=True)
number_of_legal_responses = tables.number_of_legal_responses.copy(deep=True)

attribution_time = start_date.merge(attribution_date, on="ID", how="left")
attribution_time["start_date"] = pd.to_datetime(attribution_time["start_date"])
attribution_time["attribution_date"] = pd.to_datetime(attribution_time["attribution_date"])
to_date_diff = lambda x: (x['attribution_date'] - x['start_date']) if (x['attribution_date'] - x['start_date']) >= pd.Timedelta('0 days') else np.nan
attribution_time['time_to_attribution'] = attribution_time.apply(to_date_diff, axis=1)
attribution_time['time_to_attribution'] = attribution_time['time_to_attribution'].apply(lambda x: int(x.days) if pd.notna(x) else None)

from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd

scaler = MinMaxScaler(feature_range=(0, 4))

def get_radar_scores_scaled(df, column_name, new_column_name):
    df[column_name] = pd.to_numeric(df[column_name])
    df[column_name] = np.sqrt(df[column_name])
    scaler.fit(df[[column_name]])
    df[new_column_name] = scaler.transform(df[[column_name]])
    value_average_converted = df[new_column_name].mean()
    return df, value_average_converted

impact_indicator_value_with_scores, impact_indicator_value_average_converted = get_radar_scores_scaled(impact_indicator_value, "impact_indicator_value", "radar_score_impact")
weighted_cyber_intensity_with_scores, weighted_cyber_intensity_average_converted = get_radar_scores_scaled(weighted_cyber_intensity, "weighted_cyber_intensity", "radar_score_intensity")
number_of_political_responses_with_scores, number_of_political_responses_average_converted = get_radar_scores_scaled(number_of_political_responses, "number_of_political_responses", "radar_score_political")
number_of_legal_responses_with_scores, number_of_legal_responses_average_converted = get_radar_scores_scaled(number_of_legal_responses, "number_of_legal_responses", "radar_score_legal")
offline_conflict_intensity_with_scores, offline_conflict_intensity_average_converted = get_radar_scores_scaled(offline_conflict_intensity, "offline_conflict_intensity_subcode", "radar_score_offline_conflict")
attribution_time_with_scores, attribution_time_average_converted = get_radar_scores_scaled(attribution_time, "time_to_attribution", "radar_score_attribution")


impact_indicator_value_with_scores = impact_indicator_value_with_scores.drop(columns=['impact_indicator_value'])
weighted_cyber_intensity_with_scores = weighted_cyber_intensity_with_scores.drop(columns=['weighted_cyber_intensity'])
number_of_political_responses_with_scores = number_of_political_responses_with_scores.drop(columns=['number_of_political_responses'])
number_of_legal_responses_with_scores = number_of_legal_responses_with_scores.drop(columns=['number_of_legal_responses'])
offline_conflict_intensity_with_scores = offline_conflict_intensity_with_scores.drop(columns=['offline_conflict_intensity_subcode'])
attribution_time_with_scores = attribution_time.drop_duplicates(subset=['ID'])
attribution_time_with_scores = attribution_time_with_scores.drop(columns=['start_date', 'attribution_date', 'time_to_attribution'])

df = df.merge(impact_indicator_value_with_scores, on='ID', how='outer')
df = df.merge(weighted_cyber_intensity_with_scores, on='ID', how='outer')
df = df.merge(number_of_political_responses_with_scores, on='ID', how='outer')
df = df.merge(number_of_legal_responses_with_scores, on='ID', how='outer')
df = df.merge(offline_conflict_intensity_with_scores, on='ID', how='outer')
df = df.merge(attribution_time_with_scores, on='ID', how='outer')

average_scores_across_incidents = {
    '<b>Impact indicator</b>': impact_indicator_value_average_converted,
    '<b>Cyber intensity</b>': weighted_cyber_intensity_average_converted,
    '<b>Offline conflict intensity</b>': offline_conflict_intensity_average_converted,
    '<b>Attribution time</b>': attribution_time_average_converted,
    "<b>Number of political responses</b>": number_of_political_responses_average_converted,
    "<b>Number of legal responses</b>": number_of_legal_responses_average_converted,
    "<b>Impact indicator</b>": impact_indicator_value_average_converted
}

with open('./data/average_scores_across_incidents.pickle', 'wb') as f:
    pickle.dump(average_scores_across_incidents, f)


df = df.drop(
    columns=[
        "status",
        "settled_attribution_id", "settled_attribution_year", "settled_attribution_month", "settled_attribution_day",
        "settled_attribution_basis", "settled_attribution_type", "settled_attribution_type_subcode",
        "settled_attributing_country", "settled_attributing_actor", "settled_attribution_it_company",
        "temporal_attribution_sequence", "other_attribution_id", "other_attribution_year",
        "other_attribution_month", "other_attribution_day", "other_attribution_basis", "other_attribution_type",
        "other_attribution_type_subcode", "other_attributing_country", "other_attributing_actor",
        "other_attribution_it_company", "other_legal_attribution_refs", "other_legal_attribution_refs_subcode",
        "other_temporal_attribution_sequence", "other_attributed_initiator_name", "other_attributed_initiator_country",
        "other_attributed_initiator_category", "other_attributed_initiator_category_subcode",
        "political_response_date_year", "political_response_date_month", "political_response_date_day",
        "political_response_country", "political_response_actor", "political_response_type", "political_response_type_subcode",
        'legal_response_date_year', 'legal_response_date_month', 'legal_response_date_day', 'legal_response_country',
        'legal_response_type', 'legal_response_type_subcode', 'legal_response_actor', "sources_name", "sources_category",
        "logs", "articles"
    ]
)

def to_string(x):
    if isinstance(x, list) and any(isinstance(item, list) for item in x):
        joined_sublists = ' - '.join(['; '.join(map(str, sublist)) for sublist in x])
        return joined_sublists
    elif isinstance(x, list) and not any(isinstance(item, list) for item in x):
        if x != [""] and x != [" "]:
            return '; '.join([str(i) for i in x])
        else:
            return None
    elif x is None:
        return None
    else:
        return str(x)


def convert_column(x, column_name):
    x[column_name] = x[column_name].apply(to_string)
    return x


for col in df.columns:
    convert_column(df, col)

political_responses = tables.political_responses.copy(deep=True)
attributions = tables.attributions_full_df.copy(deep=True)
legal_responses = tables.legal_responses.copy(deep=True)

attributions = attributions.fillna("")
attributions = attributions.replace("nan", "")
attributions = attributions.replace(to_replace=';', value=',', regex=True)


def replace_nat_with_empty_string(value):
    if pd.isnull(value):
        return ""
    return value
attributions = attributions.applymap(replace_nat_with_empty_string)

attributions["attribution_basis"] = attributions["attribution_basis"].astype(str)

attributions["attribution_basis_clean"] = attributions["attribution_basis"].apply(
    lambda x: "Industry attribution" if x == "IT-security community attributes attacker" else x
)
attributions["attribution_basis_clean"] = attributions["attribution_basis_clean"].apply(
    lambda x: "Political attribution" if x in [
        "Attribution by receiver government / state entity",
        "Attribution by EU institution/agency",
        "Attribution by international organization"
    ] else x
)
attributions["attribution_basis_clean"] = attributions["attribution_basis_clean"].apply(
    lambda x: "Other attribution basis" if x and x in [
        "Receiver attributes attacker",
        "Contested attribution",
        "Media-based attribution"
    ] else x
)
attributions["attribution_basis_clean"] = attributions["attribution_basis_clean"].apply(
    lambda x: "" if x and x in [
        "None",
        "",
        "Not available"
    ] else x
)

attributions_reversed = attributions.groupby("ID").agg(list).reset_index()
attributions_reversed = attributions_reversed.drop(columns="Settled")
for col in attributions_reversed.columns:
    convert_column(attributions_reversed, col)

political_responses = political_responses.fillna("")
political_responses = political_responses.replace("nan", "")
political_responses = political_responses.applymap(replace_nat_with_empty_string)

legal_responses = legal_responses.fillna("")
legal_responses = legal_responses.replace("nan", "")
legal_responses = legal_responses.applymap(replace_nat_with_empty_string)

political_responses_reversed = political_responses.groupby("ID").agg(list).reset_index()
for col in political_responses_reversed.columns:
    convert_column(political_responses_reversed, col)

legal_responses_reversed = legal_responses.groupby("ID").agg(list).reset_index()
for col in legal_responses_reversed.columns:
    convert_column(legal_responses_reversed, col)

df = df.merge(attributions_reversed, on="ID", how="left")
df = df.merge(political_responses_reversed, on="ID", how="left")
df = df.merge(legal_responses_reversed, on="ID", how="left")

order_df = df.reindex(
    columns=[
        'ID',
        'name',
        'description',
        'start_date',
        'end_date',
        'inclusion_criteria',
        'inclusion_criteria_subcode',
        'source_incident_detection_disclosure',
        'incident_type',
        'receiver_name',
        'receiver_country',
        'receiver_region',
        'receiver_category',
        'receiver_category_subcode',
        'initiator_name',
        'initiator_country',
        'initiator_category',
        'initiator_category_subcode',
        'number_of_attributions',
        'attribution_ID',
        'attribution_date',
        'attribution_type',
        'attribution_basis',
        'attribution_basis_clean',
        'attributing_actor',
        'attribution_it_company',
        'attributing_country',
        'attributed_initiator',
        'attributed_initiator_country',
        'attributed_initiator_category',
        'sources_attribution',
        'cyber_conflict_issue',
        'offline_conflict_issue',
        'offline_conflict_issue_subcode',
        'offline_conflict_intensity',
        'offline_conflict_intensity_subcode',
        'number_of_political_responses',
        'political_response_date',
        'political_response_type',
        'political_response_type_subcode',
        'political_response_country',
        'political_response_actor',
        'zero_days',
        'zero_days_subcode',
        'MITRE_initial_access',
        'MITRE_impact',
        'user_interaction',
        'has_disruption',
        'data_theft',
        'disruption',
        'hijacking',
        'physical_effects_spatial',
        'physical_effects_temporal',
        'unweighted_cyber_intensity',
        'target_multiplier',
        'weighted_cyber_intensity',
        'impact_indicator',
        'impact_indicator_value',
        'functional_impact',
        'intelligence_impact',
        'political_impact_affected_entities',
        'political_impact_affected_entities_exact_value',
        'political_impact_third_countries',
        'political_impact_third_countries_exact_value',
        'economic_impact',
        'economic_impact_exact_value',
        'economic_impact_currency',
        'state_responsibility_indicator',
        'IL_breach_indicator',
        'IL_breach_indicator_subcode',
        'evidence_for_sanctions_indicator',
        'number_of_legal_responses',
        'legal_response_date',
        'legal_response_type',
        'legal_response_type_subcode',
        'legal_response_country',
        'legal_response_actor',
        'legal_attribution_reference',
        'legal_attribution_reference_subcode',
        'legal_response_indicator',
        'casualties',
        'sources_url',
        'added_to_DB',
        'updated_at'
    ]
)
order_df = order_df.fillna("")
order_df = order_df.replace("None", "")

def remove_empty(x):
    if x == "; " or x == "N":
        return ""
    else:
        return x

for col in order_df.columns:
    order_df[col] = order_df[col].apply(remove_empty)

order_df = order_df.sort_values(by='added_to_DB', ascending=False).reset_index(drop=True)

order_df.to_csv("./app/data/eurepoc_dataset.csv", index=False)

with open("./app/data/full_data_dict.pickle", "wb") as file:
    pickle.dump(all_incidents_clean_dict, file)

full_data_dict_index_map = {}
for i in range(len(all_incidents_clean_dict)):
    full_data_dict_index_map[all_incidents_clean_dict[i]["ID"]] = i

with open("./app/data/full_data_dict_index_map.pickle", "wb") as file:
    pickle.dump(full_data_dict_index_map, file)
