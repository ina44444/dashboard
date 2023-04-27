# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import date
import plotly.graph_objects as go
from datetime import datetime
from filtering import filtered_data
from flask import Flask
# Import data
df = pd.read_excel("Processed_data.xlsx")
df_row = pd.read_excel("Выгрузка_кардиопациентов_из_FTP_2022_2023.xlsx")
# Initialize the app
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=["assets/home_style.css", dbc.themes.COSMO])

df1 = df.groupby('dischargeDate', as_index=False).agg({'id': 'count'}) \
    .sort_values('dischargeDate', ascending=True)
medical_indication_frame = pd.DataFrame(['coronaryArtery','angioplasty','catheterAblation','RCV','MKB_E10_E11','LDLcholesterol','glucoseConcentration','LipidLoweringTherapy'])
medical_indication_frame.columns = ['indication']
triada_file = pd.read_excel("Triada_table.xlsx")

# Design settings
CHARTS_TEMPLATE = go.layout.Template(
    layout= dict(
        font=dict(family='Helvetica'),
        legend=dict(orientation='v',
                    title_text='')
    )
)

# Filters
date_filter =dcc.DatePickerRange(
    id="date-filter",
    min_date_allowed=datetime(2020, 11, 3),
    max_date_allowed=datetime(2023, 1, 28), 
    start_date = date(2021, 11, 3),
    end_date = date(2023, 1, 28),
    display_format='D MMM YYYY',  
)
hospital_filter = dcc.Dropdown(
    id= "hospital-filter",
    options=[{'label':'Стационары','value':'hospitalName'},
            {'label':'Поликлиники','value':'polyclinicName'}],
    value='hospitalName'
    
)


# Markup elements
card_height_s = '18rem'
card_height = '25rem'

factoid_heigth = '7rem'

first_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Общее количество выписанных пациентов ",
                               style={'font-size': 15,
                                      'text-align': 'сenter',
                                    
                                      },
                               ),
                ], width=8),

            ]),
            dbc.Row([
                dbc.Col(html.H4(id="first_indicator-chart",
                                style={'text-align': 'сenter',
                                    #    'font-family': 'Century Gothic',
                                       'margin-left': '8px'}))
            ])
        ],
            style={
                'height': factoid_heigth, 
                'margin-right': '8px',
            }
        )
    ])
second_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество пациентов с повторным ССЗ",
                               style={'font-size': 15,
                                      'text-align': 'сenter',
                                    #   'font-family': 'Century Gothic'
                                      },
                               ),
                ], width=8),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="second_indicator-chart",
                                style={'text-align': 'сenter',
                                    #    'font-family': 'Century Gothic',
                                       'margin-right': '8px'}))
            ])
        ],
            style={
                'height': factoid_heigth,
                # 'font-family': 'Century Gothic'
            }
        )
    ])
third_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество пациентов с диагнозом МКБ Е10-Е11",
                               style={'font-size': 15,
                                      'text-align': 'сenter',
                                    #   'font-family': 'Century Gothic'
                                      },
                               ),
                ], width=8),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="third_indicator-chart",style={'text-align': 'сenter', 'margin-right': '8px',}))
            ])
        ],
            style={
                'height': factoid_heigth,
                # 'font-family': 'Century Gothic'
            }
        )
    ])
forth_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество пациентов с показателем ХС ЛПНП не ниже 5,0 ммоль/л",
                               style={'font-size': 13,
                                      'text-align': 'сenter',
                                    #   'font-family': 'Century Gothic'
                                      },
                               ),
                ], width=8),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="forth_indicator-chart",style={'text-align': 'сenter', 'margin-right': '8px',}))
            ])
        ],
            style={
                'height': factoid_heigth,
                
            }
        )
    ])
hospital_distribution = dbc.Card(
    [
        dbc.CardBody([
            # dbc.Row([
            #     dbc.Col([
            #         html.H4("Распределение пациентов по стационарам",
            #                    style={'font-size': 20,
            #                           'text-align': 'left',
            #                           'margin-bottom': '0px'
            #                           },
            #                    ),
            #     ], width=8),
            # ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="hospital_distribution-chart", style={'height': '35rem',} ))
            ])
        ],
            # style={
            #     'font-family': 'Helvetica'
            # }
        )
    ])
medical_term= dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Количество пациентов, имеющих показания",
                           style={'font-size': 20,
                                  'text-align': 'left',
                                  },
                           ),
            ]),
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="medical_term-chart", style={'height': '20rem',}),
            )
        )
    ],
        style={
            'height': card_height,
            
        }
    )
])
age_gender_histogram = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Распределение по полу и возрасту",
                           style={'font-size': 20,
                                  'text-align': 'left',
                                  },
                           ),
            ], width=8),
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="age_gender_pyramid-chart", style={'height': '20rem'}),
            )
        )
    ],
        style={
            'height': card_height,
        }
    )
   
)
diagnosis_diagram = dbc.Card([
    dbc.CardBody([
        html.H4("Процентное соотношение основных диагнозов",
                   style={'font-size': 20,
                          'text-align': 'left',
                          
                          },
                   ),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id="diagnosis_diagram-chart", style={'height': '20rem'}),
            )
        )
    ],
        style={
            'height': card_height,
            
        }
    ),     
])
all_discharged_number = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Динамика количества пациентов",
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=8),
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='time-line-plot', style={'height': '20rem'})
            )
        )
    ],
        style={
            'height': card_height,
        }
    )
])

triada = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Количество пациентов с 'ТРИАДА'",
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=3),
            dbc.Col([
                html.Div(hospital_filter,
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=8)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='triada-graph', style={'height': '35rem'})
        ])
    ])
    ],
        style={
            # 'height': card_height,
              }
    )
])

#_________TABS_________________
tab1_content = [dbc.Row([
        dbc.Col([
            hospital_distribution
        ],
        width={'size':12})
    ],
    style={'margin-bottom':25}),

        dbc.Row([
            dbc.Col([
                all_discharged_number
            ],
            width={'size':8}),
            dbc.Col([
                diagnosis_diagram
            ],
            width={'size':4})
        ],
    style={'margin-bottom':25}),
dbc.Row([
        dbc.Col([
            age_gender_histogram
        ],
        width={'size':6}),
        
        dbc.Col([
            medical_term
        ],
        width={'size':6}),
    ],
    style={'margin-bottom':25,

}),]
tab2_content = [
    dbc.Row([
            dbc.Col([
                triada
            ],
            width={'size':10})
        ],
        style={'margin-bottom':25}),


]
#_________CALLBACKS____________
# Триада
@app.callback(
    Output(component_id='triada-graph', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
        Input(component_id='hospital-filter', component_property='value'),
    ]
)
def update_triada(start_date, end_date, value):
    triada_data = filtered_data(start_date, end_date, triada_file)
    col1 = triada_data.query('RCV == 1')
    col2 = col1.query('MKB_E10_E11 != 0')
    triada = col2.query('LDLcholesterol == 1')
    triada_fig = px.histogram(triada, y = value, color_discrete_sequence=px.colors.sequential.Darkmint_r).update_yaxes(categoryorder="total ascending")
    triada_fig.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Количество пациентов")
    triada_fig.update_yaxes(title="Наименование учреждения", automargin=True)
    return triada_fig
# time_line_plot
@app.callback(
    Output(component_id='time-line-plot', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_time_line_plot(start_date, end_date):
    chart_data = filtered_data(start_date, end_date, df1)
    fig = px.line(chart_data, x='dischargeDate', y='id', markers=True, color_discrete_sequence=px.colors.sequential.Darkmint_r)
    fig.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Дата",
                  yaxis_title="Количество пациентов",)
    return fig

# hospital_distribution
@app.callback(
    Output(component_id='hospital_distribution-chart', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_hospital_distribution(start_date, end_date):
    chart_data2 =  filtered_data(start_date, end_date, df)
    fig2 = px.histogram(chart_data2, y = "hospitalName", color_discrete_sequence=px.colors.sequential.Darkmint_r)
                        # title = "Распределение пациентов по стационарам")
    fig2.update_yaxes(categoryorder="total descending", title="Название стационара", automargin=True)
    fig2.update_layout(xaxis_title="Количество пациентов",
             template=CHARTS_TEMPLATE) 
    return fig2

# diagnosis_diagram
@app.callback(
    Output(component_id='diagnosis_diagram-chart', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_diagnosis_diagram(start_date, end_date):
    chart_data3 = filtered_data(start_date, end_date, df)
    diagnosis_frame = pd.DataFrame(sorted(chart_data3["diagnosis"].unique()))
    diagnosis_frame.columns = ['diagnos']
    main_diagnosis =[]
    for k in diagnosis_frame['diagnos']:
                
        main_diagnosis.append(len(chart_data3[(chart_data3["diagnosis"]== k)]))

    diagnosis_frame['count'] = main_diagnosis
    # diagnosis_frame.head()
    s = pd.Series(diagnosis_frame['count'])
    m = s.max()
    diagnosis_frame.loc[(diagnosis_frame['count'] < (m // 10)),'diagnos'] = 'others'

    fig3 = px.pie(diagnosis_frame, values='count', names='diagnos',color_discrete_sequence=px.colors.sequential.Darkmint_r)
    fig3.update_layout(template=CHARTS_TEMPLATE)
    return fig3

#age-gender-pyramid
@app.callback(
    Output(component_id='age_gender_pyramid-chart', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_age_gender_diagram(start_date, end_date):
    chart_data4 =  filtered_data(start_date, end_date, df)
    male_ages = []
    female_ages = []
    first = 0
    second = 5
    while second < 120:
        male_ages.append(len(chart_data4[(chart_data4["gender"]=="М") &( chart_data4["Age"] > first) &( chart_data4["Age"] <= second)]))
        female_ages.append(len(chart_data4[(chart_data4["gender"]=="Ж") &( chart_data4["Age"] > first) &( chart_data4["Age"] <= second)]))
        first += 5
        second += 5

    population = pd.DataFrame({"Age":['0 - 5', '6 - 10', '11 - 15','16 - 20', '21 -25', '26 - 30', '31 - 35', '36 - 40', '41 - 45','46 - 50','51 - 55', '56 - 60', '61 - 65','66 - 70','71 - 75', '76 - 80', '81 - 85', '86 - 90', '91 - 95', '96 - 100', '101 - 105', '106 - 110', '111 - 120'],
                    "Male": male_ages,
                        "Female":female_ages})
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=population['Age'],
        y=population['Male'],
        name='Мужчины',
        marker_color='MediumAquaMarine'
    ))
    fig4.add_trace(go.Bar(
        x=population['Age'],
        y=population['Female'],
        name='Женщины',
        marker_color='Teal'
    ))
    fig4.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Возраст",
                  yaxis_title="Количество пациентов",)
    return fig4

#medical_term-chart
@app.callback(
    Output(component_id='medical_term-chart', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_medical_term(start_date, end_date):
    chart_data6 =  filtered_data(start_date, end_date, df)   
    lst= []
    df_colums = ['coronaryArtery', 'angioplasty', 'catheterAblation', 'RCV',
       'MKB_E10_E11', 'LDLcholesterol', 'glucoseConcentration',
       'LipidLoweringTherapy']
    for k in df_colums:
        lst.append(chart_data6[k].sum())
    medical_indication_frame['number'] = lst
   
    f6 = px.bar(medical_indication_frame, x = medical_indication_frame['indication'], y = medical_indication_frame['number'], color_discrete_sequence=px.colors.sequential.Darkmint_r)
    f6.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Показания",
                  yaxis_title="Количество пациентов")
    return f6

#indicator 1
@app.callback(
    Output(component_id='first_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_first_indicator(start_date, end_date):
    chart_data7 =  filtered_data(start_date, end_date, df)
    first_factoid = str(chart_data7['id'].count())

    return first_factoid

#indicator2
@app.callback(
    Output(component_id='second_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_second_indicator(start_date, end_date):
    chart_data7 =  filtered_data(start_date, end_date, df)
    second_factoid = str(chart_data7['RCV'].sum())
    return second_factoid

@app.callback(
    Output(component_id='third_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_second_indicator(start_date, end_date):

    chart_data7 =  filtered_data(start_date, end_date, df)
    third_factoid = str(chart_data7['MKB_E10_E11'].sum())

    return third_factoid

@app.callback(
    Output(component_id='forth_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_forth_indicator(start_date, end_date):

    chart_data7 = filtered_data(start_date, end_date, df)
    forth_factoid = str(chart_data7['glucoseConcentration'].sum())
    
    return forth_factoid

#triada

# LAYOUT
app.layout = html.Div([
    #header
    dbc.Row([
        dbc.Col([
          
            html.H4("Интрерактивная панель для анализа сведений о выписанных пациентах с сердечно-сосудистыми и цереброваскулярными заболеваниями"),          
            ],                                          
            style={'margin-left':'10 px'},
            width={'size': 9}),
        dbc.Col([
            date_filter
        ],
        className= "dbc",
        width={'size':4, 'offset': 9})
    ],
    className='app-header',
    style={'margin-top': 10,
           'margin-bottom':10}),
    #body
    html.H4("Ключевые показатели за выбранный период"),
    dbc.Row([
        dbc.Col([
            first_indicator,
        ], width={'size':3}),
        dbc.Col([
            second_indicator,
        ], width={'size': 3}),
        dbc.Col([
            third_indicator,
        ], width={'size': 3}),
        dbc.Col([
            forth_indicator,
        ], width={'size': 3}),

    ], style={'margin-bottom': 10}
    ),
    
    dbc.Tabs([
        dbc.Tab(tab1_content, label='Отчет о пациентах'),
        dbc.Tab(tab2_content, label='Отчет о стационарах'),
    ]),],

    style = {'margin-left':'80px',
            'margin-right':'80px'}
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)