# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback, Output, Input
from dash import dash_table
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import date
import plotly.graph_objects as go
from datetime import datetime
from filtering import filtered_data
from flask import Flask
import re
from sqlalchemy import create_engine
import psycopg2 


# Import data
df = pd.read_excel("Final_table.xlsx")
err_2 = pd.read_excel("err_2.xlsx")
err_3 = pd.read_excel("err_3.xlsx")
err_4 = pd.read_excel("err_4.xlsx")
err_5 = pd.read_excel("err_5.xlsx")
# df_row = pd.read_excel("Выгрузка_кардиопациентов_из_FTP_2022_2023.xlsx")
# df_row.columns = ['id', 'downloadDate', 'hospitalName','hospitalOID', 'birthDate', 'diagnosis', 
#              'dischargeDate', 'polyclinicName', 'policlinicOID', 'gender', 'coronaryArtery', 
#              'angioplasty', 'catheterAblation','RCV', 'MKB_E10_E11', 'LDLcholesterol', 
#             'glucoseConcentration', 'LipidLoweringTherapy' ]

# err_2 = df_row.query('MKB_E10_E11 == "fault"') 
# err_2.groupby('hospitalName', as_index=False).agg({'id': 'count'}) \
#     .sort_values('id', ascending=False)
# Initialize the app
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=["assets/home_style.css", dbc.themes.COSMO])

df1 = df.groupby('dischargeDate', as_index=False).agg({'id': 'count'}) \
    .sort_values('dischargeDate', ascending=True)
medical_indication_frame = pd.DataFrame(['coronaryArtery','angioplasty','catheterAblation','RCV','MKB_E10_E11','LDLcholesterol','glucoseConcentration','LipidLoweringTherapy'])
medical_indication_frame.columns = ['indication']
triada_file = pd.read_excel("triada_table.xlsx")
dislek_file = pd.read_excel("dislek_dataset.xlsx")
hospital_dict = pd.DataFrame(df["hospitalName"].unique())
hospital_dict_dict = df["hospitalName"].unique()
hospital_dict.columns=['Наименование']
polyclinic_dict = pd.DataFrame(df["polyclinicName"].unique())
polyclinic_dict.columns=['Наименование']

MKB_dict = pd.read_excel("MKB.xlsx")
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
hospital_filter_for_dislek = dcc.Dropdown(
    id= "hospital-filter_dislek",
    options=[{'label':'Стационары','value':'hospitalName'},
            {'label':'Поликлиники','value':'polyclinicName'}],
    value='hospitalName' 
)
hospital_filter_for_triada = dcc.Dropdown(
    id= "hospital-filter_triada",
    options=[{'label':'Стационары','value':'hospitalName'},
            {'label':'Поликлиники','value':'polyclinicName'}],
    value='hospitalName'
)

error_filter = dcc.Dropdown(
    id= "error-filter",
    options=[{'label':'Пропущенные значения/опечатки в дате','value':'date_err'},
            {'label':'Пропущенные значения/Опечатки в основном диагнозе','value':'main_diagnos'},
            {'label':'Опечатки в диагнозе Е10-Е11','value':'e10_e11'},
            {'label':'Пропущенные значения пола','value':'err_gender'},
            ],
    value='e10_e11'
)

# Markup elements
card_height_s = '18rem'
card_height = '25rem'
indicator_width = 6

factoid_heigth = '7rem'
bottom_dist = '5px'

first_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Общее количество выписанных пациентов ",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                      },
                               ),
                ],),

            ]),
            dbc.Row([
                dbc.Col(html.H4(id="first_indicator-chart",
                                style={'text-align': 'center',
                                    
                                       'margin-left': '8px'}))
            ])
        ],
            style={
                'height': factoid_heigth, 
                'margin-right': '8px',
            }
        )
    ])
forth_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество активных стационаров",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                   
                                      },
                               ),
                ]) ,
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="forth_indicator-chart",
                                style={'text-align': 'center',
                                   
                                       'margin-right': '8px'}))
            ])
        ],
            style={
                'height': factoid_heigth,
                
            }
        )
    ])
fifth_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество активных поликлиник",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                      },
                               ),
                ], ),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="fifth_indicator-chart",style={'text-align': 'center', 'margin-right': '8px',}))
            ])
        ],
            style={
                'height': factoid_heigth,
                
            }
        )
    ])
sixth_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество стационаров, передавших данные с ошибками",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                      },
                               ),
                ], ),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="sixth_indicator-chart",style={'text-align': 'center', 'margin-right': '8px',}))
            ])
        ],
            style={
                'height': factoid_heigth,
                
            }
        )
    ])

second_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество пациентов с 'ТРИАДА'",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                    
                                      },
                               ),
                ], ),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="second_indicator-chart",style={'text-align': 'center', 'margin-right': '8px',}))
            ])
        ],
            style={
                'height': factoid_heigth,
                
            }
        )
    ])
third_indicator = dbc.Card(
    [
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Количество пациентов с 'Дислек'",
                               style={'font-size': 13,
                                      'text-align': 'center',
                                    #   'font-family': 'Century Gothic'
                                      },
                               ),
                ], ),
            ]),
            dbc.Row([
                dbc.Col(html.H4(id="third_indicator-chart",style={'text-align': 'center', 'margin-right': '8px',}))
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
            dbc.Row([
                dbc.Col([
                    html.H4("Распределение пациентов по стационарам",
                               style={'font-size': 20,
                                      'text-align': 'left',
                                      'margin-bottom': '0px'
                                      },
                               ),
                ], style={'margin-bottom': '0px'},width=8),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="hospital_distribution-chart", style={'height': '35rem'}))
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
                dcc.Graph(id="age_gender_pyramid-chart", style={'height': '35rem'}),
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
            ], width=8),
            dbc.Col([
                html.Div(hospital_filter_for_triada,
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=3)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='triada-graph')
        ])
    ])
    ],
    )
])

dislek = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Количество пациентов с 'ДИСЛЕК'",
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=8),
            dbc.Col([
                html.Div(hospital_filter_for_dislek,
                           style={'font-size': 20,
                                  'text-align': 'left',
                        
                                  }, 
                           ),
            ], width=3)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='dislek-graph', style={"maxHeight": "400px", "overflow": "scroll"}),
                
        ])
    ])
    ],
    )
])

error_types = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Отчет об ошибочных значениях в передаваемых данных за выбранный период",
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=6),
            dbc.Col([
                html.Div(error_filter,
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ], width=6)
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='error-graph')
        ])
    ])
    ],
    )
])
empty_hospital = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.H4("Перечень стационаров, не передававших записи за выбранный период:",
                           style={'font-size': 20,
                                  'text-align': 'left',

                                  },
                           ),
            ]),
        ]),
         dbc.Row([
                dbc.Col(html.H4(id="error-table",style={'text-align': 'left', 'margin-right': '8px',}))
            # dash_table.DataTable(
            # id='error-table',
            # sort_action='native',
            # columns=[{'name': 'Наименование', 'id': 'Наименование', 'type': 'numeric'}],
            # style_cell={
            #     'width': '100px',
            #     'minWidth': '100px',
            #     'maxWidth': '100px',
            #     'overflow': 'hidden',
            #     'textOverflow': 'ellipsis',
            #     'text_align': 'left',
            #     'font-family': 'sans-serif',
            #     'font-size': '14px',
            # },
            # )
    
    ],
    )
])
])
#_________TABS_________________
tab1_content = [dbc.Row([
        dbc.Col([
            hospital_distribution
        ],
        width={'size':6}),
        dbc.Col([
            age_gender_histogram
        ],
        width={'size':6}),
    ],
    style={'margin-bottom':bottom_dist}),

        dbc.Row([
            dbc.Col([
                all_discharged_number
            ],
            width={'size':6}),
            dbc.Col([
                diagnosis_diagram
            ],
            width={'size':6})
        ],
    style={'margin-bottom':bottom_dist}),
    dbc.Row([
        dbc.Col([
            dislek
        ],
        width={'size':6}),
        
        dbc.Col([
            triada
        ],
        width={'size':6}),
    ],
    style={'margin-bottom':bottom_dist,

}),]
tab2_content = [
    dbc.Row([
            dbc.Col([
                error_types
            ],
            width={'size':7}),
            dbc.Col([
                empty_hospital
            ],
            width={'size': 5})
        ],
        
        style={'margin-bottom':bottom_dist}),
]

tab3_content = [
    dbc.Row([
            dbc.Col([
                dash_table.DataTable(data=hospital_dict.to_dict('records'), columns=[{'name': i, 'id':i} for i in hospital_dict.columns],
                                     style_data={'textAlign': 'left'},
                                     style_header={'textAlign': 'left'}),
            ],
            width={'size':6}),
            dbc.Col([
                dash_table.DataTable(data=MKB_dict.to_dict('records'), columns=[{'name': i, 'id':i} for i in hospital_dict.columns],
                                    style_data={'textAlign': 'left'},
                                     style_header={'textAlign': 'left'}),
            ],
            width={'size':6})
        ],
        style={'margin-bottom':bottom_dist}),

        dbc.Row([
            dbc.Col([
                dash_table.DataTable(data=polyclinic_dict.to_dict('records'), columns=[{'name': i, 'id':i} for i in hospital_dict.columns],
                                     style_data={'textAlign': 'left'},
                                     style_header={'textAlign': 'left'}),
            ],
            width={'size':6})
        ],
        style={'margin-bottom':bottom_dist}),
]
#_________CALLBACKS____________
# Триада
@app.callback(
    Output(component_id='triada-graph', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
        Input(component_id='hospital-filter_triada', component_property='value'),
    ]
)
def update_triada(start_date, end_date, value):
    triada_data = filtered_data(start_date, end_date, df)
    col1 = triada_data.query('RCV == 1')
    col2 = col1.query('MKB_E10_E11 == 1')
    triada = col2.query('LDLcholesterol == 1')
    triada_fig = px.histogram(triada, y = value, text_auto=True, color_discrete_sequence=px.colors.sequential.Darkmint_r).update_yaxes(categoryorder="total ascending")
    # triada_fig.update_layout(xaxis={'showticklabels': False})
    triada_fig.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Количество пациентов", yaxis_title="", yaxis={'visible': True, 'showticklabels': True},xaxis={'visible': True,'showticklabels': False})
    triada_fig.update_yaxes(automargin=True)
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
    fig2 = px.histogram(chart_data2, y = "hospitalName", text_auto=True, color_discrete_sequence=px.colors.sequential.Darkmint_r)
                        # title = "Распределение пациентов по стационарам")
    fig2.update_yaxes(categoryorder="total ascending", title="", automargin=True)
    fig2.update_layout(xaxis_title="Количество пациентов",yaxis={'visible': True, 'showticklabels': True},  xaxis={'visible': True,'showticklabels': False}, template=CHARTS_TEMPLATE) 
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
    diagnosis_frame.loc[(diagnosis_frame['count'] < (m // 20)),'diagnos'] = 'others'

    fig_diagnos = px.treemap(diagnosis_frame, path=['diagnos'],
                 values='count', color='count', color_continuous_scale=px.colors.sequential.Darkmint)
    fig_diagnos.update_layout(template=CHARTS_TEMPLATE)
    return fig_diagnos

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
                  yaxis_title="Количество пациентов",barmode='group', xaxis_tickangle=-45,legend_y = 1.1, legend_orientation='h')
    return fig4

# #medical_term-chart
# @app.callback(
#     Output(component_id='medical_term-chart', component_property='figure'),
#     [
#         Input(component_id='date-filter', component_property='start_date'),
#         Input(component_id='date-filter', component_property='end_date'),
#     ]
# )
# def update_medical_term(start_date, end_date):
#     chart_data6 =  filtered_data(start_date, end_date, df)   
#     lst= []
#     df_colums = ['coronaryArtery', 'angioplasty', 'catheterAblation', 'RCV',
#        'MKB_E10_E11', 'LDLcholesterol', 'glucoseConcentration',
#        'LipidLoweringTherapy']
#     for k in df_colums:
#         lst.append(chart_data6[k].sum())
#     medical_indication_frame['number'] = lst
   
#     f6 = px.bar(medical_indication_frame, x = medical_indication_frame['indication'], y = medical_indication_frame['number'], color_discrete_sequence=px.colors.sequential.Darkmint_r)
#     f6.update_layout(template=CHARTS_TEMPLATE, xaxis_title="Показания",
#                   yaxis_title="Количество пациентов")
#     return f6

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

    chart_data8 = filtered_data(start_date, end_date, triada_file)
    second_factoid = str(chart_data8['id'].count())
    
    return second_factoid

#indicator3
@app.callback(
    Output(component_id='third_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_third_indicator(start_date, end_date):

    chart_data8 = filtered_data(start_date, end_date, dislek_file)
    third_factoid = str(chart_data8.loc[chart_data8['dislek'] == "dislek", 'dislek'].count())
    
    return third_factoid

#indicator4
@app.callback(
    Output(component_id='forth_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_second_indicator(start_date, end_date):
    chart_data7 =  filtered_data(start_date, end_date, df)
    second_factoid = str(len(chart_data7["hospitalName"].unique()))
    return second_factoid

#indicator5
@app.callback(
    Output(component_id='fifth_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_fifth_indicator(start_date, end_date):

    chart_data7 =  filtered_data(start_date, end_date, df)
    fifth_factoid = str(len(chart_data7["polyclinicName"].unique()))

    return fifth_factoid
#indicator6
@app.callback(
    Output(component_id='sixth_indicator-chart', component_property='children'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
    ]
)
def update_sixth_indicator(start_date, end_date):

    chart_data7 =  filtered_data(start_date, end_date, err_2)
    sixth_factoid = str(len(chart_data7["hospitalName"].unique()))

    return sixth_factoid

#dislek
@app.callback(
    Output(component_id='dislek-graph', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
        Input(component_id='hospital-filter_dislek', component_property='value'),
    ]
)
def update_dislek(start_date, end_date, value):
    dislek_data = filtered_data(start_date, end_date, dislek_file)
    dis = dislek_data.query('dislek == "dislek"')
    dis.groupby('hospitalName', as_index=False).agg({'dislek': 'count'}) \
    .sort_values('dislek', ascending=False)
    dislek_fig = px.histogram(dis, y = value, text_auto=True, color_discrete_sequence=px.colors.sequential.Darkmint_r).update_yaxes(categoryorder="total ascending")
    dislek_fig.update_layout(xaxis_title="Количество пациентов с 'ДИСЛЕК'", yaxis_title ='',
                  template=CHARTS_TEMPLATE, title_pad_b=0)
    dislek_fig.update_layout(yaxis={'visible': True, 'showticklabels': True},  xaxis={'visible': True,'showticklabels': False}) 
    dislek_fig.update_yaxes(automargin=True)
    return dislek_fig
#errors
@app.callback(
    Output(component_id='error-graph', component_property='figure'),
    [
        Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),
        Input(component_id='error-filter', component_property='value'),
    ]
)
def update_dislek(start_date, end_date, value):
    if value == "date_err":
        row_data = filtered_data(start_date, end_date, err_3)
    elif value == "main_diagnos":
        row_data = filtered_data(start_date, end_date, err_5)
    elif value == "e10_e11":
        row_data = filtered_data(start_date, end_date, err_2)
    elif value == "err_gender":
        row_data = filtered_data(start_date, end_date, err_4)


    err_fig = px.histogram(row_data,  y= "hospitalName",text_auto=True, color_discrete_sequence=px.colors.sequential.Darkmint_r).update_yaxes(categoryorder="total ascending")
    err_fig.update_layout( xaxis_title ="Количество записей с ошибкой выбранного типа",yaxis={'visible': True, 'showticklabels': True},  xaxis={'visible': True,'showticklabels': True},
                  template=CHARTS_TEMPLATE)
    err_fig.update_yaxes(title=" ", automargin=True)
    return err_fig

#errors2
# @app.callback(
#     Output(component_id='error-table', component_property='children'),
#     [
#         Input(component_id='date-filter', component_property='start_date'),
#         Input(component_id='date-filter', component_property='end_date'),
#         # Input(component_id='error-filter', component_property='value'),
#     ]
# )
# def update_dislek(start_date, end_date):
#     uni_list = " "
#     uniq_data = filtered_data(start_date, end_date, df)
#     uni = uniq_data["hospitalName"].unique()
#     for i in uni:
#         if i not in hospital_dict_dict:
#             uni_list = uni_list + str(i) + "," +"\n"

#     return uni_list

@app.callback(
    [
        Output('error-table', 'children'),
    ],
    [   Input(component_id='date-filter', component_property='start_date'),
        Input(component_id='date-filter', component_property='end_date'),])
def update_table(start_date, end_date):
    res = []
    uni_list = " "
    uniq_data = filtered_data(start_date, end_date, df)
    uni = uniq_data["hospitalName"].unique()
    for i in hospital_dict_dict:
        if i not in uni:
            # uni_list.loc[ len(uni_list.index )] = [i]
            # uni_list.append(i)

            uni_list = uni_list +str(i) +';       '
    # return uni_list.to_dict('records')
    #         data_bars(filtered_data, "Sales") + data_bars_diverging(filtered_data, "Profit"))
    if len(uni_list) < 5:
        res.append("__")
    else:
        res.append(uni_list)
    
    return res

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
            date_filter,
            ],
            width={'size':3},
        )
    ],
    className='app-header',
    style={'margin-top': 10,
           'margin-bottom':10}),
    #body
    html.H4("Ключевые показатели за выбранный период"),
    dbc.Row([
        dbc.Col([
            first_indicator,
        ], width={'size':2}),
        dbc.Col([
            second_indicator,
        ], width={'size': 2}),
        dbc.Col([
            third_indicator,
        ], width={'size': 2}),
        dbc.Col([
            forth_indicator,
        ], width={'size': 2}),
        dbc.Col([
            fifth_indicator,
        ], width={'size': 2}),
        dbc.Col([
            sixth_indicator,
        ], width={'size': 2}),

    ], style={'margin-bottom': bottom_dist}
    ),
    
    dbc.Tabs([
        dbc.Tab(tab1_content, label='Отчет o пациентах'),
        dbc.Tab(tab2_content, label='Отчет o стационарах'),
        dbc.Tab(tab3_content, label='Справочная информация'),

    ]),],

    style = {'margin-left':'20px',
            'margin-right':'20px'}
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)