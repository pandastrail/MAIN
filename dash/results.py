# -*- coding: utf-8 -*-
"""
Created on Thu May  3 13:52:09 2018

@author: ksagilop
"""

# -*- coding: utf-8 -*-
"""
ToDo: 
    
"""
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import datetime as dt

''' Dataframes '''
# Create dataframe from csv file
csv_input_file = 'results.csv'
df = pd.read_csv(csv_input_file,
                sep=';',
                usecols=['race',
                         'cat',
                         'type',
                         'dist_km',
                         'gain_m',
                         'rank',
                         'total_entries',
                         'score',
                         'date'
                        ],
                parse_dates={'date_parsed':['date']},
                dayfirst=True,
                keep_date_col=False 
                )


# Create date columns for data mart
df['year'] = df['date_parsed'].dt.year
df['month'] = df['date_parsed'].dt.month
df['day'] = df['date_parsed'].dt.day

# Set index
df.set_index('date_parsed', inplace=True)

# Array of Available years and sort
available_years = df['year'].unique()
available_years.sort()

# Array of available types
available_types = df['type'].unique()

''' Dash '''
app = dash.Dash()

app.layout = html.Div([
        html.Div([
                
            html.H1('Race Results Analysis'),
            
            html.H3('Add a new entry'),
            
            html.Div(
                    [dcc.Input(
                            id='new_race',
                            placeholder='Enter Race Name...',
                            type='text',
                            value=''
                            ),
                     html.Button('Submit', id='button'),
                     html.Div(id='output-container-button',
                              children='Enter the values and press submit')
                    ]
                    ),
            
            html.H2('Veloviewer Score'),
            
            html.Div('Last update: ' + df.index.max().strftime("%B %d, %Y")),
            
            html.Div([dcc.Dropdown(
                        id='year_selection',
                        options=[{'label': i, 'value': i} for i in available_years],
                        value=[2018, 2017, 2016],
                        multi=True
                        )
                    ],
                    style={'width': '80%', 'align':'left'}),

            html.Div([dcc.Checklist(
                        id='type_selection',
                        options=[{'label': i, 'value': i} for i in available_types],
                        values=available_types,
                        labelStyle={'display': 'inline-block'}
                                )
                        ]),

            html.Div([dcc.Graph(id='score_graph')
                      ],
                      style={'width': '80%', 'display': 'inline-block', 'align':'left'}),
            
            # Pie chart of type distribution
            
            # Scatter number of entries vs score (or rank?)
            # Score vs dist
            # Score vs gain
            # time back vs dist
            
            ])
        ])

# Dash CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# Loading screen CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('new_race', 'value')])

def update_output(n_clicks, value):
    if n_clicks == None:
        return('No new data entered')
    else:
        
        return 'Race "{}" was added to {} with clicks'.format(
                                                value,
                                                csv_input_file
                                                )

@app.callback(
        Output(component_id='score_graph', component_property='figure'),
        [Input(component_id='year_selection', component_property='value'),
         Input(component_id='type_selection', component_property='values')
        ]
        )

def update_score_graph(value, values):
    # List to plot the traces by type
    traces = []
    
    # Year selection
    df_score = df[df['year'].isin(value)]
    
    # How many entries
    count_races = 0
    
    # Type selection
    for i in range(len(values)):
        df_type = df_score[df_score['type'] == values[i]]
        #df_marker = df_type['dist_km']   # series with size of marker
    
        X = df_type.index
        Y = df_type['score']
        T = df_type['race']
        count_races += df_type.shape[0]
    
        trace = go.Scatter(
                x=X,
                y=Y,
                text=T,
                mode='markers',
                marker={
                        'size': 10,
                        'opacity': 0.75
                        },
                name=values[i],
                )
    
        title_score = str(count_races) + ' Races'
        traces.append(trace)
    
    # x_label must be months?
    score_fig = {'data': traces,
                 'layout': go.Layout(
                                        title=title_score,
                                        xaxis=dict(
                                                title='Date',
                                                tickformat='%d %b %y'
                                                ),
                                        yaxis=dict(
                                                title='Score'
                                                ),
                                        hovermode='closest'
                                        )
                    }

    return score_fig

if __name__ == '__main__':
    app.run_server(debug=True)
