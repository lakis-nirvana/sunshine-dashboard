import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


app = Dash(__name__)

colors = {
    'background': '#ffffff',
    'text': '#000000'
}

data = pd.read_csv('sunshine hours by city.csv')

def country_select(country):
    """The following function allows to filter the dataframe by specific country and returns the dataframe after restructuring.

    Args:
        country (string): Country by which the main data source needs to be filtered and restructured should be passed as argument.

    Returns:
        dataframe: This is the final restructured and filtered dataframe that we can use for visualisation
    """
    temp = pd.melt(data[data['Country']==country],id_vars='City',
                   value_vars=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    return temp

cities = pd.read_csv('cities.csv')
data_geo=pd.merge(data,cities,left_on='City',right_on='name')
region=pd.read_csv('countryregion.csv',encoding= 'unicode_escape')
region['region']=region['region'].str.lower()
data_geo=pd.merge(data_geo,region[['alpha-2','region']],left_on='country_code',right_on='alpha-2')

temp = pd.melt(data_geo,id_vars=['City','state_code','latitude','longitude','region','Country'],
                   value_vars=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])



app.layout = html.Div(children=[
    html.H1(children='Sunshine Duration - Citywise', style={'textAlign': 'center','color': 'Black', 'fontSize': 40}),

    html.Div(children='''
        Interactive application to see the sunshine duration citywise
    ''',style={'textAlign': 'center','color': 'Black', 'fontSize': 28}),
    html.Div([        
        dcc.Dropdown(
            temp['region'].unique(),
            'europe',
            id='region'
        )],style={"height": "50%", "width": "40%",'display': 'inline-block'}), 
    html.Div([  
        dcc.Dropdown(
            temp['Country'].unique(),
            'France',
            id='xaxis-column'
        )],style={"height": "50%", "width": "40%",'display': 'inline-block'}),    
    html.Div([dcc.Graph(
        id='example-graph'
    )],style={"height": "50%", "width": "50%",'display': 'inline-block'}),    
    html.Div([dcc.Graph(
        id='example-graph2'
    )],style={"height": "50%", "width": "50%",'display': 'inline-block'})
])

@app.callback(
    [Output('example-graph', 'figure'),
     Output('example-graph2', 'figure')],
    [Input('xaxis-column', 'value'),
     Input('region', 'value')])



def update_graph(xaxis_column_name):
    dataframe = country_select(xaxis_column_name)
    fig = px.scatter(dataframe, y="City", x="variable",
           hover_name="City", color='value', size='value')
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    return fig

def update_graph(region_name):
    fig2 = px.scatter_geo(temp, lat='latitude',lon='longitude', color="value",
                     scope = region_name, 
                     animation_frame='variable',
                     category_orders={
                     'variable':list(temp['variable'].unique())
                    },)
    fig2.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="Black"
)
    fig2.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})
    return fig2

if __name__ == '__main__':
    app.run_server(debug=True)