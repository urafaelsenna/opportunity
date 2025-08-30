# analysis/plot_unidades_density.py

import pandas as pd
import sqlite3
import plotly.express as px
import os

# Caminho do banco e pasta de export
DB_PATH = "./unidades.db"
EXPORT_DIR = "./exportados"
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("""
    SELECT id, rede, nome, endereco, latitude, longitude, estado_cdn, cidade_cdn
    FROM unidades
""", conn)
conn.close()

# Converter latitude e longitude para float
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

# Criar density mapbox (heatmap de densidade)
fig = px.density_mapbox(
    df,
    lat='latitude',
    lon='longitude',
    z=None,  # Pode-se usar z='quantidade', mas None para densidade simples
    radius=15,  # Raio de influência dos pontos (ajuste visual)
    center=dict(lat=-14.2350, lon=-51.9253),  # Centro do Brasil
    zoom=3.5,
    mapbox_style='open-street-map',
    hover_data=['nome', 'rede', 'endereco', 'cidade_cdn', 'estado_cdn']
)

# Layout
fig.update_layout(
    title='Mapa de densidade de unidades de academias no Brasil',
    margin={"r":0,"t":50,"l":0,"b":0},
    height=700
)

# Exportar HTML
output_html = os.path.join(EXPORT_DIR, "mapa_density_unidades.html")
fig.write_html(output_html)
print(f"✅ Mapa de densidade exportado em {output_html}")

# Mostrar interativo
fig.show()
