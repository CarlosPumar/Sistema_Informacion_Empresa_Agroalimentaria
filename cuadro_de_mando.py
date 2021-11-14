
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import datetime
from scipy import stats

import main






data_recolecta = main.main()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


ventanas = []




#GRAFICOS DE BARRA


#GRAFICA DE BARRAS POR DIAS
bloques_slider = {}

#CREAMOS EL SLIDER CON LOS BLOQUES
i = 0
while i < len(data_recolecta):
    bloques_slider[i] = data_recolecta[i]["fecha"][0]
    i=i+1

diagrama_barras_dias = html.Div([
                    dcc.Slider(
                        id='slider_diagrama_de_barras_dias',
                        marks=bloques_slider,
                        min=0,
                        max=len(data_recolecta)-1,
                        value=0,
                        step=1,
                        updatemode='drag'
                    ),
                    html.Div(children=[
                        dcc.Graph(id='diagrama_de_barras_dias', style={'margin-top': 20}),
                        
                        dcc.Graph(id='test_dn_dias')
                    ])
                ], style={'margin-left': 40, 'margin-right': 40, 'margin-top': 20})

@app.callback([Output(component_id='diagrama_de_barras_dias', component_property='figure'),
              Output(component_id='test_dn_dias', component_property='figure')],
              Input('slider_diagrama_de_barras_dias', 'value'))
def display_diagrama_dias(value):
    
    #ACTUALIZAMOS EL GRAFICO DEBARRAS SEGUN EL SLIDER (value)
    dataset_dias = data_recolecta[value].copy(deep=True)
    
    i=0
    while i < len(dataset_dias):
        dataset_dias["fecha"][i] = datetime.datetime.strptime(dataset_dias["fecha"][i] + '-1', "%Y-%W-%w")
        i=i+1
    
    dataset_dias = dataset_dias[["fecha","recolecta"]].groupby('fecha').sum()
    dataset_dias.reset_index(inplace=True)
    

    #DIAGRAMA DE BARRAS
    fig={
        'data': [
            {'x': dataset_dias["fecha"],
             'y': dataset_dias["recolecta"], 
             'type': 'bar', 'name': 'Recolecta'}
        ],
        'layout': {
                'title': "Comienza la semana " + data_recolecta[value]["fecha"][0][-2::] + " de " + data_recolecta[value]["fecha"][0][0:4]
        }
    }

    
    #CUANTILES TEORICOS
    qq = stats.probplot(dataset_dias[dataset_dias.recolecta != 0]["recolecta"], dist='lognorm', sparams=(1))
    x = np.array([qq[0][0][0], qq[0][0][-1]])
    
    fig2 = go.Figure()
    fig2.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers')
    fig2.add_scatter(x=x, y=qq[1][1] + qq[1][0]*x, mode='lines')
    fig2.layout.update(showlegend=False)
    fig2.layout.update(title="Representación de cuantíles teóricos", title_x=0.5)
    
    
    
    
    return [fig, fig2]



#DIAGRAMA DE BARRAS POR MESES

#CREAMOS EL SLIDER CON LOS BLOQUES
diagrama_barras_meses = html.Div([
                    dcc.Slider(
                        id='slider_diagrama_de_barras_meses',
                        marks=bloques_slider,
                        min=0,
                        max=len(data_recolecta)-1,
                        value=0,
                        step=1,
                        updatemode='drag',
                    ),
                    html.Div(children=[
                        dcc.Graph(id='diagrama_de_barras_meses', style={'margin-top': 20}),
                        
                        dcc.Graph(id='test_dn_meses')
                    ])
                ], style={'margin-left': 40, 'margin-right': 40, 'margin-top': 20})

@app.callback([Output(component_id='diagrama_de_barras_meses', component_property='figure'),
              Output(component_id='test_dn_meses', component_property='figure')],
              Input('slider_diagrama_de_barras_meses', 'value'))
def display_diagrama_meses(value):
    
    #ACTUALIZAMOS EL GRAFICO DEBARRAS SEGUN EL SLIDER (value)
    
    dataset_meses = data_recolecta[value].copy(deep=True)
    #ACTUALIZAMOS LAS SEMANAS POR MESES
    i=0
    while i < len(dataset_meses):
        dataset_meses["fecha"][i] = datetime.datetime.strptime(dataset_meses["fecha"][i] + '-1', "%Y-%W-%w").strftime("%Y-%m")
        i=i+1
    
    dataset_meses = dataset_meses[["fecha","recolecta"]].groupby('fecha').sum()
    dataset_meses.reset_index(inplace=True)
    
    #DIAGRAMA DE BARRAS
    fig={
        'data': [
            {'x': dataset_meses["fecha"],
                'y': dataset_meses["recolecta"], 
                'type': 'bar', 'name': 'Recolecta'}
        ],
        'layout': {
            'title': "Comienza la semana " + data_recolecta[value]["fecha"][0][-2::] + " de " + data_recolecta[value]["fecha"][0][0:4]
        }
    }
    
    

    #CUANTILES TEORICOS
    
    qq = stats.probplot(dataset_meses["recolecta"], dist='lognorm', sparams=(1))
    x = np.array([qq[0][0][0], qq[0][0][-1]])
    
    fig2 = go.Figure()
    fig2.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers')
    fig2.add_scatter(x=x, y=qq[1][1] + qq[1][0]*x, mode='lines')
    fig2.layout.update(showlegend=False)
    fig2.layout.update(title="Representación de cuantíles teóricos", title_x=0.5)
    
    
    return [fig,fig2]



#DIAGRAMA DE BARRAS POR ANO
fechas_aux=[]

data_recolecta_aux = [] 

i=0
while i < len(data_recolecta):
    data_recolecta_aux.append(data_recolecta[i].copy(deep=True))
    i = i+1

dataset_anos = data_recolecta_aux[0]
i = 1
while i < len(data_recolecta_aux):
    dataset_anos = dataset_anos.append(data_recolecta_aux[i], ignore_index=True)
    i = i+1


#ACTUALIZAMOS LAS FECHAS POR EL ANO

i=0
while i < len(dataset_anos["fecha"]):
    dataset_anos["fecha"][i] = datetime.datetime.strptime(dataset_anos["fecha"][i] + '-1', "%Y-%W-%w").strftime("%Y")
    i=i+1

#CALCULAMOS EL CONTEO DE LAS RECOLECTAS
dataset_anos = dataset_anos[["fecha","recolecta"]].groupby('fecha').sum()
dataset_anos.reset_index(inplace=True)
    
#DIAGRAMA DE BARRAS
fig = dcc.Graph(
    id='diagrama_de_barras_recolecta_anos',
    figure={
        'data': [
            {'x': dataset_anos["fecha"],
             'y': dataset_anos["recolecta"], 
             'type': 'bar', 'name': 'Recolecta'}
            ],
        'layout': {
            'title': "Diagrama de barras por años"
        }
        }
    )

#CUANTILES TEORICOS
qq = stats.probplot(dataset_anos["recolecta"], dist='lognorm', sparams=(1))
x = np.array([qq[0][0][0], qq[0][0][-1]])
    
fig2 = go.Figure()
fig2.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers')
fig2.add_scatter(x=x, y=qq[1][1] + qq[1][0]*x, mode='lines')
fig2.layout.update(showlegend=False)
fig2.layout.update(title="Representación de cuantíles teóricos", title_x=0.5)

diagrama_barras_anos = html.Div([fig, dcc.Graph(id='test_dn_anos', figure=fig2)])





#DIAGRAMA DE BARRAS POR RECOLECTA
fechas_aux=[]

data_recolecta_aux = []


#CALCULA EL CONTEO Y LA FECHA
i=0
while i < len(data_recolecta):
    fecha_aux = data_recolecta[i]["fecha"][0][0:4]
    fecha_aux2 = int(fecha_aux)+1
    fechas_aux.append(str(fecha_aux)+"-"+str(fecha_aux2))
    data_recolecta_aux.append(data_recolecta[i]["recolecta"].sum())
    i = i+1

#DIAGRAMA DE BARRAS
fig = dcc.Graph(
    id='diagrama_de_barras_recolecta',
    figure={
        'data': [
            {'x': fechas_aux,
             'y': data_recolecta_aux, 
             'type': 'bar', 'name': 'Recolecta'}
            ],
        'layout': {
            'title': "Diagrama de barras por recolectas"
        }
        }
    )

#CUANTILES TEORICOS
qq = stats.probplot(data_recolecta_aux, dist='lognorm', sparams=(1))
x = np.array([qq[0][0][0], qq[0][0][-1]])
    
fig2 = go.Figure()
fig2.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers')
fig2.add_scatter(x=x, y=qq[1][1] + qq[1][0]*x, mode='lines')
fig2.layout.update(showlegend=False)
fig2.layout.update(title="Representación de cuantíles teóricos", title_x=0.5)

diagrama_barras_recolecta = html.Div([fig, dcc.Graph(id='test_dn_recolecta', figure=fig2)])



#INSERTAMOS TODOS LOS GRAFICOS EN EL DASHBOARD

ventanas.append(
    dcc.Tab(label='Diagramas de barras', children=[
        html.Div([
            html.H2(children="Diagramas de barras"),
            dcc.Tabs(
                [dcc.Tab(label='Diagrama de barras por días', children=[
                    diagrama_barras_dias
                ]),
                dcc.Tab(label='Diagrama de barras por meses', children=[
                    diagrama_barras_meses
                ]),
                dcc.Tab(label='Diagrama de barras por años', children=[
                    diagrama_barras_anos
                ]),
                dcc.Tab(label='Diagrama de barras por recolectas', children=[
                    diagrama_barras_recolecta
                ])]
            )
        ])
    ])
)








#VENTANA MATRIZ DE CORRELACION

data_recolecta_aux = [] 

i=0
while i < len(data_recolecta):
    data_recolecta_aux.append(data_recolecta[i].copy(deep=True))
    i = i+1
    

#USO LA SEMANA PASADA COMO REFERENCIA, ES DECIR, TODAS LAS COLUMNAS SERAN LA SIGUIENTE MENOS LA DE RECOLECTA

i = 0
while i < len(data_recolecta_aux):
    j=0
    while j < (len(data_recolecta_aux[i]) -1):
        data_recolecta_aux[i]['tmax'][j] = data_recolecta_aux[i]['tmax'][j+1]
        data_recolecta_aux[i]['tmed'][j] = data_recolecta_aux[i]['tmed'][j+1]
        data_recolecta_aux[i]['tmin'][j] = data_recolecta_aux[i]['tmin'][j+1]
        j = j +1
    i = i+1

#AGRUPAMOS LOS BLOQUES DEL DATASET
matriz_corr = data_recolecta_aux[0]
i = 1
while i < len(data_recolecta_aux):
    matriz_corr = matriz_corr.append(data_recolecta_aux[i], ignore_index=True)
    i = i+1


#ELIMINAMOS LAS SEMANAS DE RECOLECTA 0
matriz_corr = matriz_corr[matriz_corr.recolecta != 0]

#ELIMINAMOS NULOS
matriz_corr = matriz_corr.dropna()

#CALCULAMOS LA MATRIZ
z_recolecta = matriz_corr[['tmax', 'tmed', 'tmin', 'recolecta']].astype('float64').corr()
fig = go.Figure(data=go.Heatmap(
                    z=z_recolecta,
                    x=['tmax', 'tmed', 'tmin', 'recolecta'],
                    y=['tmax', 'tmed', 'tmin', 'recolecta'],
                    ),
                )

fig.update_layout(title={
                    "text" : "Matriz de correlación"
                    })
    
correlacion_grafico = dcc.Graph(figure = fig)

#INSERTAMOS EL GRAFICO
ventanas.append(
    dcc.Tab(label='Matriz de correlación', children=[
        html.Div([
            html.H2(children="Matriz de correlación"),
            dcc.Tabs(correlacion_grafico)
        ])
    ])
)








#VENTANA TABLA
ventanas_tablas = []

#ISERTO TODAS LAS TABLAS DEL DATASET EN EL CUADRO DE MANDO
i = 0
while i < len(data_recolecta):

    ventanas_tablas.append(
            dcc.Tab(label=data_recolecta[i]["fecha"][0], children=[
                html.H3(children="Semana " + data_recolecta[i]["fecha"][0][-2::] + " de " + data_recolecta[i]["fecha"][0][0:4]),
                dash_table.DataTable(
                    id='table_'+str(i),
                        columns=[{"name": j, "id": j}
                            for j in data_recolecta[i].columns],
                            data=data_recolecta[i].to_dict('records'),
                )
            ])
    )
    i = i+1
    

##Inserto la ventana

ventanas.append(
    
    dcc.Tab(label='Tabla', children=[
        html.H2(children="Dataset"),
        html.Div([
            dcc.Tabs(ventanas_tablas)
        ])
    ])

)



app.layout = html.Div([
                dcc.Tabs(ventanas)
            ])

if __name__ == '__main__':
    app.run_server(debug=True)
