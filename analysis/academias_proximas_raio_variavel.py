# analysis/academias_proximas_raio_variavel.py

import pandas as pd
from geopy.distance import geodesic
import sqlite3
from tqdm import tqdm
import os

# Caminho do banco de dados SQLite
DB_PATH = "./unidades.db"
EXPORT_DIR = "./exportados"

if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)

# Carregar dados relevantes
df = pd.read_sql_query("""
    SELECT id, rede, nome, endereco, latitude, longitude, estado_cdn
    FROM unidades
""", conn)

conn.close()

# Converter latitude e longitude para float
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

# Função para calcular distância entre duas coordenadas
def distancia_km(coord1, coord2):
    return geodesic(coord1, coord2).km

# Receber raio do usuário
while True:
    try:
        raio_km = float(input("Digite o raio em km para verificar proximidade: "))
        break
    except ValueError:
        print("Valor inválido. Digite um número.")

print(f"🔍 Calculando pares de unidades dentro de {raio_km} km...")

# Lista de pares próximos
proximos = []

# Iterar sobre todas as combinações de unidades
for i, row_i in tqdm(df.iterrows(), total=len(df), desc="Unidades processadas"):
    coord_i = (row_i['latitude'], row_i['longitude'])
    for j, row_j in df.loc[i+1:].iterrows():
        coord_j = (row_j['latitude'], row_j['longitude'])
        d = distancia_km(coord_i, coord_j)
        if d <= raio_km:
            proximos.append({
                'id_1': row_i['id'],
                'rede_1': row_i['rede'],
                'nome_1': row_i['nome'],
                'id_2': row_j['id'],
                'rede_2': row_j['rede'],
                'nome_2': row_j['nome'],
                'distancia_km': round(d, 3),
                'estado': row_i['estado_cdn']
            })

# Transformar em DataFrame
df_proximos = pd.DataFrame(proximos)

# Exportar CSV com pares próximos
csv_pares = os.path.join(EXPORT_DIR, f"unidades_proximas_{raio_km}km.csv")
df_proximos.to_csv(csv_pares, index=False)
print(f"✅ Total de pares próximos encontrados: {len(df_proximos)}")
print(f"📤 CSV exportado em {csv_pares}")

# Métricas por rede
metrics_rede = []
for rede in df['rede'].unique():
    total_pares = df_proximos[(df_proximos['rede_1'] == rede) | (df_proximos['rede_2'] == rede)].shape[0]
    metrics_rede.append({'rede': rede, 'pares_proximos': total_pares})

df_metrics_rede = pd.DataFrame(metrics_rede)
csv_rede = os.path.join(EXPORT_DIR, f"metrics_rede_{raio_km}km.csv")
df_metrics_rede.to_csv(csv_rede, index=False)
print(f"📊 Métricas por rede exportadas em {csv_rede}")

# Métricas por estado
metrics_estado = []
for estado in df['estado_cdn'].unique():
    total_pares = df_proximos[df_proximos['estado'] == estado].shape[0]
    metrics_estado.append({'estado': estado, 'pares_proximos': total_pares})

df_metrics_estado = pd.DataFrame(metrics_estado)
csv_estado = os.path.join(EXPORT_DIR, f"metrics_estado_{raio_km}km.csv")
df_metrics_estado.to_csv(csv_estado, index=False)
print(f"📊 Métricas por estado exportadas em {csv_estado}")

# Métricas por estado + rede
metrics_estado_rede = []
for estado in df['estado_cdn'].unique():
    df_estado = df_proximos[df_proximos['estado'] == estado]
    for rede in df['rede'].unique():
        total_pares = df_estado[
            (df_estado['rede_1'] == rede) | (df_estado['rede_2'] == rede)
        ].shape[0]
        metrics_estado_rede.append({
            'estado': estado,
            'rede': rede,
            'pares_proximos': total_pares
        })

df_metrics_estado_rede = pd.DataFrame(metrics_estado_rede)
csv_estado_rede = os.path.join(EXPORT_DIR, f"metrics_estado_rede_{raio_km}km.csv")
df_metrics_estado_rede.to_csv(csv_estado_rede, index=False)
print(f"📊 Métricas por estado + rede exportadas em {csv_estado_rede}")

print("🎉 Processamento concluído!")
