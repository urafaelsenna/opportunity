# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import folium
from geopy.distance import geodesic
from itertools import combinations

# Conecta ao banco
conn = sqlite3.connect("./unidades.db")
df = pd.read_sql_query("""
    SELECT id, rede, nome, endereco, latitude, longitude, bairro_cdn, cidade_cdn, estado_cdn, pais_cdn
    FROM unidades
""", conn)
conn.close()

# Filtra registros com coordenadas válidas
df = df.dropna(subset=["latitude", "longitude"])
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)
df["coords"] = list(zip(df.latitude, df.longitude))

# Define raio de proximidade (1 km)
RAIO_KM = 1.0

# Lista para armazenar pares de academias próximas
pares_proximos = []

# Calcula distância entre todas as combinações possíveis
for (idx1, row1), (idx2, row2) in combinations(df.iterrows(), 2):
    dist = geodesic(row1["coords"], row2["coords"]).km
    if dist <= RAIO_KM:
        pares_proximos.append({
            "academia_1": row1["nome"],
            "rede_1": row1["rede"],
            "coords_1": row1["coords"],
            "academia_2": row2["nome"],
            "rede_2": row2["rede"],
            "coords_2": row2["coords"],
            "distancia_km": round(dist, 3)
        })

df_proximas = pd.DataFrame(pares_proximos)

# Cria mapa centrado no Brasil
mapa = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)

# Define cores por rede
cores = {}
paleta = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
          'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink']
for i, rede in enumerate(df['rede'].unique()):
    cores[rede] = paleta[i % len(paleta)]

# Adiciona marcadores
for _, row in df.iterrows():
    folium.CircleMarker(
        location=row["coords"],
        radius=5,
        color=cores[row["rede"]],
        fill=True,
        fill_opacity=0.7,
        popup=f"{row['nome']} ({row['rede']})"
    ).add_to(mapa)

# Adiciona linhas conectando pares próximos
for _, row in df_proximas.iterrows():
    folium.PolyLine(
        locations=[row["coords_1"], row["coords_2"]],
        color="gray",
        weight=1,
        opacity=0.5,
        popup=f"{row['academia_1']} ↔ {row['academia_2']} ({row['distancia_km']} km)"
    ).add_to(mapa)

# Salva mapa
mapa.save("./exportados/mapa_academias_proximas.html")
print("✅ Mapa gerado: exportados/mapa_academias_proximas.html")
