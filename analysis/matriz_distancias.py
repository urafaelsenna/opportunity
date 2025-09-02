# =========================
# matriz_distancias.py
# =========================
import sqlite3
import pandas as pd
import numpy as np
import os
from scipy.spatial.distance import cdist

# =========================
# Configurações
# =========================
DB_PATH = "./unidades.db"
EXPORT_DIR = "./exportados"
UNIDADES_PKL = os.path.join(EXPORT_DIR, "unidades.pkl")
MATRIZ_FILE = os.path.join(EXPORT_DIR, "matriz_completa.pkl")

os.makedirs(EXPORT_DIR, exist_ok=True)

# =========================
# Função para carregar dados
# =========================
def load_unidades():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT id, rede, nome, latitude, longitude, estado_cdn
        FROM unidades
    """, conn)
    conn.close()
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    return df

# =========================
# Haversine vetorizado
# =========================
def haversine_vectorized(lat_lon):
    lat = np.radians(lat_lon[:, 0])[:, None]
    lon = np.radians(lat_lon[:, 1])[:, None]
    lat2 = lat.T
    lon2 = lon.T
    dlat = lat - lat2
    dlon = lon - lon2
    a = np.sin(dlat/2)**2 + np.cos(lat)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    R = 6371  # Raio da Terra em km
    return R * c

# =========================
# Execução
# =========================
if __name__ == "__main__":
    print("🔗 Carregando dados do banco...")
    df = load_unidades()
    df = df.dropna(subset=['latitude', 'longitude']).reset_index(drop=True)
    df.to_pickle(UNIDADES_PKL)
    print(f"✅ Dados salvos: {len(df)} unidades")

    if os.path.exists(MATRIZ_FILE):
        print("⚡ Matriz já existe. Carregando pickle...")
        matriz = pd.read_pickle(MATRIZ_FILE)
    else:
        print("🔍 Calculando matriz de distâncias (vetorizado)...")
        coords = df[['latitude', 'longitude']].to_numpy()
        matriz_array = haversine_vectorized(coords)
        matriz = pd.DataFrame(matriz_array, index=df['nome'], columns=df['nome'])
        matriz.to_pickle(MATRIZ_FILE)
        print(f"✅ Matriz calculada e salva em {MATRIZ_FILE}")
