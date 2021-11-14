import pandas
import os
import openpyxl
import math
import numpy

def getCosechaData(file):
    
    cosecha = pandas.read_excel(os.path.join(
	    "Resumen porduccion m2 2016-2020.xlsx"), engine='openpyxl', usecols="B:K")
    
    # Seleccionamos las filas que contienen las fechas (fechas) y las cabeceras (data)
    fechas = cosecha.iloc[4];
    data = cosecha.iloc[11];
    
    # Recortamos la tabla y eliminamos las celdas que ya no son útiles
    cosecha = cosecha.truncate(before=12);
    cosecha = cosecha.reset_index(drop=True);
    
    i = 0;
    while i < len(data):
        data[i] = "fecha";
        data[i+1] = "recolecta";
        i=i+2;

	# Introducimos en el dataframe las cabeceras
    cosecha.columns = data
    cosecha.columns.name = "Index";

	# Dividimos en bloques
    bloques = [];

    i = 0;
    while i < len(data):
        j = i + 1;
        bloques.append(cosecha.iloc[:, [i, j]]);
        i = i+2;

	# Eliminamos los nulos en la parte de recolecta
    i = 0;
    while i < len(bloques):
        bloques[i] = bloques[i][bloques[i]["recolecta"].notna()];
        i= i+1;

	# Finalizamos la enumeración de las fechas para cada bloque
    i = 0;
    while i < len(bloques):
        aux = -1; j = 0;

        while j < len(bloques[i]):
            if aux != -1 and math.isnan(bloques[i]["fecha"][j]):
                bloques[i]["fecha"][j] = aux + 1

            aux = bloques[i]["fecha"][j]
            j = j + 1

        i = i+1

	# Renombramos el formato de fecha
    i = 0;  k = 1;
    second = False;
    
    while i < len(bloques):
        j= 0;
        while j < len(bloques[i]):
            
            if second == True:
                fecha = fechas[k].year + 1
            else:
                fecha = fechas[k].year
            
            if int(bloques[i]["fecha"][j]) > 9:
                bloques[i]["fecha"][j] = str(fecha) + "-" + str(bloques[i]["fecha"][j])
            else:
                
                if second == False:
                    second = True
                    fecha = fechas[k].year + 1
                
                bloques[i]["fecha"][j] = str(fecha) + "-0" + str(bloques[i]["fecha"][j])
                
                
            j=j+1
        
        second = False
        i=i+1
        k=k+2

    

    i=0
    j=1
    while(i<len(bloques)):
        
        primSemana = fechas[j].isocalendar()[1]
        ultSemana = bloques[i]["fecha"][0]
        
        tam = (int(ultSemana[-2::]) - int(primSemana))
        
        auxR = []
        auxR.append(ultSemana[0:5] + str(primSemana+1))
        
        n=1
        while n < tam-1:
            auxR.append(ultSemana[0:5] + str((int(auxR[n-1][-2::]) + 1)))
            n=n+1
        
        
        
        
        data = {'fecha':  auxR,
        'recolecta': numpy.zeros(len(auxR))
        }
        
        auxDic = pandas.DataFrame.from_dict(data)
        
        bloques[i] = bloques[i].append(auxDic, ignore_index=True)
        bloques[i].sort_values('fecha',inplace=True, ascending=True)
        bloques[i] = bloques[i].reset_index()
        
        j=j+2;
        i=i+1


	# Guardamos todo en un diccionario y usamos como clave las fechas
    result = {}
    i=1;
    for bloque in bloques:
        result[str(fechas[i])[0:10]]=bloque.to_dict();	#Cambio de fecha a String: str(fechas[i])[0:10]
        i=i+2;

    return bloques;
