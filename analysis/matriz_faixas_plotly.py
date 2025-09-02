# =========================
# matriz_faixas_plotly_separado.py
# =========================
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from config import EXPORT_DIR, ESTADO_DEFAULT

# =========================
# Configurações
# =========================
FAIXAS_DISTANCIA = {
    "Muito perto (≤1 km)": (0, 1),
    "Perto (1-5 km)": (1, 5),
    "Moderado (5-10 km)": (5, 10),
    "Longe (>10 km)": (10, np.inf)
}

EXPORT_DIR = "./exportados"
os.makedirs(EXPORT_DIR, exist_ok=True)

# =========================
# Carregar dados
# =========================
df = pd.read_pickle(os.path.join(EXPORT_DIR, "unidades.pkl"))
matriz_completa = pd.read_pickle(os.path.join(EXPORT_DIR, "matriz_completa.pkl"))

# =========================
# Filtrar por estado se necessário
# =========================
estado = ESTADO_DEFAULT
if estado:
    df = df[df['estado_cdn'] == estado]
    matriz_completa = matriz_completa.loc[df['nome'], df['nome']]

# =========================
# Escolher rede base (ex: SmartFit)
# =========================
rede_base = "Smartfit"
ids_base = df[df['rede'] == rede_base]['nome']
redes = sorted(df['rede'].unique())

# =========================
# Função para contar unidades por faixa de distância
# =========================
def contar_faixas(submatriz):
    contagem = {}
    for faixa_nome, (min_km, max_km) in FAIXAS_DISTANCIA.items():
        mask = (submatriz > min_km) & (submatriz <= max_km)
        contagem[faixa_nome] = mask.sum().sum()
    return contagem

# =========================
# Criar matriz de contagens para a rede base
# =========================
matriz_faixas = pd.DataFrame(index=redes, columns=FAIXAS_DISTANCIA.keys(), dtype=float)

for rede_alvo in redes:
    ids_alvo = df[df['rede'] == rede_alvo]['nome']
    sub = matriz_completa.loc[ids_base, ids_alvo]

    if rede_base == rede_alvo:
        sub = sub.where(~np.eye(len(sub), dtype=bool))

    contagem = contar_faixas(sub)
    matriz_faixas.loc[rede_alvo] = contagem

# =========================
# Converter para porcentagem
# =========================
matriz_faixas_percent = matriz_faixas.div(matriz_faixas.sum(axis=1), axis=0) * 100

# =========================
# Função para gerar heatmap e salvar HTML
# =========================
def plot_heatmap(matriz, tipo="quantidade", titulo="Distribuição de Academias por Faixa de Distância"):
    if tipo == "percentual":
        zmin, zmax = 0, 100
        texttemplate = "%{text:.1f}%"
        hovertemplate = "Rede: %{y}<br>Faixa: %{x}<br>%: %{z:.1f}%<extra></extra>"
    else:
        zmin, zmax = None, None
        texttemplate = "%{text}"
        hovertemplate = "Rede: %{y}<br>Faixa: %{x}<br>Qtd: %{z}<extra></extra>"

    fig = go.Figure(go.Heatmap(
        z=matriz.values,
        x=matriz.columns,
        y=matriz.index,
        colorscale='Viridis',
        zmin=zmin,
        zmax=zmax,
        text=matriz.round(1),
        texttemplate=texttemplate,
        hovertemplate=hovertemplate
    ))

    fig.update_layout(
        title=dict(
            text=f"{titulo} - Rede Base: {rede_base} - Estado: {estado or 'Todos'}",
            font=dict(family="Inter", size=22, color="black"),
            x=0.5, xanchor='center'
        ),
        xaxis=dict(title="Faixas de Distância"),
        yaxis=dict(title="Redes Comparadas"),
        font=dict(family="Inter", size=14),
        autosize=True,
        margin=dict(l=50, r=50, t=100, b=50)
    )

    html_file = os.path.join(EXPORT_DIR, f"heatmap_faixas_{rede_base}_estado{estado or 'all'}_{tipo}.html")
    fig.write_html(html_file)
    print(f"🌐 Heatmap ({tipo}) salvo em {html_file}")

# =========================
# Gerar ambos os heatmaps separadamente
# =========================
plot_heatmap(matriz_faixas, tipo="quantidade")
plot_heatmap(matriz_faixas_percent, tipo="percentual")
