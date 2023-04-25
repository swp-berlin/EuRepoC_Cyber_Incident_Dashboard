from dash import html, dash_table


def make_break(num_breaks):
    br_list = [html.Br()] * num_breaks
    return br_list


def create_table(table_id=None, column_name="incident_type", column_label="Incident type"):
    datatable = dash_table.DataTable(
        id=table_id,
        data=[],
        columns=[
            {'name': 'Name (click an incident to display more info)', 'id': 'name'},
            {'name': 'Start date', 'id': 'start_date'},
            {"name": column_label, 'id': column_name}
        ],
        sort_action="native",
        sort_mode="multi",
        page_action="native",
        page_current=0,
        page_size=12,
        style_cell={
            'whiteSpace': 'nowrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0
        },
        tooltip_data=[],
        tooltip_duration=None,
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'font-family': 'var(--bs-font-sans-serif)'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(220, 220, 220, 0.3)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'font-family': 'var(--bs-font-sans-serif)'

        }
    )
    return datatable
