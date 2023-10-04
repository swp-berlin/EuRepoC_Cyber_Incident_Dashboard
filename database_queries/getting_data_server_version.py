from EuRepoC.query_database import query_database, QueryDatabase, get_token
from EuRepoC.cleaning_functions import clean_incidents
from EuRepoC.tables import TablesAll
import pandas as pd
import numpy as np


TOKEN = get_token("/home/ubuntu/database_queries/API_token.txt")

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
    for i in range(len(incident["receiver_country"])):
        if incident["receiver_country"][i] == "EU (region)" and "International / supranational organization" in incident["receiver_category"][i]:
            incident["receiver_country"][i] = "EU (institutions)"


for incident in all_incidents_clean:
    for i in range(len(incident["receiver_country"])):
        if incident["receiver_country"][i] == "NATO (region)" and "International / supranational organization" in incident["receiver_category"][i]:
            incident["receiver_country"][i] = "NATO (institutions)"

# Create tables
tables = TablesAll(all_incidents_clean)
tables.get_all_tables()

regions_dict = {
    'ID': [],
    'receiver_region': []
}

for incident in all_incidents_clean:
    regions_dict['ID'].append(incident['ID'])
    regions_dict['receiver_region'].append(incident['receiver_region'])

for inc in regions_dict["receiver_region"]:
    for region_lst in inc:
        for i, region in enumerate(region_lst):
            if region == "EU":
                region_lst[i] = "EU(MS)"

df_regions = pd.DataFrame(regions_dict)
df_regions = df_regions.explode('receiver_region')
df_regions = df_regions.explode('receiver_region')
df_regions = df_regions.drop_duplicates()
df_regions = df_regions.fillna("NO_REGION")
df_regions = df_regions.groupby("ID").agg(list).reset_index()

# Map data
receiver_country = tables.receiver_country.copy(deep=True)
start_date = tables.start_date.copy(deep=True)
initiator_country = tables.initiator_country.copy(deep=True)
initiator_name = tables.initiator_name.copy(deep=True)
weighted_cyber_intensity = tables.weighted_cyber_intensity.copy(deep=True)
incident_types = tables.incident_type.copy(deep=True)

initiator_types = tables.initiator_category.copy(deep=True)
initiator_types_data = start_date.merge(receiver_country, how="outer", on="ID")
initiator_types_data = initiator_types_data.merge(incident_types, how="outer", on="ID")
initiator_types_data = initiator_types_data.merge(initiator_country, how="outer", on="ID")
initiator_types_data = initiator_types_data.merge(initiator_types, how="outer", on="ID")
initiator_types_data = initiator_types_data.merge(initiator_name, how="outer", on="ID")
initiator_types_data = initiator_types_data.drop_duplicates()
initiator_types_data = initiator_types_data.merge(df_regions, how="left", on="ID").reset_index(drop=True)
initiator_types_data["receiver_region"] = initiator_types_data["receiver_region"].astype(str)
initiator_types_data.to_csv("/home/ubuntu/app_data/dashboard_initiators_data.csv", index=False)


# merge data
merged_data = receiver_country.merge(start_date, how="outer", on="ID")
merged_data = merged_data.merge(initiator_country, how="outer", on="ID")
merged_data = merged_data.merge(initiator_name, how="outer", on="ID")
merged_data = merged_data.merge(weighted_cyber_intensity, how="outer", on="ID")
merged_data = merged_data.merge(incident_types, how="outer", on="ID")

merged_data = merged_data.drop_duplicates()

uk_filter = merged_data[merged_data["receiver_country"] == "United Kingdom"]
date_range = pd.date_range(start="2000-01-01", end="2020-01-31")
uk_filter["start_date"] = pd.to_datetime(uk_filter["start_date"])
uk_filter = uk_filter[uk_filter["start_date"].isin(date_range)]
uk_filter["filter_column"] = "EU (member states)"
uk_filter["ISO_A3"] = "GBR"
uk_filter_ordered = uk_filter[[
    'filter_column', 'receiver_country', 'ISO_A3', 'ID', 'start_date',
    'initiator_country', 'initiator_name', 'weighted_cyber_intensity',
    'incident_type'
]]
uk_filter_ordered["start_date"] = uk_filter_ordered["start_date"].dt.strftime("%Y-%m-%d")
uk_filter_ordered["start_date"] = uk_filter_ordered["start_date"].astype(str)

states_code = pd.read_excel(
    "/home/ubuntu/database_queries/states.xlsx",
    sheet_name="Sheet1"
)

map_data = states_code.merge(merged_data, how="outer", on="receiver_country")
map_data = pd.concat([map_data, uk_filter_ordered], axis=0)
map_data["ID"] = map_data["ID"].fillna("NO_ID")
map_data["weighted_cyber_intensity"] = map_data["weighted_cyber_intensity"].fillna(0)
map_data.to_csv("/home/ubuntu/app_data/dashboard_map_data.csv", index=False)

# Evolution of cyber incidents
start_date["start_date"] = pd.to_datetime(start_date["start_date"])
start_date["year"] = start_date["start_date"].dt.year
start_date["month"] = start_date["start_date"].dt.month

evolution_merged = receiver_country.merge(start_date, how="left", on="ID")
evolution_merged = evolution_merged.merge(initiator_country, how="left", on="ID")
evolution_merged = evolution_merged.merge(incident_types, how="left", on="ID")
evolution_merged = evolution_merged.drop_duplicates()
evolution_merged = evolution_merged.merge(df_regions, how="left", on="ID").reset_index(drop=True)
evolution_merged["receiver_region"] = evolution_merged["receiver_region"].astype(str)
evolution_merged.to_csv("/home/ubuntu/app_data/dashboard_evolution_data.csv", index=False)

# Types of incidents
types_full_data = incident_types.merge(weighted_cyber_intensity, how="outer", on="ID")
types_full_data = types_full_data.merge(start_date, how="outer", on="ID")
types_full_data = types_full_data.merge(receiver_country, how="outer", on="ID")
types_full_data = types_full_data.merge(initiator_country, how="outer", on="ID")
types_full_data = types_full_data.drop_duplicates()
types_full_data = types_full_data.merge(df_regions, how="outer", on="ID")
types_full_data["receiver_region"] = types_full_data["receiver_region"].astype(str)
types_full_data["weighted_cyber_intensity"] = pd.to_numeric(types_full_data["weighted_cyber_intensity"])
types_full_data.to_csv("/home/ubuntu/app_data/dashboard_incident_types_data.csv", index=False)

# Conflict issues
conflict_issues = tables.cyber_conflict_issue.copy(deep=True)
offline_conflict = tables.offline_conflict_issue_subcode.copy(deep=True)

conflict_issues_full_data = start_date.merge(receiver_country, how="outer", on="ID")
conflict_issues_full_data = conflict_issues_full_data.merge(initiator_country, how="outer", on="ID")
conflict_issues_full_data = conflict_issues_full_data.merge(conflict_issues, how="outer", on="ID")
conflict_issues_full_data = conflict_issues_full_data.merge(offline_conflict, how="outer", on="ID")
conflict_issues_full_data = conflict_issues_full_data.drop_duplicates()
conflict_issues_full_data = conflict_issues_full_data.merge(df_regions, how="outer", on="ID")
conflict_issues_full_data["receiver_region"] = conflict_issues_full_data["receiver_region"].astype(str)
conflict_issues_full_data["cyber_conflict_issue"] = conflict_issues_full_data["cyber_conflict_issue"].str.replace("Not available", "Unknown")

conflict_issues_full_data.to_csv("/home/ubuntu/app_data/dashboard_conflict_issues_data.csv", index=False)

conflict_issues_grouped = conflict_issues_full_data.groupby(["cyber_conflict_issue"]).agg({'ID': 'nunique'}).reset_index()
conflict_issues_grouped = conflict_issues_grouped.sort_values(by="ID", ascending=False).reset_index(drop=True)
offline_conflict_grouped = conflict_issues_full_data.groupby(["offline_conflict_issue_subcode"]).agg({'ID': 'nunique'}).reset_index()
offline_conflict_grouped = offline_conflict_grouped.sort_values(by="ID", ascending=False).reset_index(drop=True)
offline_conflict_grouped = offline_conflict_grouped.drop(index=0)
offline_conflict_grouped = offline_conflict_grouped.head(5)

inclusion = tables.inclusion_criteria.copy(deep=True)
inlcusion_sub = tables.inclusion_criteria_subcode.copy(deep=True)
inclusion_full_data = start_date.merge(receiver_country, how="outer", on="ID")
inclusion_full_data = inclusion_full_data.merge(initiator_country, how="outer", on="ID")
inclusion_full_data = inclusion_full_data.merge(inclusion, how="outer", on="ID")
inclusion_full_data = inclusion_full_data.merge(inlcusion_sub, how="outer", on="ID")
inclusion_full_data = inclusion_full_data.merge(incident_types, how="outer", on="ID")
inclusion_full_data = inclusion_full_data.drop_duplicates()
inclusion_full_data = inclusion_full_data.merge(df_regions, how="outer", on="ID")
inclusion_full_data["receiver_region"] = inclusion_full_data["receiver_region"].astype(str)

inclusion_full_data["inclusion_criteria"] = inclusion_full_data["inclusion_criteria"].str.strip()  # Remove extra whitespaces

inclusion_full_data["inclusion_criteria"].replace({
    "Attack on (inter alia) political target(s), not politicized": "Non politicised attack<br>on political target(s)",
    "Attack conducted by non-state group / non-state actor with political goals (religious, ethnic, etc. groups) / undefined actor with political goals": "Attack conducted by<br>non-state actors with political goals",
    "Attack conducted by nation state (generic “state-attribution” or direct attribution towards specific state-entities, e.g., intelligence agencies)": "Attack conducted by<br>a nation state",
    "Attack on (inter alia) political target(s), politicized": "Politicised attack<br>on political target(s)",
    "Attack on critical infrastructure target(s)": "Attack on<br>critical infrastructure target(s)",
    "Attack on non-political target(s), politicized": "Politicised attack<br>on non-political target(s)",

}, inplace=True)

# Drop NaN values if present
inclusion_full_data.dropna(subset=["inclusion_criteria"], inplace=True)

inclusion_full_data["inclusion_criteria_subcode"].replace({
    "Attack conducted by a state-affiliated group (includes state-sanctioned, state-supported, state-controlled but officially non-state actors) (“cyber-proxies”) / a group that is generally attributed as state-affiliated ": "Attack conducted by<br>a state-affiliated group",
}, inplace=True)

# Drop NaN values if present
inclusion_full_data.dropna(subset=["inclusion_criteria_subcode"], inplace=True)
inclusion_full_data.to_csv("/home/ubuntu/app_data/dashboard_inclusion_data.csv", index=False)


## Network data
initiator_types = tables.initiator_category.copy(deep=True)
conflict_issues = tables.cyber_conflict_issue.copy(deep=True)

import re
network = receiver_country.merge(initiator_country, how="outer", on="ID")
network = network.merge(weighted_cyber_intensity, how="outer", on="ID")
network["weighted_cyber_intensity"] = pd.to_numeric(network["weighted_cyber_intensity"])
network = network.merge(initiator_name, how="outer", on="ID")
network = network.merge(initiator_types, how="outer", on="ID")
network = network.merge(conflict_issues, how="outer", on="ID")
network = network.drop_duplicates()
network = network.merge(df_regions, how="outer", on="ID")
network["receiver_region"] = network["receiver_region"].astype(str)
network["initiator_category"] = network["initiator_category"].astype(str).apply(lambda x: re.sub(r"Not available", "Unknown", x))
network["initiator_country"] = network["initiator_country"].astype(str).apply(lambda x: re.sub(r"Not available", "Unknown", x))
network["initiator_country"] = network["initiator_country"].astype(str).apply(lambda x: re.sub(r"nan", "Unknown", x))
network["receiver_country"] = network["receiver_country"].astype(str).apply(lambda x: re.sub(r"Not available", "Unknown", x))
network["initiator_name"] = network["initiator_name"].astype(str).apply(lambda x: re.sub(r"Not available", "Unknown", x))
network["cyber_conflict_issue"] = network["cyber_conflict_issue"].astype(str).apply(lambda x: re.sub(r"Not available", "Unknown", x))

network.to_csv("/home/ubuntu/app_data/dashboard_network_data.csv", index=False)


# Targeted sectors
targeted_sectors = tables.receiver_category_full_table.copy(deep=True)
targeted_sectors = targeted_sectors.fillna("")
targeted_sectors = targeted_sectors.drop(columns=["receiver_name"])

targeted_sectors_full = start_date.merge(initiator_country, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.merge(incident_types, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.merge(targeted_sectors, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.merge(df_regions, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.drop(columns=["receiver_region_x"])
targeted_sectors_full = targeted_sectors_full.rename(columns={"receiver_region_y": "receiver_region"})
targeted_sectors_full["receiver_region"] = targeted_sectors_full["receiver_region"].astype(str)

targeted_sectors_full["receiver_category"].replace({"Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)": "Corporate Targets"}, inplace=True)

targeted_sectors_full["receiver_category"].replace({"Not available": "Unknown"}, inplace=True)
targeted_sectors_full["receiver_category"].replace({np.nan: "Unknown"}, inplace=True)
targeted_sectors_full["receiver_category"].replace({"nan": "Unknown"}, inplace=True)

targeted_sectors_full['receiver_category'] = targeted_sectors_full['receiver_category'].astype(str)
for row in targeted_sectors_full.itertuples():
    if "Critical infrastructure" in row.receiver_category and row.receiver_category_subcode == "":
        targeted_sectors_full.at[row.Index, "receiver_category_subcode"] = "Not specified."

for row in targeted_sectors_full.itertuples():
    if "State institutions / political system" in row.receiver_category and row.receiver_category_subcode == "":
        targeted_sectors_full.at[row.Index, "receiver_category_subcode"] = "Not specified"

for row in targeted_sectors_full.itertuples():
    if "Social groups" in row.receiver_category and row.receiver_category_subcode == "":
        targeted_sectors_full.at[row.Index, "receiver_category_subcode"] = "Not Specified"

targeted_sectors_full.to_csv("/home/ubuntu/app_data/dashboard_targeted_sectors_data.csv", index=False)

# Attributions timeline
attributions = tables.attributions_full_df.copy(deep=True)
attributions = attributions.merge(start_date, on="ID", how="left")
attributions["attribution_basis"] = attributions["attribution_basis"].fillna("None")
attributions["attribution_basis"] = attributions["attribution_basis"].astype(str)
attributions_bases = attributions.copy(deep=True)

attributions["attribution_basis_clean"] = attributions["attribution_basis"].apply(
    lambda x: "Industry attribution" if x == "IT-security community attributes attacker" else x
)

attributions_bases["attribution_basis_clean"] = attributions_bases["attribution_basis"].apply(
    lambda x: "Industry attribution" if x == "IT-security community attributes attacker" else x
)

attributions["attribution_basis_clean"] = attributions["attribution_basis_clean"].apply(
    lambda x: "Political attribution" if x in [
        "Attribution by receiver government / state entity",
        "Attribution by EU institution/agency",
        "Attribution by international organization"
    ] else x
)

attributions_bases["attribution_basis_clean"] = attributions_bases["attribution_basis_clean"].apply(
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
    lambda x: np.NaN if x and x in [
        "None",
        "Not available"
    ] else x
)

attributions_bases["attribution_basis_clean"] = attributions_bases["attribution_basis_clean"].apply(
    lambda x: np.NaN if x and x in [
        "None",
        "Not available",
        "Contested attribution",
    ] else x
)


attribution_basis_df = attributions[["ID", "start_date", "attribution_ID", "attribution_date", "attribution_basis_clean"]]
attributions_bases = attributions_bases[["ID", "start_date", "attribution_ID", "attribution_date", "attribution_basis_clean"]]

attributions_bases = attributions_bases.merge(receiver_country, on='ID', how='outer')
attributions_bases = attributions_bases.merge(initiator_country, on='ID', how='outer')
attributions_bases = attributions_bases.merge(incident_types, on='ID', how='outer')
attributions_bases = attributions_bases.drop_duplicates()
attributions_bases = attributions_bases.merge(df_regions, on='ID', how='outer')
attributions_bases.to_csv("/home/ubuntu/app_data/dashboard_attributions_basis_data.csv", index=False)

# Split the data into two dataframes based on the attribution basis
attribution_start_date = attribution_basis_df[["ID", "start_date"]]
attribution_start_date["start_date"] = pd.to_datetime(attribution_start_date["start_date"])
attribution_start_date = attribution_start_date.drop_duplicates()


def get_dates_by_basis(df, attribution_basis=None, date_name=None):
    df_new = df[df['attribution_basis_clean'] == attribution_basis]
    df_new = df_new.rename(columns={'attribution_date': date_name})
    df_new = df_new.drop_duplicates()
    df_new = df_new.groupby('ID', as_index=False)[date_name].min()
    return df_new

industry_df = get_dates_by_basis(attribution_basis_df, attribution_basis="Industry attribution", date_name="industry_date")
political_df = get_dates_by_basis(attribution_basis_df, attribution_basis="Political attribution", date_name="political_date")
attacker_df = get_dates_by_basis(attribution_basis_df, attribution_basis="Attacker confirms", date_name="attacker_date")
third_party_df = get_dates_by_basis(attribution_basis_df, attribution_basis="Attribution by third-party", date_name="third_party_date")
other_df = get_dates_by_basis(attribution_basis_df, attribution_basis="Other attribution basis", date_name="other_date")

# Merge the dataframes on 'ID'
attribution_basis_df_merged = attribution_start_date.merge(industry_df[['ID', 'industry_date']], on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(political_df[['ID', 'political_date']], on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(attacker_df[['ID', 'attacker_date']], on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(third_party_df[['ID', 'third_party_date']], on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(other_df[['ID', 'other_date']], on='ID', how='outer')


# Calculate the date difference
attribution_basis_df_merged['date_difference_ind'] = (attribution_basis_df_merged['industry_date'] - attribution_basis_df_merged['start_date']).dt.days
attribution_basis_df_merged['date_difference_pol'] = (attribution_basis_df_merged['political_date'] - attribution_basis_df_merged['start_date']).dt.days
attribution_basis_df_merged['date_difference_att'] = (attribution_basis_df_merged['attacker_date'] - attribution_basis_df_merged['start_date']).dt.days
attribution_basis_df_merged['date_difference_third'] = (attribution_basis_df_merged['third_party_date'] - attribution_basis_df_merged['start_date']).dt.days
attribution_basis_df_merged['date_difference_other'] = (attribution_basis_df_merged['other_date'] - attribution_basis_df_merged['start_date']).dt.days


def convert_to_months(df, column_name=None, new_column_name=None):
    df[column_name] = df[column_name].apply(lambda x: int(x) if pd.notnull(x) else pd.NaT)
    df[column_name] = df[column_name].apply(lambda x: x if pd.notnull(x) and x >= 0 else pd.NaT)
    df[new_column_name] = df[column_name].apply(lambda x: x/30 if pd.notnull(x) else pd.NaT)
    return df

attribution_basis_df_merged = convert_to_months(attribution_basis_df_merged, column_name='date_difference_ind', new_column_name='date_difference_ind_months')
attribution_basis_df_merged = convert_to_months(attribution_basis_df_merged, column_name='date_difference_pol', new_column_name='date_difference_pol_months')
attribution_basis_df_merged = convert_to_months(attribution_basis_df_merged, column_name='date_difference_att', new_column_name='date_difference_att_months')
attribution_basis_df_merged = convert_to_months(attribution_basis_df_merged, column_name='date_difference_third', new_column_name='date_difference_third_months')
attribution_basis_df_merged = convert_to_months(attribution_basis_df_merged, column_name='date_difference_other', new_column_name='date_difference_other_months')
attribution_basis_df_merged["start_date"] = pd.to_datetime(attribution_basis_df_merged["start_date"])

attribution_basis_df_merged['average_overall'] = attribution_basis_df_merged[[
    'date_difference_ind_months',
    'date_difference_pol_months',
    'date_difference_att_months',
    'date_difference_third_months',
    'date_difference_other_months'
]].max(axis=1)

attribution_basis_df_merged = attribution_basis_df_merged.merge(receiver_country, on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(initiator_country, on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.merge(incident_types, on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged.drop_duplicates()
attribution_basis_df_merged = attribution_basis_df_merged.merge(df_regions, on='ID', how='outer')
attribution_basis_df_merged = attribution_basis_df_merged[attribution_basis_df_merged["start_date"] >= "2010-01-01"]

attribution_basis_df_merged["date_difference_ind_months"] = attribution_basis_df_merged["date_difference_ind_months"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)
attribution_basis_df_merged["date_difference_pol_months"] = attribution_basis_df_merged["date_difference_pol_months"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)
attribution_basis_df_merged["date_difference_att_months"] = attribution_basis_df_merged["date_difference_att_months"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)
attribution_basis_df_merged["date_difference_third_months"] = attribution_basis_df_merged["date_difference_third_months"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)
attribution_basis_df_merged["date_difference_other_months"] = attribution_basis_df_merged["date_difference_other_months"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)
attribution_basis_df_merged["average_overall"] = attribution_basis_df_merged["average_overall"].apply(lambda x: round(x, 1) if pd.notnull(x) else pd.NaT)

attribution_basis_df_merged.to_csv("/home/ubuntu/app_data/dashboard_attributions_data.csv", index=False)

pol = tables.political_responses.copy(deep=True)
added_to_db = tables.added_to_db
pol_graph_data = pol.merge(start_date, on='ID', how='outer')
pol_graph_data = pol_graph_data.merge(added_to_db, on='ID', how='outer')
pol_graph_data = pol_graph_data.merge(receiver_country, on='ID', how='outer')
pol_graph_data = pol_graph_data.merge(initiator_country, on='ID', how='outer')
pol_graph_data = pol_graph_data.merge(incident_types, on='ID', how='outer')
pol_graph_data = pol_graph_data.drop_duplicates()
pol_graph_data = pol_graph_data[pol_graph_data["added_to_DB"] > "2022-08-15"]
pol_graph_data = pol_graph_data.merge(df_regions, how="left", on="ID").reset_index(drop=True)
pol_graph_data["receiver_region"] = pol_graph_data["receiver_region"].astype(str)


legal = tables.legal_responses.copy(deep=True)
legal_graph_data = legal.merge(start_date, on='ID', how='outer')
legal_graph_data = legal_graph_data.merge(added_to_db, on='ID', how='outer')
legal_graph_data = legal_graph_data.merge(receiver_country, on='ID', how='outer')
legal_graph_data = legal_graph_data.merge(initiator_country, on='ID', how='outer')
legal_graph_data = legal_graph_data.merge(incident_types, on='ID', how='outer')
legal_graph_data = legal_graph_data.drop_duplicates()
legal_graph_data = legal_graph_data[legal_graph_data["added_to_DB"] > "2022-08-15"]
legal_graph_data = legal_graph_data.merge(df_regions, how="left", on="ID").reset_index(drop=True)
legal_graph_data["receiver_region"] = legal_graph_data["receiver_region"].astype(str)


nb_pol = tables.number_of_political_responses.copy(deep=True)
nb_pol["political_response"] = np.where(nb_pol["number_of_political_responses"] > 0, "Yes", "No")
nb_pol = nb_pol.drop(columns=['number_of_political_responses'])
nb_leg = tables.number_of_legal_responses.copy(deep=True)
nb_leg["legal_response"] = np.where(nb_leg["number_of_legal_responses"] > 0, "Yes", "No")
nb_leg = nb_leg.drop(columns=['number_of_legal_responses'])
responses = nb_pol.merge(nb_leg, on="ID", how="outer")
responses = responses.merge(added_to_db, on="ID", how="outer")
responses = responses[responses["added_to_DB"] > "2022-08-15"]
responses = responses.merge(weighted_cyber_intensity, on="ID", how="left")

responses["political_response"] = responses["political_response"].apply(lambda x: 1 if x == "Yes" else 0)
responses["legal_response"] = responses["legal_response"].apply(lambda x: 1 if x == "Yes" else 0)
responses["response"] = responses["political_response"] + responses["legal_response"]
responses["response"] = responses["response"].apply(lambda x: 1 if x > 0 else 0)

responses_graph_data = responses.merge(start_date, on='ID', how='left')
responses_graph_data = responses_graph_data.merge(receiver_country, on='ID', how='left')
responses_graph_data = responses_graph_data.merge(initiator_country, on='ID', how='left')
responses_graph_data = responses_graph_data.merge(incident_types, on='ID', how='left')
responses_graph_data = responses_graph_data.drop_duplicates()
responses_graph_data = responses_graph_data.merge(df_regions, how="left", on="ID").reset_index(drop=True)
responses_graph_data["receiver_region"] = responses_graph_data["receiver_region"].astype(str)
responses_graph_data.to_csv("/home/ubuntu/app_data/dashboard_responses_data.csv", index=False)

pol_graph_data[['country_type_response', 'response_type']] = pol_graph_data['political_response_type'].str.split(':', expand=True)
pol_graph_data['country_type_response'] = pol_graph_data['country_type_response'].str.strip()
pol_graph_data['response_type'] = pol_graph_data['response_type'].str.strip()
pol_response_type = pol_graph_data[['ID', 'country_type_response', 'response_type']]

legal_graph_data_sub = legal_graph_data[['ID', 'legal_response_type', 'legal_response_type_subcode']]
legal_graph_data_sub = legal_graph_data_sub.drop_duplicates()
legal_graph_data_sub['legal_response_type_clean'] = np.where(legal_graph_data_sub['legal_response_type_subcode'] == '', legal_graph_data_sub['legal_response_type'], legal_graph_data_sub['legal_response_type_subcode'])
legal_graph_data_sub = legal_graph_data_sub[['ID', 'legal_response_type_clean']]

responses_details = responses_graph_data.merge(pol_response_type, on='ID', how='left')
responses_details = responses_details.merge(legal_graph_data_sub, on='ID', how='left')

responses_details.to_csv("/home/ubuntu/app_data/dashboard_responses_details_data.csv", index=False)
