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

# Clean data
all_database_incidents_clean_dict = clean_incidents_dict(all_incidents)
all_tracker_incidents_clean_dict = clean_incidents_dict(incidents_sent_to_tracker)

all_incidents_clean_dict = all_database_incidents_clean_dict
for incident in all_tracker_incidents_clean_dict:
    if incident not in all_incidents_clean_dict:
        all_incidents_clean_dict.append(incident)

df = pd.DataFrame(all_database_incidents_clean)

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



tables = TablesAll(all_database_incidents_clean)
tables.get_all_tables()

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

order_df.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/eurepoc_dataset.csv", index=False)


with open("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/full_data_dict.pickle", "wb") as file:
    pickle.dump(all_incidents_clean_dict, file)

full_data_dict_index_map = {}
for i in range(len(all_incidents_clean_dict)):
    full_data_dict_index_map[all_incidents_clean_dict[i]["ID"]] = i

with open("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/full_data_dict_index_map.pickle", "wb") as file:
    pickle.dump(full_data_dict_index_map, file)



from dash import html

incident = order_df.iloc[458].to_dict()

attribution_dates = incident['attribution_date'].split('; ')
attribution_types = incident['attribution_type'].split('; ')
attribution_basis = incident['attribution_basis'].split('; ')
attributing_actors = incident['attributing_actor'].split('; ')
attribution_it_companies = incident['attribution_it_company'].split('; ')
attributing_countries = incident['attributing_country'].split('; ')
attributed_initiators = incident['attributed_initiator'].split('; ')
attributed_initiator_countries = incident['attributed_initiator_country'].split('; ')
attributed_initiator_categories = incident['attributed_initiator_category'].split('; ')

def get_attribution_details(
        attribution_dates,
        attribution_types,
        attribution_basis,
        attributing_actors,
        attribution_it_companies,
        attributing_countries,
        attributed_initiators,
        attributed_initiator_countries,
        attributed_initiator_categories
):
    attribution_text = []
    for i in range(len(attribution_dates)):
        elements = [
            html.Div([
                html.P(f"Attribution {i + 1}", style={"font-weight": "bold"}),
                html.P([html.Span("Attribution date: ", style={"font-weight": "bold"}), f"{attribution_dates[i]}"]),
                html.P([html.Span("Attribution basis: ", style={"font-weight": "bold"}), f"{attribution_basis[i]}"]),
                html.P([html.Span("Attribution type: ", style={"font-weight": "bold"}), f"{attribution_types[i]}"]),
                html.P([html.Span("Attributing actor: ", style={"font-weight": "bold"}), f"{attributing_actors[i]}"]),
                html.P([html.Span("Attributing country: ", style={"font-weight": "bold"}), f"{attributing_countries[i]}"]),
                html.P([html.Span("Attributed initiator: ", style={"font-weight": "bold"}), f"{attributed_initiators[i]}"]),
                html.P([html.Span("Attributed initiator country: ", style={"font-weight": "bold"}), f"{attributed_initiator_countries[i]}"]),
                html.P([html.Span("Attributed initiator category: ", style={"font-weight": "bold"}), f"{attributed_initiator_categories[i]}"]),
            ], style={
                "background-color": "#f3f2f3",
                "padding": "10px",
                "margin": "10px",
                "border-radius": "5px",
                "box-shadow": "2px 2px 2px #d6d6d6"
            })
        ]
        attribution_text += elements
    return attribution_text

sources_attribution = incident["sources_attribution"].split('; ')





receiver_names = incident["receiver_name"].split('- ')
receiver_countries = incident['receiver_country'].split('; ')
receiver_categories = incident['receiver_category'].split('- ')
receiver_categories = [category.split('; ') for category in receiver_categories]
receiver_categories_subcodes = incident['receiver_category_subcode'].split('- ')
receiver_categories_subcodes = [subcode.split('; ') for subcode in receiver_categories_subcodes]
receivers_text = []

receiver_names = incident["receiver_name"].split('- ') if incident["receiver_name"] is not None else ["Unknown"]
receiver_countries = incident['receiver_country'].split('; ')
receiver_categories = [category.split('; ') for category in incident['receiver_category'].split('- ')]
receiver_categories_subcodes = [subcode.split('; ') for subcode in incident['receiver_category_subcode'].split('- ')] if incident['receiver_category_subcode'] and isinstance(incident['receiver_category_subcode'], str) else [[""]]


sources_url = incident['sources_url'].split('; ')
sources_url_text = []
for source in sources_url:
    sources_url_text.append(html.A(source, href=source, target="_blank"))



for incident in all_incidents_clean_dict:
    elements = [
        html.Div([
            f"Receiver {i}",
            html.P([html.Span("Name: ", style={"font-weight": "bold"}), f"{incident['name']}"]),
            html.P([html.Span("Country: ", style={"font-weight": "bold"}), f"{receiver_countries[i]}"]),
        ])
    ]
    for y in range(len(receiver_categories[i])):
        elements.append(html.P([html.Span("Category: ", style={"font-weight": "bold"}), f"{receiver_categories[i][y]}"]))
        elements.append(html.P([html.Span("Category Subcode: ", style={"font-weight": "bold"}), f"{receiver_categories_subcodes[i][y]}"]))
    receivers_text.append(elements)

content = html.Div([
    dbc.Accordion(
        [
            dbc.AccordionItem(
                html.P([html.Span("Name of incident: ", style={"font-weight": "bold"}), f"{incident['name']}"]),
                html.P([html.Span("Start Date: ", style={"font-weight": "bold"}), f"{incident['start_date']}"]),
                html.P([html.Span("End Date: ", style={"font-weight": "bold"}), f"{incident['end_date']}"]),
                html.P([html.Span("Incident Type: ", style={"font-weight": "bold"}), f"{incident['incident_type']}"]),
                html.P([html.Span("Source Incident Detection Disclosure: ", style={"font-weight": "bold"}), f"{incident['source_incident_detection_disclosure']}"]),
                html.P([html.Span("Inclusion Criteria: ", style={"font-weight": "bold"}), f"{incident['inclusion_criteria']}"]),
                html.P([
                    html.Span("Sources URL: ", style={"font-weight": "bold"}),
                    html.Span([sources_url_text[i] for i in receivers_text])
                ]),
                html.P([html.Span("Added to database: ", style={"font-weight": "bold"}), f"{incident['added_to_DB']}"]),
                html.P([html.Span("Last updated: ", style={"font-weight": "bold"}), f"{incident['updated_at']}"]),
                title="Key information about the incident"
            ),
            dbc.AccordionItem(
                [receivers_text[i] for i in receivers_text],
                title="Receiver(s)"
            ),
            dbc.AccordionItem(
                html.P([html.Span(f"Initiator Country: ", style={"font-weight": "bold"}), f"{incident['initiator_country']}"]),
                html.P([html.Span(f"Initiator Category: ", style={"font-weight": "bold"}), f"{incident['initiator_category']}"]),
                html.P([html.Span(f"Initiator Category Subcode: ", style={"font-weight": "bold"}), f"{incident['initiator_category_subcode']}"]),
                title="Initator(s)"
            ),
            dbc.AccordionItem(
                title="Attribution(s)"
            ),
            dbc.AccordionItem(
                html.P([html.Span("Impact indicator: ", style={"font-weight": "bold"}), f"{incident['impact_indicator']} - {incident['impact_indicator_value']}"]),
                html.P([html.Span("Functional impact: ", style={"font-weight": "bold"}), f"{incident['functional_impact']}"]),
                html.P([html.Span("Intelligence impact: ", style={"font-weight": "bold"}), f"{incident['intelligence_impact']}"]),
                html.P([html.Span("Political impact (Affected entities): ", style={"font-weight": "bold"}), f"{incident['political_impact_affected_entities']}"]),
                html.P([html.Span("Political impact (Third countries): ", style={"font-weight": "bold"}), f"{incident['political_impact_third_countries']}"]),
                html.P([html.Span("Economic impact: ", style={"font-weight": "bold"}), f"{incident['economic_impact']}"]),
                title="Impact Indicator"
            ),
            dbc.AccordionItem(
                title="Technical Categories"
            ),
            dbc.AccordionItem(
                title="Political Categories"
            ),
            dbc.AccordionItem(
                title="Legal Categories"
            ),
        ], flush=True,
    )
])

index_map = {}
for i in range(len(all_incidents_clean_dict)):
    index_map[all_incidents_clean_dict[i]["ID"]] = i

first_value = all_incidents_clean_dict[index_map[8]]

attr_date = df_reversed["attribution_date"][14].split('; ')
attr_type = df_reversed["attribution_type"][14].split('; ')

incident = all_incidents_clean_dict[14]

content = html.Div([
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [html.P([html.Span("Name of incident: ", style={"font-weight": "bold"}),
                         f"{incident['name']}"]),
                 html.P([html.Span("Description: ", style={"font-weight": "bold"}),
                         f"{incident['description']}"]),
                 html.P([html.Span("Start Date: ", style={"font-weight": "bold"}),
                         f"{incident['start_date']}"]),
                 html.P([html.Span("End Date: ", style={"font-weight": "bold"}), f"{incident['end_date']}"]),
                 html.P([html.Span("Incident Type: ", style={"font-weight": "bold"}),
                         f"{'; '.join(incident['incident_type'])}"]),
                 html.P([html.Span("Source Incident Detection Disclosure: ", style={"font-weight": "bold"}),
                         f"{'; '.join(incident['source_incident_detection_disclosure'])}"]),
                 html.P([html.Span("Inclusion Criteria: ", style={"font-weight": "bold"}),
                         f"{'<br>'.join(incident['inclusion_criteria'])}"]),
                 html.P([
                     html.Span("Sources URL: ", style={"font-weight": "bold"}),
                     html.Span([sources_url_text[i] for i in range(len(sources_url_text))])
                 ]),
                 html.P([html.Span("Added to database: ", style={"font-weight": "bold"}),
                         f"{incident['added_to_DB']}"]),
                 html.P([html.Span("Last updated: ", style={"font-weight": "bold"}),
                         f"{incident['updated_at']}"])],
                title="Key information about the incident"
            ),
            dbc.AccordionItem(
                [receivers_text[i] for i in range(len(receivers_text))],
                title="Receiver(s)"
            ),
            dbc.AccordionItem(
                [html.P([html.Span(f"Initiator Country: ", style={"font-weight": "bold"}),
                         f"{incident['initiator_country']}"]),
                 html.P([html.Span(f"Initiator Category: ", style={"font-weight": "bold"}),
                         f"{incident['initiator_category']}"]),
                 html.P([html.Span(f"Initiator Category Subcode: ", style={"font-weight": "bold"}),
                         f"{incident['initiator_category_subcode']}"])],
                title="Initator(s)"
            ),
            dbc.AccordionItem(
                [attribution_text[i] for i in range(len(attribution_text))],
                title="Attribution(s)"
            ),
            dbc.AccordionItem(
                [html.P([html.Span("Impact indicator: ", style={"font-weight": "bold"}),
                         f"{incident['impact_indicator']} - {incident['impact_indicator_value']}"]),
                 html.P([html.Span("Functional impact: ", style={"font-weight": "bold"}),
                         f"{incident['functional_impact']}"]),
                 html.P([html.Span("Intelligence impact: ", style={"font-weight": "bold"}),
                         f"{incident['intelligence_impact']}"]),
                 html.P([html.Span("Political impact (Affected entities): ", style={"font-weight": "bold"}),
                         f"{incident['political_impact_affected_entities']}"]),
                 html.P([html.Span("Political impact (Third countries): ", style={"font-weight": "bold"}),
                         f"{incident['political_impact_third_countries']}"]),
                 html.P([html.Span("Economic impact: ", style={"font-weight": "bold"}),
                         f"{incident['economic_impact']}"])],
                title="Impact Indicator"
            ),
            dbc.AccordionItem(
                [html.P(
                    [html.Span("Data theft: ", style={"font-weight": "bold"}), f"{incident['data_theft']}"]),
                    html.P(
                        [html.Span("Disruption: ", style={"font-weight": "bold"}),
                         f"{incident['disruption']}"]),
                    html.P(
                        [html.Span("Hijacking: ", style={"font-weight": "bold"}), f"{incident['hijacking']}"]),
                    html.P([html.Span("Physical effects (Temporal): ", style={"font-weight": "bold"}),
                            f"{incident['physical_effects_temporal']}"]),
                    html.P([html.Span("Physical effects (Spatial): ", style={"font-weight": "bold"}),
                            f"{incident['physical_effects_spatial']}"]),
                    html.P([html.Span("Unweighted Cyber Intensity: ", style={"font-weight": "bold"}),
                            f"{incident['unweighted_cyber_intensity']}"]),
                    html.P([html.Span("Target/Effect multiplier: ", style={"font-weight": "bold"}),
                            f"{incident['target_multiplier']}"]),
                    html.P([html.Span("Weighted Cyber Intensity: ", style={"font-weight": "bold"}),
                            f"{incident['weighted_cyber_intensity']}"]),
                    html.P([html.Span("MITRE-Initial Access: ", style={"font-weight": "bold"}),
                            f"{incident['MITRE_initial_access']}"]),
                    html.P([html.Span("MITRE-Impact: ", style={"font-weight": "bold"}),
                            f"{incident['MITRE_impact']}"]),
                    html.P([html.Span("Common Vulnerability Scoring System-User Interaction: ",
                                      style={"font-weight": "bold"}), f"{incident['user_interaction']}"]),
                    html.P(
                        [html.Span("Zero day: ", style={"font-weight": "bold"}), f"{incident['zero_days']}"])],
                title="Technical Categories"
            ),
            dbc.AccordionItem(
                [html.P([html.Span("Cyber conflict issue: ", style={"font-weight": "bold"}),
                         f"{incident['cyber_conflict_issue']}"]),
                 html.P([html.Span("Offline conflict issue: ", style={"font-weight": "bold"}),
                         f"{incident['offline_conflict_issue']}"]),
                 html.P([html.Span("Offline conflict name: ", style={"font-weight": "bold"}),
                         f"{incident['offline_conflict_issue_subcode']}"]),
                 html.P([html.Span("Online conflict intensity: ", style={"font-weight": "bold"}),
                         f"{incident['offline_conflict_intensity']}"]),
                 html.P([html.Span("Offline conflict intensity score: ", style={"font-weight": "bold"}),
                         f"{incident['offline_conflict_intensity_subcode']}"]),
                 html.P(
                     [html.Span("Casualties: ", style={"font-weight": "bold"}), f"{incident['casualties']}"]),
                 html.P([html.Span("Number of political responses: ", style={"font-weight": "bold"}),
                         f"{incident['number_of_political_responses']}"])],
                title="Political Categories"
            ),
            dbc.AccordionItem(
                [html.P([html.Span("State Responsibility Indicator: ", style={"font-weight": "bold"}),
                         f"{incident['state_responsibility_indicator']}"]),
                 html.P([html.Span("IL Breach Indicator: ", style={"font-weight": "bold"}),
                         f"{incident['IL_breach_indicator']}"]),
                 html.P([html.Span("Evidence for Sanctions Indicator: ", style={"font-weight": "bold"}),
                         f"{incident['evidence_for_sanctions_indicator']}"]),
                 html.P([html.Span("Number of legal responses: ", style={"font-weight": "bold"}),
                         f"{incident['number_of_legal_responses']}"])],
                title="Legal Categories"
            ),
        ], start_collapsed=True,
    )
])