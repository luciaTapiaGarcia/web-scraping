import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# PASO 1 Obtener el HTML de la web 
# Url de la  pagina a descargar en este caso la pagina de worldometers con los datos del coronavirus
resource_url = "https://www.worldometers.info/coronavirus/"
# Hacemos la peticion a la pagina http get a la url 
response = requests.get(resource_url)
# Imprimimos el codigo de estado de la respuesta para verificar que se ha descargado correctamente
print("Codigo de estado:", response.status_code)

if response.status_code != 200:
    raise Exception("No se pudo descargar la página")

# PASO 2 Parsear el HTML con BeautifulSoup
# Creamos un objeto BeautifulSoup a partir del HTML descargado
soup = BeautifulSoup(response.text, "html.parser")

# luego con find buscamos la tabla que contiene los datos del coronavirus, esta tabla tiene un id "main_table_countries_today" lo hemos encontrado inspeccionando el codigo html de la pagina con las herramientas de desarrollo del navegador 
tabla = soup.find("table", id="main_table_countries_today")

print(tabla) 

# Creamos listas vacías para guardar los datos
paises = []
total_casos = []
total_muertes = []
total_recuperados = []

# Recorremos todas las filas de la tabla (tr = filas)
#find_all("tr") devuelve una lista de todas las filas de la tabla
for fila in tabla.find_all("tr")[1:]:  # [1:] para saltar el encabezado
    
    # Obtenemos todas las celdas de la fila (td = columnas)
    celdas = fila.find_all("td")
    
    # Comprobamos que la fila tenga datos válidos
    if len(celdas) > 4:
        
        # Guardamos los datos en cada lista
        paises.append(celdas[1].get_text(strip=True))  # nombre del país
        
        # Quitamos comas para poder convertir luego a número
        # sttip=True para eliminar espacios en blanco al inicio y al final
        #replace(",", "") para eliminar las comas de los números grandes
        total_casos.append(celdas[2].get_text(strip=True).replace(",", ""))
        total_muertes.append(celdas[3].get_text(strip=True).replace(",", ""))
        total_recuperados.append(celdas[4].get_text(strip=True).replace(",", ""))

    
import pandas as pd

# Creamos una tabla (DataFrame) con los datos
df = pd.DataFrame({
    "Pais": paises,
    #pd.to_numeric para convertir las cadenas de texto a números, 
    # 
    # errors="coerce" para convertir los valores no numéricos a NaN
    "Total_Casos": pd.to_numeric(total_casos, errors="coerce"),
    "Total_Muertes": pd.to_numeric(total_muertes, errors="coerce"),
    "Total_Recuperados": pd.to_numeric(total_recuperados, errors="coerce")
})

# Mostramos las primeras filas
print(df.head())

# Guardamos los datos en una base de datos SQLite
conn = sqlite3.connect("covid_data.db")
# to_sql para guardar el DataFrame en una tabla de la base de datos, 
# si la tabla ya existe se reemplaza, y no se guarda el índice del DataFrame como una columna
df.to_sql("covid_paises", conn, if_exists="replace", index=False)
conn.close()
print("Datos guardados correctamente en SQLite")