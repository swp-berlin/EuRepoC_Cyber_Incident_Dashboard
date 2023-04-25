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
        Input('receiver_country_dd', 'value'),
        Input(input_id, input_component_property)
    )
    def clear_active_cell(receiver_country_filter, clickData):
        return None


def create_modal_text(data=None, active_cell=None, page_current=None, is_open=None):
    if active_cell is None:
        return is_open, None

    else:
        row_on_current_page = active_cell['row'] + (page_current) * 12
        incident = data.iloc[row_on_current_page].to_dict()

        if incident["receiver_name"] is not None:
            receiver_names = incident["receiver_name"].split('- ')
        else:
            receiver_names = ["Unknown"]
        receiver_countries = incident['receiver_country'].split('; ')
        receiver_categories = incident['receiver_category'].split('- ')
        receiver_categories = [category.split('; ') for category in receiver_categories]
        if incident['receiver_category_subcode'] is not None:
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
                         html.P([html.Span("Sources URL: ", style={"font-weight": "bold"}),
                                 f"{incident['sources_url']}"]),
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
