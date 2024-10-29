#-------------------------------------------------------------------------------
# Project 2
# Author: Jorge Rodriguez
# Date: November 2024
# Description: This script creates a Dash app that allows users to explore the history of the Olympics by filtering and visualizing data from the 120 years of the modern Olympic era.
# The app includes the following features:
# - RadioItems for selecting the Olympic season (Summer, Winter, or Both)
# - Dropdown for selecting a specific sport
# - RadioItems for selecting Gender
# - Dropdown for selecting a specific year
# - Input for filtering countries that have won more than X medals
#-------------------------------------------------------------------------------


import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

#--------------------------------------------------------
# Load data and create additional columns and dataframes
#--------------------------------------------------------
#df = pd.read_csv('athlete_events.csv')
events_df = pd.read_csv('athlete_events.csv') # 120 years of Olympic history
events_df = pd.get_dummies(events_df, columns=['Medal'], drop_first=False)

data_120_total = events_df.groupby(['NOC']).agg(total_gold = ('Medal_Gold','sum'),
                                        total_bronze = ('Medal_Bronze','sum'),
                                        total_silver = ('Medal_Silver','sum')).reset_index()

data_120_per_season = events_df.groupby(['NOC','Season']).agg(total_gold = ('Medal_Gold','sum'),
                                        total_bronze = ('Medal_Bronze','sum'),
                                        total_silver = ('Medal_Silver','sum')).reset_index()


data_120_per_year = events_df.groupby(['NOC','Season','Year']).agg(total_gold = ('Medal_Gold','sum'),
                                        total_bronze = ('Medal_Bronze','sum'),
                                        total_silver = ('Medal_Silver','sum')).reset_index()

df = events_df[['Name','Sex','Age','Season','Year']][(events_df['Age'] > 0)].sort_values(by='Year', ascending=True) 


data_120_total['total_medals'] = data_120_total['total_gold'] + data_120_total['total_silver'] + data_120_total['total_bronze']
data_120_per_season['total_medals'] = data_120_per_season['total_gold'] + data_120_per_season['total_silver'] + data_120_per_season['total_bronze']
data_120_per_year['total_medals'] = data_120_per_year['total_gold'] + data_120_per_year['total_silver'] + data_120_per_year['total_bronze']

#-------------------------
# Initialize the Dash app
#-------------------------
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Olympics Data Explorer"),

    dcc.Markdown('## The Olympics Data Explorer allows you to explore the history of the Olympics by filtering and visualizing data from the 120 years of the modern Olympic era.'),
    dcc.Markdown('### The app includes the following features:'),
    dcc.Markdown('#### - RadioItems for selecting the Olympic season (Summer, Winter, or Both)'),
    dcc.Markdown('#### - Checkbox for selecting the Medal Type (Gold, Silver, Bronze)'),
    dcc.Markdown('#### - Nuemric Input for filtering countries that have won more than X medals'),
    dcc.Markdown('#### - RadioItems for Gender selection for a Histogram of age distribution'),
    dcc.Markdown('#### - Dropdown for selecting a specific year'),
    dcc.Markdown('#### - Graphs: A GeoGraph, a MapGraph and a Histogram'),
    dcc.Markdown('#### - Hope you enjoy it!'),

    
    # RadioItems for Season filter
    html.Label('Olympic Season',
                       style={'font': '15px Arial, sans-serif', 'color': 'blue', 'font-weight': 'bold'}),
    dcc.RadioItems(
        id='season-radio',
        options=[{'label': 'Summer', 'value': 'Summer'}, {'label': 'Winter', 'value': 'Winter'}, {'label': 'Both', 'value': 'Both'}],
        value='Both',
        labelStyle={'display': 'inline-block'}
    ),

   # Checkbox for Metal Type
    html.Br(),
    html.Label('Medal Type',
                       style={'font': '15px Arial, sans-serif', 'color': 'blue', 'font-weight': 'bold'}),
    dcc.Checklist(
        id='medal-checklist',
        options=[{'label': 'Gold', 'value': 'Gold'}, {'label': 'Silver', 'value': 'Silver'}, {'label': 'Bronze', 'value': 'Bronze'}],
        value=['Gold', 'Silver', 'Bronze'],
    ),
    
    html.Br(),
    html.Label('Display Countries that have won more than X medals:',
                       style={'font': '15px Arial, sans-serif', 'color': 'blue', 'font-weight': 'bold'}),
    html.Div([
        "Total Medals won: ",
        dcc.Input(id='total-medals', value=0, type='number'),
    ]),


    # RadioItems for Gender
    html.Br(),
    html.Label('Gender',
                       style={'font': '15px Arial, sans-serif', 'color': 'blue', 'font-weight': 'bold'}),
    dcc.RadioItems(
        id='gender-radio',
        options=[{'label': 'Male', 'value': 'M'}, {'label': 'Female', 'value': 'F'}, {'label': 'Both', 'value': 'B'}],
        value='B',
        labelStyle={'display': 'inline-block'}
    ),
    
    # Dropdown for Olympic Year with an "All years" option
    html.Br(),
    html.Label('Olympic Year',
                       style={'font': '15px Arial, sans-serif', 'color': 'blue', 'font-weight': 'bold'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': 'All Years', 'value': 'All'}] + [{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
        value='All',
        placeholder="Select Year"
    ),
    

    html.Br(),
    # Graphs
    dcc.Graph(id='geo-graph'),
    html.Br(),
    dcc.Graph(id='map-graph'),
    html.Br(),
    dcc.Graph(id='histogram')
])

# Define callback
@app.callback(
    Output('geo-graph', 'figure'),
    Output('map-graph', 'figure'),
    Output('histogram', 'figure'),
    Input('season-radio', 'value'),
    #Input('sport-dropdown', 'value'),
    Input('gender-radio', 'value'),
    Input('year-dropdown', 'value'),
    Input('total-medals', 'value'),
    Input('medal-checklist', 'value')
)
def update_graphs(selected_season, selected_gender, selected_year, total_medals, medal_checklist):

    if len(medal_checklist) == 0:
        medal_checklist = ['Gold', 'Silver', 'Bronze']
    medal_checklist_str = ", ".join(medal_checklist)


    if selected_season== 'Both':
        data = data_120_total
    else:
        data = data_120_per_season[data_120_per_season['Season']== selected_season]
    
    data['total_medals'] = 0
    if 'Gold' in medal_checklist:
        data['total_medals'] += data['total_gold']
    if 'Silver' in medal_checklist:
        data['total_medals'] += data['total_silver']
    if 'Bronze' in medal_checklist:
        data['total_medals'] += data['total_bronze']
    
    data = data[data['total_medals'] > total_medals]
    geo_graph = px.scatter_geo(data, locations='NOC', locationmode='ISO-3',size='total_medals', hover_data=['NOC', 'total_medals','total_gold', 'total_silver', 'total_bronze'], template='plotly_dark',
               title=f'Total {medal_checklist_str} Medals per Country over the past 120 years for {str(selected_season)} Olympics in All Sports', color='total_medals', projection='natural earth', color_continuous_scale='teal',
               labels=({'total_medals':'Total Medals'} , {'NOC':'Country'} , {'total_gold':'Gold'} , {'total_silver':'Silver'} , {'total_bronze':'Bronze'}))


    data = data[data['total_medals'] > total_medals]
    geo_map = px.choropleth(data, locations='NOC', locationmode='ISO-3', color='total_medals', hover_data=['NOC','total_medals','total_gold', 'total_silver', 'total_bronze'], template='plotly_dark',
               title=f'Total {medal_checklist_str} Medals per Country over the past 120 years for {str(selected_season)} Olympics in All Sports', projection='natural earth', color_continuous_scale='teal', scope='world',
               labels=({'total_medals':'Total Medals'}, {'NOC':'Country'}, {'total_gold':'Gold'}, {'total_silver':'Silver'}, {'total_bronze':'Bronze'}))


    if (selected_gender == 'F'):
        gender = 'Females'
        df1 = df[(df['Sex'] == 'F')]
    if (selected_gender == 'M'):
        gender = 'Males'
        df1 = df[(df['Sex'] == 'M')]
    if (selected_gender == 'B'):
        gender = 'Females & Males'
        df1 = df

    if (selected_season != 'Both'):
        df1 = df1[df1['Season'] == (selected_season)]

    if selected_year != 'All':
        df1 = df1[df1['Year'] == (selected_year)]

    histogram = px.histogram(df1, x='Age', title=f'{str(selected_year)} {str(selected_season)} Olympics ages Distribution for {gender} Athletes', animation_frame='Year', range_y=[0, 1500], range_x=[10, 40], labels={'Age':'Age'}, 
                            template='plotly_dark',nbins=50)
    histogram.update_layout(xaxis_title='Age', yaxis_title='Number of Athletes')
    

    return geo_graph, geo_map, histogram

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
 