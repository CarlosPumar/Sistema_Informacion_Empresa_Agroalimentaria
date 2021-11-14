import http.client
import pandas
import json
from datetime import datetime

#Conectamos con la API
#Establecemos parámetros de conexión

#Establecemos parametros de pandas
pandas.options.mode.chained_assignment = None;

def getDataApi(estacion, fecha_ini, fecha_fin):

    conn = http.client.HTTPSConnection("opendata.aemet.es")
    apikey = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb3NlamJhcm5ldG9AZ21haWwuY29tIiwianRpIjoiODI4MzA5NzgtMWI4Yi00YzI2LThkOGMtMzA1ZjAwMTdhODEzIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2MTk4MDAxMDEsInVzZXJJZCI6IjgyODMwOTc4LTFiOGItNGMyNi04ZDhjLTMwNWYwMDE3YTgxMyIsInJvbGUiOiIifQ.sshPYw85B8Eng5mjl3VS28cyfV96OWj9ZX2P7KmHej8"
    
    headers = {
        'cache-control': "no-cache"
        }
    
    
    #Enviamos la petición
    request_str = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/"+fecha_ini+"/fechafin/"+fecha_fin+"/estacion/"+estacion+"/?api_key="+apikey
    
    
    conn.request("GET", request_str, headers=headers)
    
    
    #Obtenemos el resultado
    res = conn.getresponse()
    data = res.read()
    
    #Casteamos el JSON
    data_decode = json.loads(data.decode("utf-8"))
    
    #Enviamos la peticion
    conn.request("GET", data_decode['datos'], headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    #Cargamos los datos
    final_data = json.loads(data.decode("utf-8"))
    
    return pandas.DataFrame.from_dict(final_data)

def processingWeatherData(data):
    
    #Lectura de los datos
    #Cargamos en un dataFrame (data)
    # data = pandas.DataFrame.from_dict(final_data)
    
    #Seleccionamos los atributos necesarios
    data = data[["fecha", "tmax", "tmin", "tmed"]]
    
    #Cambiamos las comas por puntos en los valores float
    data["tmax"] = data["tmax"].replace({',':'.'}, regex=True);
    data["tmin"] = data["tmin"].replace({',':'.'}, regex=True);
    data["tmed"] = data["tmed"].replace({',':'.'}, regex=True);
    
    #Cambiamos las fechas por el siguiente formato: (Año-Número de la semana)
    i = 0;
    while i < len(data):
        date = datetime.strptime(data["fecha"][i], '%Y-%m-%d')

        if date.isocalendar()[1] >= 10:
            data["fecha"][i] = (str(date.year) + "-" +  str(date.isocalendar()[1]))
        else:
            data["fecha"][i] = (str(date.year) + "-0" +  str(date.isocalendar()[1]))
        i=i+1
    
    #Casteamos a float
    data = data.astype({'tmax': 'float64', 'tmin': 'float64', 'tmed': 'float64'})
    
    maximos = data[["fecha","tmax"]].groupby('fecha').max()
    minimos = data[["fecha","tmin"]].groupby('fecha').min()
    media = data[["fecha","tmed"]].groupby('fecha').mean()
    
    maximos.reset_index(inplace=True)
    minimos.reset_index(inplace=True)
    media.reset_index(inplace=True)
    
    df = pandas.concat( [maximos, minimos],axis=0,ignore_index=True)
    df = pandas.concat( [df, media],axis=0,ignore_index=True)
    df = df.groupby('fecha').sum().reset_index()
    
    # df = df.set_index('fecha')
    
    return df
