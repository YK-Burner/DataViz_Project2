import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, PathPatch
import matplotlib as mpl
import numpy as np 
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import os

#Taken from Project 1 
filename = 'finaldata1-3_Youllee_update_20260119.csv'
df = pd.read_csv(filename)

DF_civ_time= df[['civicengage1','civicengage2','civicengage3']]
DF_civ_time = DF_civ_time.dropna()
civ1_avg = np.mean(DF_civ_time['civicengage1'])
civ2_avg = np.mean(DF_civ_time['civicengage2'])
civ3_avg = np.mean(DF_civ_time['civicengage3'])

# Create DF fora  static figure of average civic engagement
avg_data = pd.DataFrame({
    'Wave': ['Wave 1', 'Wave 2', 'Wave 3'],
    'Average Civic Engagement': [civ1_avg, civ2_avg, civ3_avg]
})


if 'gender' in df.columns:
    df['gender_label'] = df['gender'].map({1: 'Male', 2: 'Female'}).fillna('Other')
else:
    df['gender_label'] = 'Unknown'

# --- App Initialization ---
app = dash.Dash(__name__)
server = app.server 

#Setting up the div 
#Taken from google and stack overflow. Updated with correct fields
app.layout = html.Div([
    html.H1("Survey Data Interactive Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # Control Panel Row
    html.Div([
        # X-Axis Dropdown
        html.Div([
            html.Label("Select X-Axis Variable:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='xaxis-column',
                options=[
                    {'label': 'Age', 'value': 'age'},
                    {'label': 'Socioeconomic Status (SES)', 'value': 'ses'},
                    {'label': 'Political Orientation', 'value': 'poli'},
                    {'label': 'Affective Polarization (Wave 1)', 'value': 'affectpol1'},
                    {'label': 'Media Source TV percentage', 'value': 'media1_tv_perc2'},
                    {'label': 'Media Source newspaper percentage', 'value': 'media2_newspaper_perc2'},
                    {'label': 'Media Source youtube percentage', 'value': 'media4_youtube_perc2'},
                    {'label': 'Media Source Community percentage', 'value': 'media5_community_perc2'},
                    
                ],
                value='age',
                clearable=False
            )
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Y-Axis Dropdown
        html.Div([
            html.Label("Select Y-Axis Variable:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='yaxis-column',
                options=[
                    {'label': 'Civic Engagement (Wave 1)', 'value': 'civicengage1'},
                    {'label': 'Civic Engagement (Wave 2)', 'value': 'civicengage2'},
                    {'label': 'Civic Engagement (Wave 3)', 'value': 'civicengage3'},
                ],
                value='civicengage1',
                clearable=False
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px'}),

    # Include first graph. Call back function to be included below
    dcc.Graph(id='scatter-plot', style={'marginTop': '20px'}),

    # Gender check button filter (not radio buttons, but this worked better for the data)
    #
    html.Div([
        html.Label("Filter by Gender:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Checklist(
            id='gender-filter',
            options=[
                {'label': ' Male', 'value': 'Male'},
                {'label': ' Female', 'value': 'Female'}
            ],
            value=['Male', 'Female'],
            inline=True,
            inputStyle={"margin-right": "5px", "margin-left": "10px"}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),

# hard line to seperate the plots. I think this makes it look a bit better
    html.Hr(),

#Div for the Demographics Histogram. I am copy pasting the same layout as before and updating for the hist
    html.Div([
        html.H3("Study Demographics", style={'textAlign': 'center'}),
        html.Div([
            html.Label("Select Variable:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='histogram-column',
                options=[
                    {'label': 'Age', 'value': 'age'},
                    {'label': 'Socioeconomic Status (SES)', 'value': 'ses'},
                    {'label': 'Political Orientation', 'value': 'poli'}
                ],
                value='age',
                clearable=False
            )
        ], style={'width': '40%', 'margin': '0 auto', 'padding': '10px'}),
        dcc.Graph(id='histogram-plot')
    ], style={'padding': '20px', 'marginTop': '20px'}),

    html.Hr(),
# Static plot. This is mostly just taken from project 1 
    html.Div([
        html.H3("Average Civic Engagement Over Time", style={'textAlign': 'center'}),
        dcc.Graph(
            id='avg-line-plot',
            figure=px.line(avg_data, x='Wave', y='Average Civic Engagement', markers=True)
        )
    ], style={'padding': '20px'})
])

# --- Callbacks ---
# most of this formating is pulled from stack overflow or google
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('gender-filter', 'value')]
)
def update_graph(xaxis_col, yaxis_col, selected_genders):
    # Filter the dataframe based on selected genders
    filtered_df = df[df['gender_label'].isin(selected_genders)]

    # Scatter Plot
    fig = px.scatter(
        filtered_df,
        x=xaxis_col,
        y=yaxis_col,
        color='gender_label',
        hover_data=['ID', 'age', 'gender'],
        title=f"Correlation: {xaxis_col} vs {yaxis_col}",
       
        opacity=0.7
    )

    fig.update_layout(
        margin={'l': 40, 'b': 40, 't': 40, 'r': 0},
        hovermode='closest',
        legend_title_text='Gender'
    )

    return fig

@app.callback(
    Output('histogram-plot', 'figure'),
    [Input('histogram-column', 'value'),
     Input('gender-filter', 'value')]
)
# Again most of this formating is pulled from stack overflow or google
def update_histogram(column, selected_genders):
    filtered_df = df[df['gender_label'].isin(selected_genders)]
    
    fig = px.histogram(
        filtered_df,
        x=column,
        color='gender_label',
        title=f"Distribution of {column}",
        labels={'gender_label': 'Gender'},
        opacity=0.7
    )
    fig.update_layout(bargap=0.1)
    return fig

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)