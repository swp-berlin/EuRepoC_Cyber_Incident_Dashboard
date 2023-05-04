from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd


def clear_selected_click_data_callback(app, output_id=None, output_component_property=None, input_id=None):
    @app.callback(
        Output(output_id, output_component_property),
        Input(input_id, "n_clicks")
    )
    def clear_click_data(n_clicks):
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
    return [
        f"Country: {country} - \
          Name: {name} - \
          Type: {cat}" for country, name, cat in zip(initiator_name, initiator_country, initiator_category)
    ]


def get_receiver_details(receiver_countries):
    receivers_text = []
    for i, receiver in enumerate(receiver_countries):
        cats = format_receiver_categories(receiver['receiver_category'], receiver['receiver_category_subcode'])
        elements = [
            html.Div([
                html.P(f"Receiver {i + 1}", style={"font-weight": "bold"}),
                html.P([html.Span("Name: ", style={"font-weight": "bold"}), f"{receiver['receiver_name']}"]),
                html.P([html.Span("Country: ", style={"font-weight": "bold"}), f"{receiver['receiver_country']}"]),
                html.P(f"Category(ies): ", style={"font-weight": "bold"}),
                *[html.P([f"{cat}"]) for cat in cats],
            ], style={
                "background-color": "#f3f2f3",
                "padding": "10px",
                "margin": "10px",
                "border-radius": "5px",
                "box-shadow": "2px 2px 2px #d6d6d6"
            })
        ]
        receivers_text += elements
    return receivers_text


def get_attribution_details(
        attributions
):
    attribution_text = []
    for i, attribution in enumerate(attributions):
        initiators = format_attributed_initiators(attribution['attributed_initiator_country'], attribution['attributed_initiator_name'], attribution['attributed_initiator_category'])
        elements = [
            html.Div([
                html.P(f"Attribution {i + 1}", style={"font-weight": "bold"}),
                html.P([html.Span("Attribution date: ", style={"font-weight": "bold"}), f"{attribution['attribution_year']}"]),
                html.P([html.Span("Attribution basis: ", style={"font-weight": "bold"}),
                        f"{'; '.join(attribution['attribution_basis'])}"]),
                html.P([html.Span("Attribution type: ", style={"font-weight": "bold"}),
                        f"{'; '.join(attribution['attribution_type'])}"]),
                html.P([html.Span("Attributing actor: ", style={"font-weight": "bold"}),
                        f"{'; '.join(attribution['attributing_actor'])}"]),
                html.P([html.Span("Attributing country: ", style={"font-weight": "bold"}),
                        f"{'; '.join(attribution['attributing_country'])}"]),
                html.P(f"Attributed initiator(s): ", style={"font-weight": "bold"}),
                *[html.P([f"{initiator}"]) for initiator in initiators],
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


def create_modal_text(data=None, index=None, derived_virtual_data=None, active_cell=None, page_current=None, is_open=None):
    if active_cell is None:
        return is_open, None
    else:
        row_on_current_page = active_cell['row'] + (page_current) * 12
        id = pd.DataFrame(derived_virtual_data).iloc[row_on_current_page].to_dict()
        incident = data[index[int(id['ID'])]]

        sources_url_text = [
            html.Ul([
                html.Li(html.A(source, href=source, target="_blank"))
            ]) for source in incident['sources_url']]

        #receiver_names = incident["receiver_name"].split('- ') if incident["receiver_name"] is not None and isinstance(incident['receiver_name'], str) else ["Unknown"]
        #receiver_countries = incident['receiver_country'].split('; ')
        #receiver_categories = [category.split('; ') for category in incident['receiver_category'].split('- ')]
        #receiver_categories_subcodes = [subcode.split('; ') for subcode in incident['receiver_category_subcode'].split('- ')] if incident['receiver_category_subcode'] and isinstance(incident['receiver_category_subcode'], str) else [[""] * len(sublist) for sublist in receiver_categories]

        #attribution_dates = incident['attribution_date'].split('; ') if incident['attribution_date'] and isinstance(incident['attribution_date'], str) else [""]
        #attribution_types = incident['attribution_type'].split('; ') if incident['attribution_type'] and isinstance(incident['attribution_type'], str) else [""]*len(attribution_dates)
        #attribution_basis = incident['attribution_basis'].split('; ') if incident['attribution_basis'] and isinstance(incident['attribution_basis'], str) else [""]*len(attribution_dates)
        #attributing_actors = incident['attributing_actor'].split('; ') if incident['attributing_actor'] and isinstance(incident['attributing_actor'], str) else [""]*len(attribution_dates)
        #attribution_it_companies = incident['attribution_it_company'].split('; ') if incident['attribution_it_company'] and isinstance(incident['attribution_it_company'], str) else [""]*len(attribution_dates)
        #attributing_countries = incident['attributing_country'].split('; ') if incident['attributing_country'] and isinstance(incident['attributing_country'], str) else [""]*len(attribution_dates)
        #attributed_initiators = incident['attributed_initiator'].split('; ') if incident['attributed_initiator'] and isinstance(incident['attributed_initiator'], str) else [""]*len(attribution_dates)
        #attributed_initiator_countries = incident['attributed_initiator_country'].split('; ') if incident['attributed_initiator_country'] and isinstance(incident['attributed_initiator_country'], str) else [""]*len(attribution_dates)
        #attributed_initiator_categories = incident['attributed_initiator_category'].split('; ') if incident['attributed_initiator_category'] and isinstance(incident['attributed_initiator_category'], str) else [""]*len(attribution_dates)

        receivers_text = get_receiver_details(incident['receivers'])

        attribution_text = get_attribution_details(
           incident['attributions']
        )

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
                            [html.Span("Data theft: ", style={"font-weight": "bold"}),
                             f"{'; '.join(incident['data_theft'])}"]),
                            html.P(
                                [html.Span("Disruption: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['disruption'])}"]),
                            html.P(
                                [html.Span("Hijacking: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['hijacking'])}"]),
                            html.P([html.Span("Physical effects (Temporal): ", style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['physical_effects_temporal'])}"]),
                            html.P([html.Span("Physical effects (Spatial): ", style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['physical_effects_spatial'])}"]),
                            html.P([html.Span("Unweighted Cyber Intensity: ", style={"font-weight": "bold"}),
                                    f"{incident['unweighted_cyber_intensity']}"]),
                            html.P([html.Span("Target/Effect multiplier: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['target_multiplier'])}"]),
                            html.P([html.Span("Weighted Cyber Intensity: ", style={"font-weight": "bold"}),
                                    f"{incident['weighted_cyber_intensity']}"]),
                            html.P([html.Span("MITRE-Initial Access: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['MITRE_initial_access'])}"]),
                            html.P([html.Span("MITRE-Impact: ", style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['MITRE_impact'])}"]),
                            html.P([html.Span("Common Vulnerability Scoring System-User Interaction: ",
                                              style={"font-weight": "bold"}),
                                    f"{'; '.join(incident['user_interaction'])}"]),
                            html.P(
                                [html.Span("Zero day: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['zero_days'])}"])],
                        title="Technical Categories"
                    ),
                    dbc.AccordionItem(
                        [html.P([html.Span("Cyber conflict issue: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['cyber_conflict_issue'])}"]),
                         html.P([html.Span("Offline conflict issue: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['offline_conflict_issue'])}"]),
                         html.P([html.Span("Offline conflict name: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['offline_conflict_issue_subcode'])}"]),
                         html.P([html.Span("Online conflict intensity: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['offline_conflict_intensity'])}"]),
                         html.P([html.Span("Offline conflict intensity score: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['offline_conflict_intensity_subcode'])}"]),
                         html.P(
                             [html.Span("Casualties: ", style={"font-weight": "bold"}),
                              f"{'; '.join(incident['casualties'])}"]),
                         html.P([html.Span("Number of political responses: ", style={"font-weight": "bold"}),
                                 f"{incident['number_of_political_responses']}"])],
                        title="Political Categories"
                    ),
                    dbc.AccordionItem(
                        [html.P([html.Span("State Responsibility Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['state_responsibility_indicator'])}"]),
                         html.P([html.Span("IL Breach Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['IL_breach_indicator'])}"]),
                         html.P([html.Span("Evidence for Sanctions Indicator: ", style={"font-weight": "bold"}),
                                 f"{'; '.join(incident['evidence_for_sanctions_indicator'])}"]),
                         html.P([html.Span("Number of legal responses: ", style={"font-weight": "bold"}),
                                 f"{incident['number_of_legal_responses']}"])],
                        title="Legal Categories"
                    ),
                ], start_collapsed=True,
            )
        ])
        return True, content



"""def create_modal_text(data=None, active_cell=None, page_current=None, is_open=None):
    if active_cell is None:
        return is_open, None

    else:
        row_on_current_page = active_cell['row'] + (page_current) * 12
        incident = data.iloc[row_on_current_page].to_dict()

        sources_url = incident['sources_url'].split('; ')
        sources_url_text = []
        for source in sources_url:
            sources_url_text.append(html.Ul([html.Li(html.A(source, href=source, target="_blank"))]))

        if incident["receiver_name"] is not None:
            receiver_names = incident["receiver_name"].split('- ')
        else:
            receiver_names = ["Unknown"]
        receiver_countries = incident['receiver_country'].split('; ')
        receiver_categories = incident['receiver_category'].split('- ')
        receiver_categories = [category.split('; ') for category in receiver_categories]
        if incident['receiver_category_subcode'] is not None \
            and incident['receiver_category_subcode'] != "" \
            and isinstance(incident['receiver_category_subcode'], str):
            receiver_categories_subcodes = incident['receiver_category_subcode'].split('- ')
        else:
            receiver_categories_subcodes = [""]
        receiver_categories_subcodes = [subcode.split('; ') for subcode in receiver_categories_subcodes]

        receivers_text = []
        for i in range(len(receiver_countries)):
            elements = [
                html.Div([
                    html.P(f"Receiver {i + 1}", style={"font-weight": "bold"}),
                    html.P([html.Span("Name: ", style={"font-weight": "bold"}), f"{receiver_names[i]}"]),
                    html.P([html.Span("Country: ", style={"font-weight": "bold"}), f"{receiver_countries[i]}"]),
                    *[html.P([html.Span(f"Category {y + 1}: ", style={"font-weight": "bold"}),
                              f"{receiver_categories[i][y]} - {receiver_categories_subcodes[i][y]}"]) for y in
                      range(len(receiver_categories[i]))]
                ], style={"background-color": "rgba(0, 0, 0, 0.05)", "padding": "10px", "margin": "10px"})
            ]
            receivers_text += elements

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
                                 f"{incident['incident_type']}"]),
                         html.P([html.Span("Source Incident Detection Disclosure: ", style={"font-weight": "bold"}),
                                 f"{incident['source_incident_detection_disclosure']}"]),
                         html.P([html.Span("Inclusion Criteria: ", style={"font-weight": "bold"}),
                                 f"{incident['inclusion_criteria']}"]),
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
                             [html.Span("Disruption: ", style={"font-weight": "bold"}), f"{incident['disruption']}"]),
                         html.P([html.Span("Hijacking: ", style={"font-weight": "bold"}), f"{incident['hijacking']}"]),
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
                         html.P([html.Span("Zero day: ", style={"font-weight": "bold"}), f"{incident['zero_days']}"])],
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
        return True, content
"""