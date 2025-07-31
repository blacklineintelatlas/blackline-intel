
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import unicodedata

st.set_page_config(page_title="BLACKLINE", layout="wide")

st.markdown("""
    <style>
    html, body, .main, .stApp, .block-container {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    .viewerBadge_container__1QSob, header, footer {
        display: none !important;
        visibility: hidden;
    }
    .stButton>button {
        background-color: #C3102E;
        color: white;
        font-weight: bold;
        border-radius: 4px;
    }
    thead tr th {
        background-color: #C3102E !important;
        color: white !important;
        border-bottom: 1px solid white;
    }
    tbody tr td {
        background-color: black;
        color: white;
        border: 1px solid white;
    }
    </style>
""", unsafe_allow_html=True)

logo_path = "blackline_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=160)
st.sidebar.markdown("## BLACKLINE SYSTEM")
st.sidebar.markdown("**Inteligencia Estratégica en Tiempo Real**")

st.markdown("<h1 style='text-align: center; color: white;'>BLACKLINE</h1><hr style='border: 1px solid #C3102E;'>", unsafe_allow_html=True)

data_path = os.path.join("..", "data", "alertas_geopoliticas.xlsx")

coords = {
    'ucrania': [48.3794, 31.1656],
    'iran': [32.4279, 53.688],
    'china': [35.8617, 104.1954],
    'israel': [31.0461, 34.8516],
    'argelia': [28.0339, 1.6596],
    'espana': [40.4637, -3.7492],
    'rusia': [61.5240, 105.3188],
    'estados unidos': [37.0902, -95.7129],
    'corea del norte': [40.3399, 127.5101],
    'palestina': [31.9522, 35.2332],
    'marruecos': [31.7917, -7.0926],
    'turquia': [38.9637, 35.2433],
    'francia': [46.6034, 1.8883],
    'alemania': [51.1657, 10.4515],
    'reino unido': [55.3781, -3.4360],
    'india': [20.5937, 78.9629],
    'pakistan': [30.3753, 69.3451],
    'venezuela': [6.4238, -66.5897]
}

def normalizar(texto):
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.strip()

if os.path.exists(data_path):
    df = pd.read_excel(data_path)
    df["pais_norm"] = df["País"].apply(normalizar)
    df["Latitud"] = df["pais_norm"].apply(lambda p: coords.get(p, [None, None])[0])
    df["Longitud"] = df["pais_norm"].apply(lambda p: coords.get(p, [None, None])[1])

    st.markdown("### Filtros de búsqueda")
    paises = sorted(df["País"].unique().tolist())
    claves = sorted(df["Palabra Clave"].unique().tolist())
    niveles = sorted(df["Nivel de Alerta"].unique().tolist())

    sel_pais = st.selectbox("Filtrar por país", ["Todos"] + paises)
    sel_clave = st.selectbox("Filtrar por palabra clave", ["Todos"] + claves)
    sel_nivel = st.selectbox("Filtrar por nivel de alerta", ["Todos"] + list(map(str, niveles)))

    if sel_pais != "Todos":
        df = df[df["País"] == sel_pais]
    if sel_clave != "Todos":
        df = df[df["Palabra Clave"] == sel_clave]
    if sel_nivel != "Todos":
        df = df[df["Nivel de Alerta"].astype(str) == sel_nivel]

    st.markdown("### Mapa estratégico", unsafe_allow_html=True)
    mapa = folium.Map(location=[25, 10], zoom_start=2, tiles="CartoDB dark_matter")

    for _, row in df.iterrows():
        lat, lon = row["Latitud"], row["Longitud"]
        nivel = int(row["Nivel de Alerta"])
        color = "green" if nivel == 1 else "orange" if nivel == 2 else "red"
        if pd.notna(lat) and pd.notna(lon):
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f"{row['País']} — Nivel {nivel}"
            ).add_to(mapa)

    st_data = st_folium(mapa, width=1300, height=600)
    st.markdown("### 📋 Alertas registradas")
    st.dataframe(df.drop(columns=['pais_norm']), use_container_width=True)
else:
    st.error("No se ha encontrado el archivo de alertas.")
