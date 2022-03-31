from audioop import mul
from cProfile import label
from msilib.schema import Component
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import scipy.signal.signaltools

def _centered(arr, newsize):
    # Return the center newsize portion of the array.
    newsize = np.asarray(newsize)
    currsize = np.array(arr.shape)
    startind = (currsize - newsize) // 2
    endind = startind + newsize
    myslice = [slice(startind[k], endind[k]) for k in range(len(endind))]
    return arr[tuple(myslice)]

scipy.signal.signaltools._centered = _centered


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

#data section:
#---------------------------------------------------------
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
region['Continent']=region['Continent'].str.lower()
data_geo=pd.merge(data_geo,region[['iso-2','Continent']],left_on='country_code',right_on='iso-2')

temp = pd.melt(data_geo,id_vars=['City','state_code','latitude','longitude','Continent','Country'],
                   value_vars=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])


#Layout Section:
#---------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Sunshine Duration Dashboard for 2020",
                        className='text-center font-weight-bold bg-secondary text-primary p-2'),
                width=12)        
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='region-selector',multi=False,
                         value='europe',
                         options=[{'label':x, 'value':x}
                                  for x in temp['Continent'].unique()]),
            dcc.Graph(id='region-map',figure={})
        ], width = {'size': 6 ,'order':1}),
        dbc.Col([
            dcc.Dropdown(id='month-selector',multi=False,
                         value='Jan',
                         options=[{'label':x, 'value':x}
                                  for x in temp['variable'].unique()]),
            dcc.Graph(id='month-scatter',figure={})
        ], width = {'size': 6,'order':2 }),
    ]),
    dbc.Row([
        
    ]),
])

@app.callback(
    Output(component_id='region-map',component_property='figure'),
    Input(component_id='region-selector',component_property='value')
)
def update_regionn_graph(region_value):
    fig2 = px.scatter_geo(temp[temp['Continent']==region_value],
                            lat='latitude',lon='longitude', 
                            color="value",
                            size='value',
                            scope = region_value, 
                            animation_frame='variable',
                            category_orders={
                                'variable':list(temp['variable'].unique())
                            },
                        )
    fig2.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="Black"
)
    fig2.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    return fig2

@app.callback(
    Output(component_id='month-scatter',component_property='figure'),
    Input(component_id='month-selector',component_property='value'),
     Input(component_id='region-selector',component_property='value')
)

def update_country_graph(month_value,region_value):
    dataframe = temp[(temp['Continent']==region_value) & (temp['variable']==month_value)]
    fig = px.scatter(dataframe, y="value", x="latitude",
           hover_name="City", color='value', size='value',
            trendline="ols")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)