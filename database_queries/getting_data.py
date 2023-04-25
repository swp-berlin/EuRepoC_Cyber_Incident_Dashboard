from EuRepoC.query_database import query_database, QueryDatabase, get_token
from EuRepoC.cleaning_functions import clean_incidents
from EuRepoC.tables import TablesAll
import pandas as pd


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

# merge data
merged_data = receiver_country.merge(start_date, how="outer", on="ID")
merged_data = merged_data.merge(initiator_country, how="outer", on="ID")
merged_data = merged_data.merge(initiator_name, how="outer", on="ID")
merged_data = merged_data.merge(weighted_cyber_intensity, how="outer", on="ID")

merged_data = merged_data.drop_duplicates()

states_code = pd.read_excel(
    "/Users/camille/Sync/PycharmProjects/stats_dashboard/database_queries/states.xlsx",
    sheet_name="Sheet1"
)

map_data = states_code.merge(merged_data, how="left", on="receiver_country")
map_data["ID"] = map_data["ID"].fillna("NO_ID")
map_data["weighted_cyber_intensity"] = map_data["weighted_cyber_intensity"].fillna(0)
map_data.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_map_data.csv", index=False)

# Evolution of cyber incidents
start_date["start_date"] = pd.to_datetime(start_date["start_date"])
start_date["year"] = start_date["start_date"].dt.year
start_date["month"] = start_date["start_date"].dt.month

evolution_merged = receiver_country.merge(start_date, how="left", on="ID")
evolution_merged = evolution_merged.merge(initiator_country, how="left", on="ID")
evolution_merged = evolution_merged.drop_duplicates()
evolution_merged = evolution_merged.merge(df_regions, how="left", on="ID").reset_index(drop=True)
evolution_merged["receiver_region"] = evolution_merged["receiver_region"].astype(str)
evolution_merged.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_evolution_data.csv", index=False)

# Types of incidents
incident_types = tables.incident_type.copy(deep=True)
types_full_data = incident_types.merge(weighted_cyber_intensity, how="outer", on="ID")
types_full_data = types_full_data.merge(start_date, how="outer", on="ID")
types_full_data = types_full_data.merge(receiver_country, how="outer", on="ID")
types_full_data = types_full_data.merge(initiator_country, how="outer", on="ID")
types_full_data = types_full_data.drop_duplicates()
types_full_data = types_full_data.merge(df_regions, how="outer", on="ID")
types_full_data["receiver_region"] = types_full_data["receiver_region"].astype(str)
types_full_data["weighted_cyber_intensity"] = pd.to_numeric(types_full_data["weighted_cyber_intensity"])
types_full_data.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_incident_types_data.csv", index=False)

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

conflict_issues_full_data.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_conflict_issues_data.csv", index=False)

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
inclusion_full_data = inclusion_full_data.drop_duplicates()
inclusion_full_data = inclusion_full_data.merge(df_regions, how="outer", on="ID")
inclusion_full_data["receiver_region"] = inclusion_full_data["receiver_region"].astype(str)

inclusion_full_data["inclusion_criteria"] = inclusion_full_data["inclusion_criteria"].str.strip()  # Remove extra whitespaces

inclusion_full_data["inclusion_criteria"].replace({
    "Attack on (inter alia) political target(s), not politicized": "Attack on political target(s), not politicized",
    "Attack conducted by non-state group / non-state actor with political goals (religious, ethnic, etc. groups) / undefined actor with political goals": "Attack conducted by non-state group/actor with political goals",
    "Attack conducted by nation state (generic “state-attribution” or direct attribution towards specific state-entities, e.g., intelligence agencies)": "Attack conducted by nation state",
    "Attack on (inter alia) political target(s), politicized": "Attack on political target(s), politicized",
}, inplace=True)

# Drop NaN values if present
inclusion_full_data.dropna(subset=["inclusion_criteria"], inplace=True)

inclusion_full_data["inclusion_criteria_subcode"].replace({
    "Attack conducted by a state-affiliated group (includes state-sanctioned, state-supported, state-controlled but officially non-state actors) (“cyber-proxies”) / a group that is generally attributed as state-affiliated ": "Attack conducted by a state-affiliated group (“cyber-proxies”)",
}, inplace=True)

# Drop NaN values if present
inclusion_full_data.dropna(subset=["inclusion_criteria_subcode"], inplace=True)
inclusion_full_data.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_inclusion_data.csv", index=False)


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

network.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_network_data.csv", index=False)


# Targeted sectors
targeted_sectors = tables.receiver_category_full_table.copy(deep=True)
targeted_sectors = targeted_sectors.fillna("")
targeted_sectors = targeted_sectors.drop(columns=["receiver_name"])

targeted_sectors_full = start_date.merge(initiator_country, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.merge(targeted_sectors, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.merge(df_regions, how="outer", on="ID")
targeted_sectors_full = targeted_sectors_full.drop(columns=["receiver_region_x"])
targeted_sectors_full = targeted_sectors_full.rename(columns={"receiver_region_y": "receiver_region"})
targeted_sectors_full["receiver_region"] = targeted_sectors_full["receiver_region"].astype(str)

targeted_sectors_full["receiver_category"].replace({"Corporate Targets (corporate targets only coded if the respective company is not part of the critical infrastructure definition)": "Corporate Targets"}, inplace=True)

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

targeted_sectors_full.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/dashboard_targeted_sectors_data.csv", index=False)
