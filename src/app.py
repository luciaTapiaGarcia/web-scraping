import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

resource_url = "https://www.imdb.com/chart/top/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(resource_url, headers=headers)

if response:
    html = response.text
    print("HTML descargado correctamente.")


soup = BeautifulSoup(html, "html.parser")

tabla = soup.find("tbody", class_="lister-list")

titulos = []
años = []
ranking = []

for fila in tabla.find_all("tr"):
    # Título de la película
    titulo = fila.find("td", class_="titleColumn").a.text
    # Año de la película
    año = fila.find("span", class_="secondaryInfo").text.strip("()")
    # Rating de IMDb
    rating = fila.find("td", class_="ratingColumn imdbRating").strong.text
    
    # Guardamos los datos en las listas
    titulos.append(titulo)
    años.append(año)
    ratings.append(float(rating))


df = pd.DataFrame({
    "Titulo": titulos,
    "Año": años,
    "Rating": ratings
})
df["Año"] = df["Año"].astype(int)
print(df.head())

# Conectamos a SQLite (crea el archivo si no existe)
conn = sqlite3.connect("peliculas.db")
cursor = conn.cursor()

# Creamos la tabla (si no existe)
cursor.execute("""
CREATE TABLE IF NOT EXISTS peliculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    año INTEGER,
    rating REAL
)
""")

# Insertamos los datos
for i in range(len(df)):
    cursor.execute("""
    INSERT INTO peliculas (titulo, año, rating) VALUES (?, ?, ?)
    """, (df["Titulo"][i], df["Año"][i], df["Rating"][i]))

# Guardamos los cambios y cerramos la conexión
conn.commit()
conn.close()

print("Datos guardados en SQLite correctamente")

# Histograma de ratings
plt.hist(df["Rating"], bins=10, color="skyblue", edgecolor="black")
plt.title("Distribución de Ratings de Películas")
plt.xlabel("Rating")
plt.ylabel("Cantidad de Películas")
plt.show()

# Gráfico de películas por década
df["Década"] = (df["Año"] // 10) * 10
decada_counts = df.groupby("Década").size()

decada_counts.plot(kind="bar", color="orange")
plt.title("Cantidad de películas por década")
plt.xlabel("Década")
plt.ylabel("Cantidad")
plt.show()

# Top 10 películas mejor valoradas
top10 = df.sort_values("Rating", ascending=False).head(10)
plt.barh(top10["Titulo"], top10["Rating"], color="green")
plt.title("Top 10 películas mejor valoradas")
plt.xlabel("Rating")
plt.ylabel("Película")
plt.gca().invert_yaxis()  # Para que la más alta esté arriba
plt.show()