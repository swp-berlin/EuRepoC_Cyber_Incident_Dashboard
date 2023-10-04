import numpy as np

response_true = responses_graph_data[responses_graph_data["response"] == 1]


pol_graph_data[['country_type_response', 'response_type']] = pol_graph_data['political_response_type'].str.split(':', expand=True)
pol_graph_data['country_type_response'] = pol_graph_data['country_type_response'].str.strip()
pol_graph_data['response_type'] = pol_graph_data['response_type'].str.strip()
pol_response_type = pol_graph_data[['ID', 'country_type_response', 'response_type']]

legal_graph_data_sub = legal_graph_data[['ID', 'legal_response_type', 'legal_response_type_subcode']]
legal_graph_data_sub = legal_graph_data_sub.drop_duplicates()
legal_graph_data_sub['legal_response_type_clean'] = np.where(legal_graph_data_sub['legal_response_type_subcode'] == '', legal_graph_data_sub['legal_response_type'], legal_graph_data_sub['legal_response_type_subcode'])
legal_graph_data_sub = legal_graph_data_sub[['ID', 'legal_response_type_clean']]

response_true_merge = response_true.merge(pol_response_type, on='ID', how='left')
response_true_merge = response_true_merge.merge(legal_graph_data_sub, on='ID', how='left')

response_true_merge_test = response_true_merge[response_true_merge["legal_response"]==1]
response_true_merge_test["ID"].nunique()

response_true_merge_test_pol = response_true_merge[response_true_merge["political_response"]==1]
response_true_merge_test_pol["ID"].nunique()

grouped_pol = response_true_merge_test_pol.groupby(['country_type_response', 'response_type']).agg(
    count=('ID', 'nunique')
).reset_index()
grouped_legal = response_true_merge_test.groupby(['legal_response_type_clean']).agg(
    count=('ID', 'nunique')
).reset_index()
grouped_legal = grouped_legal[grouped_legal['legal_response_type_clean'] != 'Not available']

total = grouped_pol.groupby('response_type')['count'].sum().reset_index()
total = total.rename(columns={'count': 'total'})

# Merge the total back to the original DataFrame
df = grouped_pol.merge(total, on='response_type')

# Sort the DataFrame based on the total
df = df.sort_values(by='total', ascending=False).reset_index(drop=True)

import plotly.express as px

fig = px.bar(grouped_pol, x="response_type", y="count", color="country_type_response", title="Long-Form Input")
fig.show()

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Title1', 'Title2'),
)

# Add traces for grouped_pol
# Assume you have three unique values in 'country_type_response': 'Type1', 'Type2', 'Type3'
# You can set specific colors for each type
colors = {'State Actors': 'blue', 'EU member states': 'green', 'EU': 'red', 'International organizations': 'yellow'}
for country_type in df['country_type_response'].unique():
    df2 = df[df['country_type_response'] == country_type]
    fig.add_trace(
        go.Bar(y=df2['response_type'], x=df2['count'], name=country_type, orientation='h', marker_color=colors[country_type]),
        row=1, col=1
    )

# Add trace for grouped_legal
fig.add_trace(
    go.Bar(y=grouped_legal['legal_response_type_clean'], x=grouped_legal['count'], name='Legal Response', orientation='h'),
    row=1, col=2
)

# Update layout
fig.update_layout(
    title_text="Horizontal Stacked Bar Charts",
    barmode='stack'  # for the first subplot
)

# Show figure
fig.show()