
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

def limpiar(texto):
    if isinstance(texto, str):
        return texto.encode('ascii', 'ignore').decode('ascii')
    return str(texto)

# Cargar datos
base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, "..", "data", "alertas_geopoliticas.xlsx")
logo_path = os.path.join(base_path, "blackline_logo.png")
output_path = os.path.join(base_path, "..", "data", "blackline_atlas_PRO.pdf")

df = pd.read_excel(data_path)
df['Fecha'] = pd.to_datetime(df['Fecha'])
df_ordenado = df.sort_values(by='Fecha', ascending=False).head(10)

class BlacklinePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Confidencial - BLACKLINE ATLAS © {datetime.now().year}', 0, 0, 'C')

pdf = BlacklinePDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Portada
pdf.add_page()
pdf.set_fill_color(0, 0, 0)
pdf.rect(0, 0, 210, 297, 'F')

if os.path.exists(logo_path):
    pdf.image(logo_path, x=75, y=40, w=60)

pdf.set_font("Arial", 'B', 24)
pdf.set_text_color(255, 255, 255)
pdf.set_y(120)
pdf.cell(0, 10, "BLACKLINE ATLAS", ln=True, align='C')

pdf.set_font("Arial", '', 14)
pdf.set_y(135)
pdf.cell(0, 10, "INTELLIGENCE FOR A COMPLEX WORLD", ln=True, align='C')

pdf.set_font("Arial", '', 12)
pdf.set_y(150)
pdf.set_text_color(200, 200, 200)
pdf.cell(0, 10, "Fecha de emision: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ln=True, align='C')

pdf.set_y(180)
pdf.set_text_color(195, 16, 46)
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, "CONFIDENCIAL", ln=True, align='C')

# Página de alertas
pdf.add_page()
pdf.set_text_color(0, 0, 0)
pdf.set_font("Arial", 'B', 16)
pdf.cell(0, 10, "INFORME DE ALERTAS RECIENTES", ln=True)
pdf.ln(5)

for index, row in df_ordenado.iterrows():
    pdf.set_font("Arial", 'B', 12)
    color = (0, 128, 0) if row['Nivel de Alerta'] == 1 else (255, 165, 0) if row['Nivel de Alerta'] == 2 else (195, 16, 46)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"{row['País']} - Nivel {row['Nivel de Alerta']}", ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 8, limpiar(f"TITULAR: {row['Titular']}"))
    pdf.cell(0, 8, limpiar(f"Palabra clave: {row['Palabra Clave']}"), ln=True)
    pdf.cell(0, 8, limpiar(f"Fecha: {row['Fecha'].strftime('%Y-%m-%d %H:%M:%S')}"), ln=True)
    pdf.ln(5)

# Guardar
pdf.output(output_path)
print("✅ Informe generado con exito en:", output_path)
