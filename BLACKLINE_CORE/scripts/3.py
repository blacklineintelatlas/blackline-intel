
import requests
import yaml
import pandas as pd
import time
from datetime import datetime

# Cargar clave API
with open('C:/Users/dondriano/Desktop/BLACKLINE_SYSTEM/BLACKLINE_CORE/configuracion/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
api_key = config['newsapi_key']

# Países estratégicos actualizados
countries = {
    'España': 'Spain', 'Ucrania': 'Ukraine', 'Rusia': 'Russia', 'Estados Unidos': 'United States',
    'China': 'China', 'Irán': 'Iran', 'Corea del Norte': 'North Korea', 'Israel': 'Israel',
    'Palestina': 'Palestine', 'Marruecos': 'Morocco', 'Argelia': 'Algeria', 'Turquía': 'Turkey',
    'Francia': 'France', 'Alemania': 'Germany', 'Reino Unido': 'United Kingdom',
    'Venezuela': 'Venezuela', 'India': 'India', 'Pakistán': 'Pakistan'
}

# Palabras clave estratégicas actualizadas
keywords = [
    'attack', 'missile', 'military', 'conflict', 'explosion',
    'terrorism', 'strike', 'border clash', 'nuclear', 'embassy',
    'assassination', 'diplomatic crisis', 'ambush', 'sniper', 'evacuation',
    'Putin', 'Biden', 'China', 'Israel', 'Iran', 'Taiwan', 'Hamas',
    'missile launch', 'airstrike', 'soldier killed', 'diplomat killed',
    'election', 'vote', 'fraud', 'boycott', 'opposition', 'referendum'
]

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
                    nivel = min(keywords.index(keyword) + 1, 5)
                    nuevas_alertas.append([fecha_actual, nombre, titulo, keyword, nivel])
            break  # solo primera coincidencia por país

    if nuevas_alertas:
        df_nuevo = pd.DataFrame(nuevas_alertas, columns=["Fecha", "País", "Titular", "Palabra Clave", "Nivel de Alerta"])
        df_total = pd.concat([df_existente, df_nuevo], ignore_index=True)
        df_total.to_excel(excel_path, index=False)
        print(f"[{fecha_actual}] ✅ Nuevas alertas guardadas: {len(nuevas_alertas)}")
    else:
        print(f"[{fecha_actual}] ⚠️ Sin nuevas alertas.")



# 🔁 Integración con GDELT
import zipfile
import io

def obtener_alertas_gdelt():
    try:
        url_update = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
        nombre_archivo = requests.get(url_update).text.strip().split(" ")[2]
        url_descarga = f"http://data.gdeltproject.org/gdeltv2/{nombre_archivo}"

        response = requests.get(url_descarga)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    df = pd.read_csv(f, sep='\t', header=None)

        df_alertas = df[[0, 1, 26, 27, 53, 57, 58]]
        df_alertas.columns = ["GlobalEventID", "Day", "Actor1", "Actor2", "EventCode", "Lat", "Lon"]

        df_alertas["Fecha"] = pd.to_datetime(df_alertas["Day"], format="%Y%m%d")
        df_alertas = df_alertas.dropna(subset=["Lat", "Lon"])
        df_alertas = df_alertas[df_alertas["EventCode"].astype(str).str.startswith(('1','2','3','4'))]

        df_alertas.to_excel("../data/alertas_gdelt.xlsx", index=False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ GDELT actualizado con {len(df_alertas)} alertas.")
    except Exception as e:
        print(f"❌ Error al obtener alertas de GDELT: {e}")


# Bucle infinito cada 15 minutos
print("🛰️ BLACKLINE Daemon iniciado. Escaneando el mundo cada 15 minutos...")
while True:
    obtener_alertas()
    time.sleep(900)
