from dash import html, dash_table
import dash_bootstrap_components as dbc


# Prdefined columns for incident detail tables
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


# Function to create the incident detail tables
def create_table(
        table_id=None,
        column_name="incident_type",
        column_label="Incident type",
        column_name_2=None,
        column_label_2=None,
        column_name_3=None,
        column_label_3=None,
):
    """Generate a dash datatable with specified columns."""
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
        sort_mode="single",
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
            'font-family': 'var(--bs-font-sans-serif)',
            'border': '0.5px solid var(--bs-border-color-translucent)',
        },
        style_data_conditional=[
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


# Function to create a specified number of line breaks (used for formatting)
def make_break(num_breaks):
    """Return a list containing a specified number of line breaks."""
    br_list = [html.Br()] * num_breaks
    return br_list


# Configurations for the graphs - disabling the zoom and scroll
CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    'responsive': True
}

# Function to generate the popover explaining the "Cyber Intensity Indicator"
def generate_intensity_popover(target_id=None):
    return dbc.Popover(
        [
            dbc.PopoverBody([
                "Our Cyber Intensity Indicator assesses each cyber incident, based on its physical effects \
                and socio-political severity, with scores ranging from 1-15. The figure presented here represents the \
                average score for all cyber incidents corresponding to your selection. \
                For more information on the methodology see ",
                html.A("here", href="https://www.eurepoc.eu/methodology", target="_blank"),
                "."
            ]),
        ],
        target=target_id,
        trigger="hover",
    )


# Function to create the i icon with the popover
def generate_text_with_popover_icon(text=None, span_id=None, popover=None):
    text_span = html.Span([
        text,
        html.I(
            id=span_id,
            className="fa-regular fa-circle-question",
            style={
                'text-align': 'center',
                'font-size': '12px',
                'color': '#002C38',
                'right': '-14px', 'top': '-2px',
                'position': 'absolute'
            },
        ),
        popover,
    ], className="position-relative")
    return text_span


def generate_incident_details_modal(modal_body_id=None, modal_id=None):
    return dbc.Modal([
        dbc.ModalHeader(html.H3('Incident details')),
        dbc.ModalBody(id=modal_body_id),
    ], id=modal_id, size='xl', centered=True, scrollable=True)
