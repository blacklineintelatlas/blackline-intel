
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# Configuración
st.set_page_config(page_title="BLACKLINE KAI", layout="wide")

# Cargar datos
data_path = os.path.join("..", "data", "alertas_geopoliticas.xlsx")
df = pd.read_excel(data_path)

# Filtros
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

# Mapa
st.markdown("### Mapa estratégico")
mapa = folium.Map(location=[25, 10], zoom_start=2, tiles="CartoDB dark_matter")

for _, row in df.iterrows():
    lat, lon = row.get("Latitud"), row.get("Longitud")
    if pd.notna(lat) and pd.notna(lon):
        color = "green" if row["Nivel de Alerta"] == 1 else "orange" if row["Nivel de Alerta"] == 2 else "red"
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"{row['País']} — Nivel {row['Nivel de Alerta']}"
        ).add_to(mapa)

st_folium(mapa, width=1300, height=600)

# Tabla
st.markdown("### 📋 Alertas registradas")
st.dataframe(df, use_container_width=True)
