from dash import html, dash_table
import json

column_names = [
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
    'zero_days', 'zero_days_subcode',
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
    'political_impact_third_countries',
    'economic_impact',
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


def make_break(num_breaks):
    br_list = [html.Br()] * num_breaks
    return br_list


def create_table(
        table_id=None,
        column_name="incident_type",
        column_label="Incident type",
        column_name_2=None,
        column_label_2=None,
        column_name_3=None,
        column_label_3=None,
):
    base_columns = [
        {'name': 'ID', 'id': 'ID'},
        {'name': 'Incident name', 'id': 'name'},
        {'name': 'Start date', 'id': 'start_date'},
        {"name": column_label, 'id': column_name},
    ]

    additional_columns = []

    if column_name_2 is not None:
        additional_columns.append({"name": column_label_2, 'id': column_name_2})

    if column_name_3 is not None:
        additional_columns.append({"name": column_label_3, 'id': column_name_3})

    columns = base_columns + additional_columns

    datatable = dash_table.DataTable(
        id=table_id,
        data=[],
        columns=columns,
        hidden_columns=["ID"],
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=12,
        style_cell={
            'whiteSpace': 'nowrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,
            'padding': '8px',
        },
        tooltip_data=[],
        tooltip_duration=None,
        style_data={
            'color': 'black',
            #'backgroundColor': 'rgb(230, 234, 235)',
            'font-family': 'var(--bs-font-sans-serif)',
            'border': '0.5px solid var(--bs-border-color-translucent)',
        },
        style_data_conditional=[
            #{
                #'if': {'row_index': 'odd'},
               # 'backgroundColor': 'rgb(204, 213, 215)',
            #}
            {
                'if': {'state': 'active'},
                'backgroundColor': '#f5ccd6',
                'border': '1px solid #cc0130'
            },
        ],
        style_header={
            'backgroundColor': 'rgb(230, 234, 235)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'var(--bs-font-sans-serif)',
            'border': '0.5px solid var(--bs-border-color-translucent)',
        },
        #style_as_list_view=True,
        css=[
            {
                'selector': '.dbc .previous-page:hover, .first-page:hover, .next-page:hover',
                'rule': 'color: #cc0130 !important;'
            },
            {
                'selector': '.dbc .previous-next-container .last-page:hover',
                'rule': 'color: #cc0130 !important;'
            },
            {"selector": ".show-hide", "rule": "display: none"}
        ],
    )
    return datatable


CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    'responsive': True
}
