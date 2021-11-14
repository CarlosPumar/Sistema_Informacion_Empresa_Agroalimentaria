import aemetapi
import extraccion_datos
from ModelSignal import ModelSignal

import numpy as np
import pandas

from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates

import statsmodels.api as sm
import datetime
from datetime import timedelta

file = 'Resumen porduccion m2 2016-2020.xlsx'

estacion = "6293X"
fecha_ini = "2016-01-06T00:00:00UTC"
fecha_fin = "2021-01-03T23:59:59UTC"


def joinData(dataWeather, dataCosecha):

    result = []

    for dat in dataCosecha:
        
        df = pandas.merge(dataWeather, dat, on="fecha", how="right")

        df['sort'] = df["fecha"].replace({'-':''}, regex=True)
        
        df['sort'] = df['sort'].str.extract('(\d+)', expand=False).astype(int)
        df.sort_values('sort',inplace=True, ascending=True)
        df = df.drop('sort', axis=1)
        
        result.append(df)

    return result

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)   

def splitFecha(fecha):
    return fecha.split(sep="-")

def process(row):    
    
    year = int(row[0])
    week = int(row[1])
    
    dt = iso_to_gregorian(year, week, 1)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

def getProduction(data):
    
    listProduccion = []
    p = 0
        
    size = len(data['recolecta'])
    
    i = 0
    
    while i < size:
        p+=data['recolecta'][i]
        listProduccion.append(p)
        i+=1
    
    data['acumulado'] = listProduccion
    
    return data
    
def getAcumulado(data):
    
    size = len(data)
    i=0
    while i < size:
        data[i] = getProduction(data[i])
        i+=1
    
    return data


def main():
    
    dataWeather = aemetapi.getDataApi(estacion, fecha_ini, fecha_fin)
    dataWeather = aemetapi.processingWeatherData(dataWeather)
    
    dataCosecha = extraccion_datos.getCosechaData(file)
    
    
    data = joinData(dataWeather, dataCosecha)
    
    res_acumulado = getAcumulado(data)
    
    return data



