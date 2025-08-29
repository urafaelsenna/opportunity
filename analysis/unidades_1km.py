# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
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
            "cidade_1": row1["cidade_cdn"],
            "estado_1": row1["estado_cdn"],
            "academia_2": row2["nome"],
            "rede_2": row2["rede"],
            "cidade_2": row2["cidade_cdn"],
            "estado_2": row2["estado_cdn"],
            "distancia_km": round(dist, 3)
        })

df_proximas = pd.DataFrame(pares_proximos)

# Estatísticas gerais
total_pares = len(df_proximas)
print(f"📊 Total de pares de academias próximas (<{RAIO_KM} km): {total_pares}")

# Estatísticas por rede (quantos pares envolvem cada rede)
prox_por_rede = df_proximas.groupby(["rede_1", "rede_2"]).size().reset_index(name="quantidade")
print("\n📌 Pairs de academias por rede:")
print(prox_por_rede)

# Estatísticas por cidade
prox_por_cidade = df_proximas.groupby(["cidade_1"]).size().reset_index(name="quantidade")
print("\n📌 Quantidade de pares por cidade:")
print(prox_por_cidade)

# Exporta CSV para análise detalhada
df_proximas.to_csv("./exportados/academias_proximas_1km.csv", index=False)
print("\n✅ CSV gerado: exportados/academias_proximas_1km.csv")
