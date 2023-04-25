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

#This is how to access the tables.
political_responses = tables.political_responses.copy(deep=True)
attributions = tables.attributions_full_df.copy(deep=True)
legal_responses = tables.legal_responses.copy(deep=True)

attributions = attributions.fillna("")
attributions = attributions.replace("nan", "")
def replace_nat_with_empty_string(value):
    if pd.isnull(value):
        return ""
    return value
attributions = attributions.applymap(replace_nat_with_empty_string)

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

order_df = order_df.sort_values(by='added_to_DB', ascending=False)

order_df.to_csv("/Users/camille/Sync/PycharmProjects/stats_dashboard/app/data/eurepoc_dataset.csv", index=False)

from dash import html

incident = order_df.iloc[14].to_dict()
receiver_names = incident["receiver_name"].split('- ')
receiver_countries = incident['receiver_country'].split('; ')
receiver_categories = incident['receiver_category'].split('- ')
receiver_categories = [category.split('; ') for category in receiver_categories]
receiver_categories_subcodes = incident['receiver_category_subcode'].split('- ')
receiver_categories_subcodes = [subcode.split('; ') for subcode in receiver_categories_subcodes]
receivers_text = []
for i in range(len(receiver_countries)):
    elements = [
        html.Div([
            f"Receiver {i}",
            html.P([html.Span("Name: ", style={"font-weight": "bold"}), f"{receiver_names[i]}"]),
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
                html.P([html.Span("Sources URL: ", style={"font-weight": "bold"}), f"{incident['sources_url']}"]),
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


attr_date = df_reversed["attribution_date"][14].split('; ')
attr_type = df_reversed["attribution_type"][14].split('; ')


names = df['receiver_name'][933].split('- ')
names = [name.split('; ') for name in names]
countries = df['receiver_country'][933].split('; ')
categories = df['receiver_category'][933].split('- ')
categories = [category.split('; ') for category in categories]
subcodes = df['receiver_category_subcode'][933].split('- ')
subcodes = [subcode.split('; ') for subcode in subcodes]


for i in range(len(countries)):
    for y in range(len(categories[i])):
        print(f'''\
        {countries[i]}: {names[i]} - {categories[i]} - {subcodes[i]}''')


for i in range(len(names)):
    for y in range(len(categories[i])):
        print(f'''\
        {countries[i]}: {names[i]} - {categories[i][y]} - {subcodes[i][y]}''')
