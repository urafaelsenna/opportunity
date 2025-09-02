# =========================
# matriz_resumida.py
# =========================
import pandas as pd
import numpy as np
import os
from config import EXPORT_DIR, DIST_MAX_DEFAULT, ESTADO_DEFAULT

EXPORT_DIR = "./exportados"
DIST_MAX_DEFAULT = 10  # km
MATRIZ_FILE = os.path.join(EXPORT_DIR, "matriz_completa.pkl")
UNIDADES_FILE = os.path.join(EXPORT_DIR, "unidades.pkl")
AGREGADA_FILE = os.path.join(EXPORT_DIR, "matriz_agregada.pkl")

# =========================
# Carregar dados
# =========================
df = pd.read_pickle(UNIDADES_FILE)
matriz_completa = pd.read_pickle(MATRIZ_FILE)

# =========================
# Filtrar por estado se necessário
# =========================
# Exemplo: estado = "SP"
estado = ESTADO_DEFAULT
if estado:
    df = df[df['estado_cdn'] == estado]
    matriz_completa = matriz_completa.loc[df['nome'], df['nome']]

# =========================
# Agregar rede x rede (corrigido)
# =========================
redes = sorted(df['rede'].unique())
matriz_agregada_min = pd.DataFrame(index=redes, columns=redes, dtype=float)
matriz_agregada_mean = pd.DataFrame(index=redes, columns=redes, dtype=float)

for rede_i in redes:
    ids_i = df[df['rede'] == rede_i]['nome']
    for rede_j in redes:
        ids_j = df[df['rede'] == rede_j]['nome']
        sub = matriz_completa.loc[ids_i, ids_j]

        # Aplicar limite de distância
        sub_limited = sub[sub <= DIST_MAX_DEFAULT]

        # Remover a diagonal se estiver comparando a mesma rede
        if rede_i == rede_j:
            sub_limited = sub_limited.where(~np.eye(len(sub_limited), dtype=bool))

        # Distância mínima e média
        if not sub_limited.empty:
            # mínimo entre unidades diferentes
            matriz_agregada_min.loc[rede_i, rede_j] = sub_limited.min().min()
            # média entre unidades diferentes
            matriz_agregada_mean.loc[rede_i, rede_j] = sub_limited.mean().mean()
        else:
            matriz_agregada_min.loc[rede_i, rede_j] = np.nan
            matriz_agregada_mean.loc[rede_i, rede_j] = np.nan


# =========================
# Salvar resultados
# =========================
matriz_agregada_min.to_pickle(os.path.join(EXPORT_DIR, "matriz_agregada_min.pkl"))
matriz_agregada_mean.to_pickle(os.path.join(EXPORT_DIR, "matriz_agregada_mean.pkl"))
print(f"✅ Matrizes agregadas salvas em {EXPORT_DIR}")