
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🛰️ BLACKLINE - Panel Estratégico")

# Cargar datos
@st.cache_data
def cargar_alertas():
    try:
        df1 = pd.read_excel("data/alertas_geopoliticas.xlsx")
    except:
        df1 = pd.DataFrame()
    try:
        df2 = pd.read_excel("data/alertas_gdelt.xlsx")
    except:
        df2 = pd.DataFrame()
    return df1, df2

alertas_newsapi, alertas_gdelt = cargar_alertas()

# Filtros
with st.sidebar:
    st.header("🎯 Filtros")
    paises = alertas_newsapi["País"].unique() if not alertas_newsapi.empty else []
    pais = st.selectbox("País", ["Todos"] + list(paises))
    palabra = st.text_input("Buscar palabra clave")

# Mapa
m = folium.Map(location=[20,0], zoom_start=2)

if not alertas_gdelt.empty:
    for _, row in alertas_gdelt.iterrows():
        folium.CircleMarker(
            location=[row["Lat"], row["Lon"]],
            radius=5,
            popup=row.get("Actor1", "Evento"),
            color="red",
            fill=True
        ).add_to(m)

st.subheader("🌍 Mapa de Alertas")
st_folium(m, width=1200, height=600)

# Tabla filtrada
st.subheader("📋 Noticias Detalladas")

if not alertas_newsapi.empty:
    df_filtrado = alertas_newsapi.copy()
    if pais != "Todos":
        df_filtrado = df_filtrado[df_filtrado["País"] == pais]
    if palabra:
        df_filtrado = df_filtrado[df_filtrado["Titular"].str.contains(palabra, case=False, na=False)]
    st.dataframe(df_filtrado)
else:
    st.warning("Sin alertas cargadas desde NewsAPI.")
