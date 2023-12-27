import pandas as pd
# import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
# import plotly.graph_objects as go
import dash_bootstrap_components as dbc
# from dash import callback_context
import os

# Wrangling ----------------------------------------------------------------------------------
os.chdir = "D:\\Vignesh\\Personal\\Data Analyst\\Recent Projects\\Financial Dashboard\\Data"
df = pd.read_csv('Data\\data.csv')

cls_df = pd.pivot_table(df, index=['Direction', 'State/UT', 'Year', 'Contact'], columns='Type', values="Amount",
                        aggfunc='sum').reset_index()
cls_df['profit'] = cls_df['Sales']-cls_df['Purchases']-cls_df['Expense']

pl = []
Abs_Amount = []
for i in cls_df['profit']:
    if i > 0:
        pl.append('Profit')
        Abs_Amount.append(abs(i))
    else:
        pl.append('Loss')
        Abs_Amount.append(abs(i))
cls_df['profit/Loss'] = pl
cls_df['Abs_profit'] = Abs_Amount


# App -----------------------------------------------------------------------------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server = app.server

app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Financial Dashboard",
                        className='text-center text-primary mb-4'),
                width=12)
    ),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='treemap', figure=px.treemap(
                data_frame=cls_df,
                path=['Year', 'Direction', 'State/UT', ],
                values='Abs_profit',
                color='profit/Loss',
                template='plotly_dark',
                color_discrete_map={
                    'Profit': 'Green',
                    'Loss': 'crimson'},
                custom_data=['State/UT']),
                      )], xs=12, sm=12, md=12, lg=12, xl=12),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='starburst', figure={}
                          )], xs=12, sm=12, md=12, lg=5, xl=5),
            dbc.Col([
                dcc.Graph(id='line', figure={}
                          )], xs=12, sm=12, md=12, lg=5, xl=5),
        ]),
    ])
])


@app.callback(
    Output(component_id='starburst', component_property='figure'),
    Input(component_id='treemap', component_property='hoverData'),
    Input(component_id='treemap', component_property='clickData')
)
def update_starburst(hover_data, click_data):
    entry = hover_data['points'][0]['entry'] if click_data['points'][0]['entry'] is None \
        else click_data['points'][0]['entry']
    print(entry)
    if entry is None or entry == 2020:
        ddf = df
    elif entry in ["North", "South", "East", "West"]:
        ddf = df.loc[df['Direction'] == entry]
    else:
        ddf = df.loc[df['State/UT'] == entry]

    figure = px.sunburst(ddf, path=['Type', 'Account', ], values='Amount', template='plotly_dark',
                         color_discrete_map={'Sales': 'Green',
                                             'Expense': 'crimson',
                                             'Purchases': 'Grey'},
                         custom_data=['Account'])
    return figure


if __name__ == '__main__':

    app.run_server(debug=True)
