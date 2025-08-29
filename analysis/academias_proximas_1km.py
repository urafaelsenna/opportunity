# analysis/proximidade_academias.py
import sqlite3
import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import os

DB_PATH = './unidades.db'
CSV_OUT = './exportados/unidades_proximas.csv'
PNG_ALL = './exportados/proximidade_geral.png'
PNG_REDE = './exportados/proximidade_rede.png'

# --- Criar pasta de exportados caso não exista ---
os.makedirs('./exportados', exist_ok=True)

# --- 1️⃣ Ler dados do banco ---
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT id, rede, nome, latitude, longitude, estado_cdn FROM unidades", conn)
conn.close()

# --- 2️⃣ Calcular número de academias próximas dentro de 1 km ---
def calcular_proximidade(df, raio_km=1.0):
    proximidade = []
    for i, a1 in df.iterrows():
        count = 0
        for j, a2 in df.iterrows():
            if i != j:
                dist = geodesic((a1.latitude, a1.longitude), (a2.latitude, a2.longitude)).km
                if dist <= raio_km:
                    count += 1
        proximidade.append(count)
    df['academias_proximas_1km'] = proximidade
    return df

df = calcular_proximidade(df)

# --- 3️⃣ Exportar CSV ---
df.to_csv(CSV_OUT, index=False)
print(f"✅ CSV exportado em {CSV_OUT}")

# --- 4️⃣ Gráfico geral por rede ---
plt.figure(figsize=(12, 6))
cores = {'Bluefit':'blue', 'SmartFit':'red', 'Selfit':'green'}
for rede in df['rede'].unique():
    subset = df[df['rede']==rede]
    plt.scatter(subset['longitude'], subset['latitude'], 
                label=rede, alpha=0.7, s=subset['academias_proximas_1km']*10 + 20)

plt.title("Academias no Brasil e proximidade dentro de 1 km (tamanho ~ nº de academias próximas)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(True)
plt.savefig(PNG_ALL, dpi=300)
plt.close()
print(f"✅ Gráfico geral exportado em {PNG_ALL}")

# --- 5️⃣ Gráfico por região (estado) e por rede ---
for rede in df['rede'].unique():
    plt.figure(figsize=(12, 6))
    subset_rede = df[df['rede']==rede]
    estados = subset_rede['estado_cdn'].unique()
    for estado in estados:
        subset_estado = subset_rede[subset_rede['estado_cdn']==estado]
        plt.scatter(subset_estado['longitude'], subset_estado['latitude'], 
                    label=f"{rede} - {estado}", alpha=0.7, s=subset_estado['academias_proximas_1km']*10 + 20)

    plt.title(f"{rede} - Distribuição por estado e proximidade dentro de 1 km")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    out_file = f"./exportados/proximidade_{rede}.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico por rede exportado em {out_file}")
