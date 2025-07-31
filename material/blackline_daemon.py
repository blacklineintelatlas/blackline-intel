
import requests
import yaml
import pandas as pd
import time
from datetime import datetime

# Cargar clave API
with open('C:/Users/dondriano/Desktop/BLACKLINE_SYSTEM/BLACKLINE_CORE/configuracion/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
api_key = config['newsapi_key']

# Países y keywords
countries = {
    'Ucrania': 'Ukraine',
    'Irán': 'Iran',
    'China': 'China',
    'Argelia': 'Algeria',
    'Israel': 'Israel'
}
keywords = ['attack', 'protest', 'military', 'bomb', 'war', 'strike']
excel_path = '../data/alertas_geopoliticas.xlsx'

# Función para obtener noticias nuevas
def obtener_alertas():
    try:
        df_existente = pd.read_excel(excel_path)
    except FileNotFoundError:
        df_existente = pd.DataFrame(columns=["Fecha", "País", "Titular", "Palabra Clave", "Nivel de Alerta"])

    nuevas_alertas = []
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for nombre, pais in countries.items():
        for keyword in keywords:
            url = f"https://newsapi.org/v2/everything?q={keyword}+{pais}&sortBy=publishedAt&apiKey={api_key}&language=en&pageSize=1"
            response = requests.get(url)
            noticias = response.json()

            if noticias.get("articles"):
                article = noticias["articles"][0]
                titulo = article["title"]

                # Verificar duplicados
                duplicado = df_existente[
                    (df_existente['País'] == nombre) &
                    (df_existente['Titular'] == titulo)
                ]

                if duplicado.empty:
                    nivel = keywords.index(keyword) + 1
                    nuevas_alertas.append([fecha_actual, nombre, titulo, keyword, nivel])
            break  # solo primera coincidencia por país

    if nuevas_alertas:
        df_nuevo = pd.DataFrame(nuevas_alertas, columns=["Fecha", "País", "Titular", "Palabra Clave", "Nivel de Alerta"])
        df_total = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_total.to_excel(excel_path, index=False)
        print(f"[{fecha_actual}] ✅ Nuevas alertas guardadas: {len(nuevas_alertas)}")
    else:
        print(f"[{fecha_actual}] ⚠️ Sin nuevas alertas.")

# Bucle infinito cada 15 minutos
print("🛰️ BLACKLINE Daemon iniciado. Escaneando el mundo cada 15 minutos...")
while True:
    obtener_alertas()
    time.sleep(900)  # 15 minutos
