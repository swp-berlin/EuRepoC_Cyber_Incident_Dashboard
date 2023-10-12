from dash import html
from dash.exceptions import PreventUpdate
from dash import callback_context as ctx
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd


def clear_selected_click_data_callback(app, output_id=None, output_component_property=None, input_id=None):
    @app.callback(
        Output(output_id, output_component_property),
        Input(input_id, "n_clicks"),
        Input('receiver_country_dd', 'value'),
        Input('initiator_country_dd', 'value'),
        Input('incident_type_dd', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
    )
    def clear_click_data(
            n_clicks,
            receiver_country_filter,
            initiator_country_filter,
            incident_type_filter,
            start_date_filter,
            end_date_filter
    ):

        if not ctx.triggered:
            # This means the callback has not been triggered yet (initial load)
            raise PreventUpdate
        else:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'receiver_country_dd':
                n_clicks = 1
            if trigger_id == 'initiator_country_dd':
                n_clicks = 1
            if trigger_id == 'incident_type_dd':
                n_clicks = 1
            if trigger_id == 'date-picker-range':
                n_clicks = 1
        if n_clicks:
            return None


def clear_active_cell_datatables_callback(app, output_id=None, input_component_property=None, input_id=None):
    @app.callback(
        Output(output_id, 'active_cell'),
        Output(output_id, 'derived_virtual_data'),
        Input('receiver_country_dd', 'value'),
        Input(input_id, input_component_property)
    )
    def clear_active_cell(receiver_country_filter, clickData):
        return None, None


def format_receiver_categories(receiver_categories, receiver_categories_subcodes):
    return [f"{cat} - {subcode}" if cat and subcode and len(subcode) > 2 and subcode != "Not available" else "Not available" if cat is None else cat for cat, subcode in zip(receiver_categories, receiver_categories_subcodes)]


def format_attributed_initiators(initiator_name, initiator_country, initiator_category):
    if initiator_name is None:
        initiator_name = ["Not available"]
    if initiator_country is None:
        initiator_country = ["Not available"]
    if initiator_category is None:
        initiator_category = ["Not available"]

    components = []
    for name, country, cat in zip(initiator_name, initiator_country, initiator_category):
        components.extend([
           html.Span("Name: ", style={"padding-left": "24px", "font-weight": "bold"}),
           html.Span(f"{name}"),
           html.Br(),
           html.Span("Country: ", style={"padding-left": "24px", "font-weight": "bold"}),
           html.Span(f"{country}"),
           html.Br(),
           html.Span("Type: ", style={"padding-left": "24px", "font-weight": "bold"}),
           html.Span(f"{cat}"),
           html.Br(),
           html.Br()
        ])

    return components


def get_receiver_details(receiver_countries):
    receivers_text = []
    for i, receiver in enumerate(receiver_countries):
        cats = format_receiver_categories(receiver['receiver_category'], receiver['receiver_category_subcode'])
        elements = [
            html.Div([
                dbc.Card([
                    dbc.CardHeader([
                        html.P(f"Receiver {i + 1}", style={"font-weight": "bold"}),
                    ]),
                    dbc.CardBody([
                        html.P([html.Span("Name: ", style={"font-weight": "bold"}), f"{receiver['receiver_name']}"]),
                        html.P([html.Span("Country: ", style={"font-weight": "bold"}), f"{receiver['receiver_country']}"]),
                        html.P(f"Category(ies): ", style={"font-weight": "bold"}),
                        *[html.P([f"{cat}"]) for cat in cats],
                    ])
                ])
            ], style={"margin-bottom": "10px"})
        ]
        receivers_text += elements
    return receivers_text


def get_attribution_details(
        attributions
):
    attribution_text = []
    for i, attribution in enumerate(attributions):
        initiators = format_attributed_initiators(attribution['attributed_initiator_name'], attribution['attributed_initiator_country'], attribution['attributed_initiator_category'])
        elements = [
            html.Div([
                dbc.Card([
                    dbc.CardHeader([
                        html.P(f"Attribution {i + 1}", style={"font-weight": "bold"}),
                    ]),
                    dbc.CardBody([
                        html.P([html.Span("Attribution date: ", style={"font-weight": "bold"}), f"{attribution['attribution_full_date'][0]}"]),
                        html.P([html.Span("Attribution basis: ", style={"font-weight": "bold"}),
                                f"{'; '.join(attribution['attribution_basis'])}"]),
                        html.P([html.Span("Attribution type: ", style={"font-weight": "bold"}),
                                f"{'; '.join(attribution['attribution_type'])}"]),
                        html.P([html.Span("Attributing actor: ", style={"font-weight": "bold"}),
                                f"{'; '.join(attribution['attributing_actor'])}"]),
                        html.P([html.Span("Attributing country: ", style={"font-weight": "bold"}),
                                f"{'; '.join(attribution['attributing_country'])}"]),
                        html.P(f"Attributed initiator(s): ", style={"font-weight": "bold"}),
                        *initiators,
                    ])
                ])
            ], style={"margin-bottom": "10px"})
        ]
        attribution_text += elements
    return attribution_text


def get_responses_details(
        responses,
        label,
        dict_label
):
    response_text = []
    for i, response in enumerate(responses):
        elements = [
            html.Div([
                dbc.Card([
                    dbc.CardHeader([
                        html.P(f"{label} response {i + 1}", style={"font-weight": "bold"}),
                    ]),
                    dbc.CardBody([
                        html.P([html.Span("Response date: ", style={"font-weight": "bold"}), f"{response[f'{dict_label}_full_date'][0]}"]),
                        html.P([html.Span("Country of response: ", style={"font-weight": "bold"}),
                                f"{'; '.join(response[f'{dict_label}_country'])}"]),
                        html.P([html.Span("Type of actor responding: ", style={"font-weight": "bold"}),
                                f"{'; '.join(response[f'{dict_label}_actor'])}"]),
                        html.P([html.Span("Type of response: ", style={"font-weight": "bold"}),
                                f"{'; '.join(response[f'{dict_label}_type'])}"]),
                        html.P([html.Span("Sub-type of response: ", style={"font-weight": "bold"}),
                                f"{'; '.join(response[f'{dict_label}_type_sub'])}"]),
                    ])
                ])
            ], style={"margin-bottom": "10px"})
        ]
        response_text += elements
    return response_text



def create_modal_text(data=None, index=None, derived_virtual_data=None, active_cell=None, page_current=None, is_open=None):
    if active_cell is None:
        return is_open, None
    else:
        row_on_current_page = active_cell['row'] + (page_current) * 12
        incident_id = pd.DataFrame(derived_virtual_data).iloc[row_on_current_page].to_dict()
        incident = data[index[int(incident_id['ID'])]]

        sources_url_text = [
            html.Ul([
                html.Li(html.A(source, href=source, target="_blank"))
            ]) for source in incident['sources_url']]

        receivers_text = get_receiver_details(incident['receivers'])

        attribution_text = get_attribution_details(
           incident['attributions']
        )

        if incident["number_of_political_responses"] == 0:
            pol_response_text = []
        else:
            pol_response_text = get_responses_details(
            incident['political_responses'], "Political", "political_response"
        )

        if incident["number_of_legal_responses"] == 0:
            leg_response_text = []
        else:
            leg_response_text = get_responses_details(
                incident['legal_responses'], "Legal", "legal_response"
            )

        initiator_names = incident['initiator_name']
        initiator_names = filter(None, initiator_names)  # This filters out None values
        initiator_displayed_names = '; '.join(set(initiator_names)) if initiator_names else "Not available"

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
                                 f"{'; '.join(list(set(incident['incident_type'])))}"]),
                         html.P([html.Span("Source Incident Detection Disclosure: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['source_incident_detection_disclosure'])))}"]),
                         html.P([html.Span("Inclusion Criteria: ", style={"font-weight": "bold"}),
                                 f"{'<br>'.join(incident['inclusion_criteria'])}"]),
                         html.P(
                             html.Details([
                                 html.Summary("Sources (URLs):", style={"font-weight": "bold"}),
                                 html.Span([sources_url_text[i] for i in range(len(sources_url_text))])
                             ])
                         ),
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
                        [html.P([html.Span(f"Initiator Name: ", style={"font-weight": "bold"}),
                                 initiator_displayed_names]),
                            html.P([html.Span(f"Initiator Country: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(set(incident['initiator_country']))}"]),
                         html.P([html.Span(f"Initiator Category: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(set(incident['initiator_category']))}"]),
                         html.P([html.Span(f"Initiator Category Subcode: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(set(incident['initiator_category_subcode']))}"])],
                        title="Initator(s)"
                    ),
                    dbc.AccordionItem(
                        [attribution_text[i] for i in range(len(attribution_text))],
                        title="Attribution(s)"
                    ),
                    dbc.AccordionItem([
                       html.P([html.Span("Overall impact score: ", style={"font-weight": "bold"}),
                                 f"{incident['impact_indicator']} - {incident['impact_indicator_value']}"]),
                         html.P([
                             html.Span("↳"),
                             html.Span([
                                 html.Span("Functional impact: ", style={"font-weight": "bold"}),
                                 f"{incident['functional_impact']}"
                             ], style={"padding-left": "10px"})
                         ]),
                         html.P([html.Span("Intelligence impact: ", style={"font-weight": "bold"}),
                                 f"{incident['intelligence_impact']}"], style={"padding-left": "24px"}),
                         html.P([html.Span("Political impact (Affected entities): ", style={"font-weight": "bold"}),
                                 f"{incident['political_impact_affected_entities']}"], style={"padding-left": "24px"}),
                         html.P([html.Span("Political impact (Third countries): ", style={"font-weight": "bold"}),
                                 f"{incident['political_impact_third_countries']}"], style={"padding-left": "24px"}),
                         html.P([html.Span("Economic impact: ", style={"font-weight": "bold"}),
                                 f"{incident['economic_impact']}"], style={"padding-left": "24px"})
                    ], title="Impact Indicator"),
                    dbc.AccordionItem(
                        [html.P(
                            [html.Span("Data theft: ", style={"font-weight": "bold"}),
                             f"{'; '.join(list(set(incident['data_theft'])))}"]),
                            html.P(
                                [html.Span("Disruption: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['disruption'])))}"]),
                            html.P(
                                [html.Span("Hijacking: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['hijacking'])))}"]),
                            html.P([html.Span("Physical effects (Temporal): ", style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['physical_effects_temporal'])))}"]),
                            html.P([html.Span("Physical effects (Spatial): ", style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['physical_effects_spatial'])))}"]),
                            html.P([html.Span("Unweighted Cyber Intensity: ", style={"font-weight": "bold"}),
                                    f"{incident['unweighted_cyber_intensity']}"]),
                            html.P([html.Span("Target/Effect multiplier: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['target_multiplier'])))}"]),
                            html.P([html.Span("Weighted Cyber Intensity: ", style={"font-weight": "bold"}),
                                    f"{incident['weighted_cyber_intensity']}"]),
                            html.P([html.Span("MITRE-Initial Access: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['MITRE_initial_access'])))}"]),
                            html.P([html.Span("MITRE-Impact: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['MITRE_impact'])))}"]),
                            html.P([html.Span("Common Vulnerability Scoring System-User Interaction: ",
                                              style={"font-weight": "bold"}),
                                    f"{'; '.join(list(set(incident['user_interaction'])))}"]),
                            html.P(
                                [html.Span("Zero day: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['zero_days'])))}"])],
                        title="Technical Categories"
                    ),
                    dbc.AccordionItem(
                        [html.P([html.Span("Cyber conflict issue: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['cyber_conflict_issue'])))}"]),
                         html.P([html.Span("Offline conflict issue: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['offline_conflict_issue'])))}"]),
                         html.P([html.Span("Offline conflict name: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['offline_conflict_issue_subcode'])))}"]),
                         html.P([html.Span("Online conflict intensity: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['offline_conflict_intensity'])))}"]),
                         html.P([html.Span("Offline conflict intensity score: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['offline_conflict_intensity_subcode'])))}"]),
                         html.P(
                             [html.Span("Casualties: ", style={"font-weight": "bold"}),
                              f"{'; '.join(list(set(incident['casualties'])))}"]),
                         html.P([html.Span("Number of political responses: ", style={"font-weight": "bold"}),
                                 f"{incident['number_of_political_responses']}"]),
                         html.Div([pol_response_text[i] for i in range(len(pol_response_text))])],
                        title="Political Categories"
                    ),
                    dbc.AccordionItem(
                        [html.P([html.Span("State Responsibility Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['state_responsibility_indicator'])))}"]),
                         html.P([html.Span("IL Breach Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['IL_breach_indicator'])))}"]),
                         html.P([html.Span("Evidence for Sanctions Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(list(set(incident['evidence_for_sanctions_indicator'])))}"]),
                         html.P([html.Span("Number of legal responses: ", style={"font-weight": "bold"}),
                                 f"{incident['number_of_legal_responses']}"]),
                         html.Div([leg_response_text[i] for i in range(len(leg_response_text))])],
                        title="Legal Categories"
                    ),
                ], start_collapsed=True,
            )
        ])
        return True, content
