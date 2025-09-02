# =========================
# matriz_plotly.py
# =========================
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from config import EXPORT_DIR, DIST_MAX_DEFAULT, ESTADO_DEFAULT

# =========================
# Definir estado para visualização
# =========================
estado = ESTADO_DEFAULT if ESTADO_DEFAULT is not None else "all"

# =========================
# Carregar matrizes agregadas
# =========================
matriz_min = pd.read_pickle(os.path.join(EXPORT_DIR, "matriz_agregada_min.pkl"))
matriz_mean = pd.read_pickle(os.path.join(EXPORT_DIR, "matriz_agregada_mean.pkl"))

# Validar dados
if matriz_min.empty or matriz_mean.empty:
    raise ValueError("Matrizes agregadas estão vazias ou corrompidas.")

# =========================
# Função para gerar heatmap e salvar HTML
# =========================
def plot_heatmap(matriz, tipo_matriz, dist_max=DIST_MAX_DEFAULT):
    # Aplicar limite de distância e preencher NaN
    matriz_plot = matriz.fillna(dist_max)
    matriz_plot[matriz_plot > dist_max] = dist_max

    # Nome do arquivo
    html_file = os.path.join(
        EXPORT_DIR,
        f"matriz_agregada_{tipo_matriz.lower()}_dist{dist_max}km_estado{estado.replace(' ', '_')}.html"
    )

    # Criar heatmap
    fig = go.Figure(go.Heatmap(
        z=matriz_plot.values,
        x=matriz_plot.columns,
        y=matriz_plot.index,
        colorscale='Magma',
        zmin=0,
        zmax=dist_max,
        text=matriz_plot.round(2),
        texttemplate="%{text}",
        hovertemplate="Rede X: %{x}<br>Rede Y: %{y}<br>Distância: %{z} km<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"Matriz agregada de distâncias por rede (≤ {dist_max} km)<br>Tipo: {tipo_matriz} - Estado: {estado}",
            font=dict(
                family="Inter",  # aqui você escolhe a fonte
                size=24,                           # tamanho do título
                color="black"                      # cor do título
            ),
            x=0.5,  # centraliza horizontalmente
            xanchor='center'
        ),
        #title=f"Matriz agregada de distâncias por rede (≤ {dist_max} km de raio)<br>Tipo: {tipo_matriz} distância - Estado: {estado}",
        xaxis=dict(title="Rede", tickfont=dict(family="Inter", size=12, color="black")),
        yaxis=dict(title="Rede", tickfont=dict(family="Inter", size=12, color="black")),
        font=dict(family="Inter", size=14, color="black"),
        autosize=True,
        margin=dict(l=50, r=50, t=100, b=50)
    )

    # Salvar HTML
    fig.write_html(html_file)
    print(f"🌐 Heatmap {tipo_matriz} salvo em {html_file}")

# =========================
# Gerar heatmaps mínima e média
# =========================
plot_heatmap(matriz_min, "Minima")
plot_heatmap(matriz_mean, "Media")
