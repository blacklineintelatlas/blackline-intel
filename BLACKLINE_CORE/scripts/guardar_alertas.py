
import requests
import yaml
import pandas as pd
from datetime import datetime

# 1. Cargar clave API desde archivo config
with open('C:/Users/dondriano/Desktop/BLACKLINE_SYSTEM/BLACKLINE_CORE/configuracion/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
api_key = config['newsapi_key']

# 2. Lista de países a analizar
countries = {
    'Ucrania': 'Ukraine',
    'Irán': 'Iran',
    'China': 'China',
    'Argelia': 'Algeria',
    'Israel': 'Israel'
}

# 3. Palabras clave que indican alerta
keywords = ['attack', 'protest', 'military', 'bomb', 'war', 'strike']

# 4. Almacenar resultados
data = []
fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 5. Extraer titulares por país
for nombre, pais in countries.items():
    for keyword in keywords:
        url = f"https://newsapi.org/v2/everything?q={keyword}+{pais}&sortBy=publishedAt&apiKey={api_key}&language=en&pageSize=1"
        response = requests.get(url)
        noticias = response.json()

        if noticias.get("articles"):
            article = noticias["articles"][0]
            titulo = article["title"]
            nivel = keywords.index(keyword) + 1  # Nivel de alerta según gravedad
            data.append([fecha, nombre, titulo, keyword, nivel])
        break

# 6. Guardar en Excel
df = pd.DataFrame(data, columns=["Fecha", "País", "Titular", "Palabra Clave", "Nivel de Alerta"])
df.to_excel("../data/alertas_geopoliticas.xlsx", index=False)
print("✅ Archivo Excel creado con éxito: alertas_geopoliticas.xlsx")
