from dash import dcc, html
import dash_bootstrap_components as dbc
from layout.layout_functions import (
    create_table, CONFIG, generate_intensity_popover,
    generate_text_with_popover_icon, generate_incident_details_modal, generate_key_insights_layout,
    generate_datatable_details_layout,
)


modal_types = generate_incident_details_modal(modal_body_id="modal_types_content", modal_id="modal_types")


data_theft_popover = dbc.Popover(
    "Incidents initiated to gather information from a targeted computer or computer system. Although data or \
    information is not “lost” for the target - it still possesses it - the data is no longer confidential. \
    If state actors are involved, it is regularly called “Cyber Espionage.”",
    target="data_theft_info",
    body=True,
    trigger="hover",
)

data_theft_doxing_popover = dbc.Popover(
    "Additionally to the ‘theft’ of data, the attacker(s) leak(s) the stolen information to the public.",
    target="data_theft_doxing_info",
    body=True,
    trigger="hover",
)

disruption_popover = dbc.Popover(
    "Incidents that negatively impact the functioning of the targeted systems, with potentially disruptive effects \
    on connected physical systems. Examples include DDoS attacks, defacements and wiper attacks.",
    target="disruption_info",
    body=True,
    trigger="hover",
)

hijacking_with_misuse_popover = dbc.Popover(
    "Incidents where the attacker penetrates or takes over the attacked system(s), \
    gaining deeper administrative rights, and some abuse of these rights has been observed \
    - e.g. data theft and/or disruption.",
    target="hijacking_misuse_info",
    body=True,
    trigger="hover",
)

hijacking_without_misuse_popover = dbc.Popover(
    "Incidents where the attacker penetrates or takes over the attacked system(s), \
    gaining deeper administrative rights, but no obvious abuse of these rights has been observed so far.",
    target="hijacking_without_misuse_info",
    body=True,
    trigger="hover",
)

ransomware_popover = dbc.Popover(
    "Ransomware is a type of malicious software (malware) that encrypts the victim's files. \
    The attacker then demands a ransom from the victim to restore access to the data upon payment.",
    target="ransomware_info",
    body=True,
    trigger="hover",
)

mean_intensity_types_popover = generate_intensity_popover(target_id="mean_intensity_types_info")
mean_intensity_types_popover_icon = generate_text_with_popover_icon(
    text="Mean intensity", span_id="mean_intensity_types_info", popover=mean_intensity_types_popover)


types_key_insights = generate_key_insights_layout(
    nb_incidents_id="nb_incidents_types",
    average_intensity_id="average_intensity_types",
    mean_intensity_popover_icon=mean_intensity_types_popover_icon,
    description_text_id="types_description_text",
    selected_item_id="types_selected",
    clear_click_data_id="clear_types_click_data",
)


types_incident_details_table = generate_datatable_details_layout(
    datatable_id="types_datatable",
    column_name="weighted_cyber_intensity",
    column_label="Weighted cyber intensity",
    modal_layout=modal_types,
)


types_tab = dbc.Container(
    dbc.Row([
        dbc.Row([
            dbc.Col([
                html.H3("What are the main types of cyber incidents?", style={'text-align': 'center'}),
            ], style={'margin': '20px'}),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id="types_title", style={"font-size": "1rem"}),
                        dcc.Graph(
                            id="types_graph",
                            config={
                                **CONFIG,
                            },
                            style={'height': '450px'}
                        )
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(204, 1, 48, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px'
                                        }
                                    ),
                                    " Data theft",
                                    html.I(
                                        id="data_theft_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    data_theft_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(0, 44, 56, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Data theft & doxing",
                                    html.I(
                                        id="data_theft_doxing_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    data_theft_doxing_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(137, 189, 158, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Disruption",
                                    html.I(
                                        id="disruption_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    disruption_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                        ], style={"text-align": "left"}),
                        dbc.Row([
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(132, 126, 137, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px'
                                        }
                                    ),
                                    " Hijacking with misuse",
                                    html.I(
                                        id="hijacking_misuse_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                            'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    hijacking_with_misuse_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(244, 185, 66, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Hijacking without misuse",
                                    html.I(
                                        id="hijacking_without_misuse_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                           'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    hijacking_without_misuse_popover
                                ], className="position-relative"),
                            ], lg=4, xl=4, xxl=4),
                            dbc.Col([
                                html.Span([
                                    html.I(
                                        className="fa-solid fa-circle",
                                        style={
                                            'font-size': '18px',
                                            'color': 'rgba(121, 68, 59, 0.7)',
                                            'display': 'inline-block',
                                            'margin-right': '5px',
                                        }
                                    ),
                                    " Ransomware",
                                    html.I(
                                        id="ransomware_info",
                                        className="fa-regular fa-circle-question",
                                        style={
                                           'text-align': 'center',
                                            'font-size': '12px',
                                            'color': '#002C38',
                                            'right': '-14px', 'top': '-2px',
                                            'position': 'absolute'
                                        }
                                    ),
                                    ransomware_popover
                                ], className="position-relative")
                            ], lg=4, xl=4, xxl=4)
                        ], style={"text-align": "left", "margin-top": "2px"}),
                    ], style={"padding-left": "50px"}),
                ], style={'margin-top': '15px'}),
            ], sm=12, xs=12, md=12, lg=9, xl=9, xxl=9),
            *types_key_insights,
        ]),
        *types_incident_details_table
    ])
)
