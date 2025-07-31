import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os, unicodedata
from fpdf import FPDF
from datetime import datetime

# ---------- CONFIG GLOBAL ----------
st.set_page_config(page_title="BLACKLINE", layout="wide")
st.markdown("""
    <style>
    html, body, .stApp {background:#000;color:#FFF;}
    .viewerBadge_container__1QSob, header, footer{display:none !important;}
    .stButton>button{background:#C3102E;color:#FFF;font-weight:bold;border-radius:4px;}
    thead tr th{background:#C3102E !important;color:#FFF !important;border-bottom:1px solid #FFF;}
    tbody tr td{background:#000;color:#FFF;border:1px solid #FFF;}
    </style>""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
logo_path = "blackline_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=160)
st.sidebar.markdown("## BLACKLINE SYSTEM")
st.sidebar.markdown("**Inteligencia Estratégica en Tiempo Real**")

# ---------- TÍTULO ----------
st.markdown("<h1 style='text-align:center;color:white;'>BLACKLINE</h1>"
            "<hr style='border:1px solid #C3102E;'>",
            unsafe_allow_html=True)

# ---------- PATH EXCEL ----------
data_path = os.path.join("..", "data", "alertas_geopoliticas.xlsx")

# ---------- FUNCIÓN AUX ----------
def normalizar(texto):
    return unicodedata.normalize('NFKD', str(texto).lower()).encode('ascii','ignore').decode('ascii').strip()

# ---------- COORDS ----------
coords = {
    'ucrania':[48.3794,31.1656], 'iran':[32.4279,53.688], 'china':[35.8617,104.1954],
    'israel':[31.0461,34.8516], 'argelia':[28.0339,1.6596], 'espana':[40.4637,-3.7492],
    'rusia':[61.5240,105.3188], 'estados unidos':[37.0902,-95.7129],
    'corea del norte':[40.3399,127.5101], 'palestina':[31.9522,35.2332],
    'marruecos':[31.7917,-7.0926], 'turquia':[38.9637,35.2433], 'francia':[46.6034,1.8883],
    'alemania':[51.1657,10.4515], 'reino unido':[55.3781,-3.4360],
    'india':[20.5937,78.9629], 'pakistan':[30.3753,69.3451],
    'venezuela':[6.4238,-66.5897],'Mexico': (23.6345, -102.5528), 'México': (23.6345, -102.5528)
}

# ---------- CARGA / CREACIÓN DF ----------
if os.path.exists(data_path):
    try:
        df = pd.read_excel(data_path)
        # columnas extra
        df["pais_norm"] = df["País"].apply(normalizar)
        df["Latitud"]   = df["pais_norm"].apply(lambda p: coords.get(p,[None,None])[0])
        df["Longitud"]  = df["pais_norm"].apply(lambda p: coords.get(p,[None,None])[1])
    except Exception as e:
        st.error(f"Error leyendo Excel: {e}")
        df = pd.DataFrame(columns=["Fecha","País","Titular","Palabra Clave","Nivel de Alerta",
                                   "Latitud","Longitud","pais_norm"])
else:
    st.error("El archivo de datos no se encuentra.")
    df = pd.DataFrame(columns=["Fecha","País","Titular","Palabra Clave","Nivel de Alerta",
                               "Latitud","Longitud","pais_norm"])

# ---------- FILTROS ----------
st.markdown("### Filtros de búsqueda")
paises  = sorted(df["País"].unique().tolist())
claves  = sorted(df["Palabra Clave"].unique().tolist())
niveles = sorted(df["Nivel de Alerta"].unique().tolist())

sel_pais  = st.selectbox("Filtrar por país", ["Todos"]+paises)
sel_clave = st.selectbox("Filtrar por palabra clave", ["Todos"]+claves)
sel_nivel = st.selectbox("Filtrar por nivel de alerta", ["Todos"]+list(map(str,niveles)))

if sel_pais!="Todos":   df = df[df["País"]==sel_pais]
if sel_clave!="Todos":  df = df[df["Palabra Clave"]==sel_clave]
if sel_nivel!="Todos":  df = df[df["Nivel de Alerta"].astype(str)==sel_nivel]

# ---------- MAPA ----------
st.markdown("### Mapa estratégico")
mapa = folium.Map(location=[25,10], zoom_start=2, tiles="CartoDB dark_matter")
for _,row in df.iterrows():
    lat,lon=row["Latitud"],row["Longitud"]
    if pd.notna(lat) and pd.notna(lon):
        nivel=int(row["Nivel de Alerta"])
        color = "green" if nivel==1 else "orange" if nivel==2 else "red"
        folium.CircleMarker(location=[lat,lon],radius=8,color=color,fill=True,
                            fill_color=color,fill_opacity=0.7,
                            popup=f"{row['País']} — Nivel {nivel}").add_to(mapa)
st_folium(mapa,width=1300,height=600)

# ---------- TABLA ----------
st.markdown("### 📋 Alertas registradas")
st.dataframe(df.drop(columns=["pais_norm"]),use_container_width=True)

# ---------- EXPORTAR PDF ----------
if st.button("📤 Exportar informe PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",'B',14)
    pdf.cell(0,10,"Informe de Alertas BLACKLINE",ln=True,align="C")
    pdf.set_font("Arial","",10)
    pdf.ln(5)
    pdf.cell(0,10,f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",ln=True)

    def clean(t): return str(t).encode('ascii','ignore').decode('ascii')

    for _,row in df.iterrows():
        pdf.ln(4)
        pdf.set_font("Arial",'B',11)
        pdf.cell(0,8,clean(f"{row['País']} — Nivel {row['Nivel de Alerta']}"),ln=True)
        pdf.set_font("Arial","",10)
        pdf.multi_cell(0,6,clean(row["Titular"]))
        pdf.cell(0,6,f"Palabra clave: {clean(row['Palabra Clave'])}",ln=True)
        pdf.cell(0,6,f"Fecha: {clean(row['Fecha'])}",ln=True)

    out_name = f"blackline_atlas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(os.path.join("..","data",out_name))
    st.success(f"Informe exportado como {out_name}")
