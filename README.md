# 🏋️‍♂️ Análise de Investimento - Smart Fit (SMFT3)

## Desafio Opportunity - Análise de Dados e Investimentos

> **⚠️ Nota Importante:** Este projeto foi desenvolvido com auxílio de Inteligência Artificial (IA) como parte do meu processo de aprendizado. Como sou iniciante em programação e análise de dados, o código pode apresentar características amadoras e está em constante evolução. Este é um projeto de estudo e desenvolvimento de habilidades.

## 🎯 Objetivo do Projeto

Este projeto foi criado especificamente para o **Desafio Opportunity de Análise de Investimentos**, focando na análise da **Smart Fit (SMFT3)** - empresa listada na B3 que atua no setor de academias low-cost no Brasil.

### 📊 Foco da Análise

- **Distribuição geográfica** das unidades Smart Fit vs concorrentes
- **Análise de mercado** e posicionamento competitivo
- **Insights estratégicos** para avaliação de investimento
- **Comparativo** com principais concorrentes privados (BlueFit, Selfit, BodyTech, etc.)
- **Análise de distâncias** entre unidades para identificar proximidade e cobertura geográfica

## 🆕 Nova Funcionalidade: Análise de Distâncias entre Academias

Este projeto agora calcula e visualiza **as distâncias entre unidades de academias no Brasil**, agregando por rede e por estado, permitindo identificar proximidade, cobertura geográfica e unidades isoladas.

### 📍 Estrutura dos Dados

- **Banco de dados (`unidades.db`)**: informações de cada academia

  - `id` → identificador único da unidade
  - `rede` → nome da rede da academia
  - `nome` → nome da unidade
  - `latitude` e `longitude` → coordenadas geográficas
  - `estado_cdn` → código do estado

- **Arquivos gerados**:
  - `unidades.pkl` → DataFrame com todas as unidades carregadas do banco
  - `matriz_completa.pkl` → matriz completa de distâncias entre todas as unidades
  - `matriz_agregada_min.pkl` → matriz agregada por rede com distância mínima entre **unidades diferentes**
  - `matriz_agregada_mean.pkl` → matriz agregada por rede com distância média entre unidades diferentes
  - Heatmaps HTML → visualização interativa das matrizes agregadas

### 🧮 Como Funciona a Matriz de Distâncias

O cálculo das distâncias entre academias é feito em **três níveis**, cada um gerando arquivos próprios para análise:

1. **Matriz completa (`matriz_completa.pkl`)**

   - Cada unidade é comparada com todas as outras usando a **fórmula de Haversine**, que calcula a distância geodésica (em km) entre dois pontos de latitude/longitude.
   - Resultado: matriz **simétrica**, onde cada linha e coluna representam uma unidade individual.
   - A diagonal originalmente era **0 km** (distância da unidade com ela mesma), mas isso não entra nas análises agregadas.

2. **Matrizes agregadas por rede (`matriz_agregada_min.pkl` e `matriz_agregada_mean.pkl`)**

   - A matriz completa é resumida para comparar **redes de academias entre si**.
   - O cálculo considera apenas unidades diferentes, e dentro de um **raio máximo configurável** (`DIST_MAX_DEFAULT`, ex.: 10 km):

     - **Matriz mínima (`Min`)** → menor distância encontrada entre qualquer par de unidades de duas redes.
     - **Matriz média (`Mean`)** → média de todas as distâncias válidas (≤ raio) entre unidades de duas redes.

   - Se nenhuma unidade ficar dentro do raio definido, o resultado será `NaN`.

3. **Visualizações (`*.html`)**

   - Heatmaps interativos em HTML são gerados com **cores representando distâncias**:

     - Cores claras → academias muito próximas.
     - Cores escuras → academias distantes ou inexistentes no raio.

   - O usuário pode filtrar por estado (`ESTADO_DEFAULT = "SP"`, por exemplo), para análises regionais.

### 📊 Interpretação dos Resultados

- **Distâncias mínimas (`Min`)** → revelam proximidade máxima entre redes (ex.: Smart Fit e Bluefit com academias a 0.8 km no RJ).
- **Distâncias médias (`Mean`)** → mostram a tendência geral de proximidade ou dispersão entre as redes em determinada região.
- **Valores pequenos (>0 km)** → indicam redes com academias vizinhas ou sobreposição de mercado.
- **Valores altos (próximos ao raio limite)** → indicam redes que coexistem na mesma região, mas não tão próximas.
- **NaN** → nenhuma unidade dentro do raio definido (não há sobreposição geográfica entre as redes analisadas).

### 🆕 Nova Lógica: Faixas de Distância Dinâmicas

O projeto agora suporta **análise de distâncias entre unidades de academias** usando faixas de distância **dinâmicas**, definidas a partir de um **limite máximo configurável pelo usuário** (`DIST_MAX_ULTIMA_FAIXA`).

- **Faixas neutras:** não são usadas classificações subjetivas como "perto" ou "longe".
- **Divisão automática:** os intervalos são gerados a partir de pontos fixos (1, 5, 10, 15, 20, 30, 40, 50 km) até o valor máximo definido pelo usuário.
- **Exemplo:** se `DIST_MAX_ULTIMA_FAIXA = 15`, as faixas serão:

  ```
  ≤ 1 km
  > 1 – ≤ 5 km
  > 5 – ≤ 10 km
  > 10 – ≤ 15 km
  ```

- **Primeira faixa:** inclui todas as distâncias menores ou iguais ao limite inferior (0–1 km).
- **Demais faixas:** incluem apenas valores **maiores que o limite inferior e menores ou iguais ao limite superior**.

✅ **Vantagens desta abordagem:**

- Evita duplicação de contagem de unidades entre faixas.
- Permite ajustar facilmente a granularidade da análise, dependendo do tamanho do mercado ou da cidade analisada.
- Facilita comparações regionais e por estado sem depender de termos subjetivos.
- O valor de `DIST_MAX_ULTIMA_FAIXA` é incluído no nome do arquivo gerado, permitindo organizar múltiplas execuções:

**Exemplo de nome de arquivo:**

```
heatmap_faixas_Smartfit_estadoRJ_quantidade_max15km.html
heatmap_faixas_Smartfit_estadoRJ_percentual_max15km.html
```

### ⚙️ Configurações (`config.py`)

```python
EXPORT_DIR = "./exportados"      # pasta de arquivos gerados
DIST_MAX_DEFAULT = 10            # raio máximo em km para cálculo de agregados
ESTADO_DEFAULT = None            # None = todos os estados; ou string ex: "SP"
```

- Alterar `ESTADO_DEFAULT` permite filtrar resultados por estado específico.

### 🚀 Passo a Passo da Análise de Distâncias

1. Executar `matriz_distancias.py` → gera a matriz completa de distâncias.
2. Executar `matriz_resumida.py` → agrega as distâncias por rede, considerando apenas unidades diferentes.
3. Executar `matriz_plotly.py` → gera heatmaps interativos em HTML.
4. Visualizar os heatmaps e interpretar proximidade, cobertura e unidades isoladas.

## 🤖 Desenvolvimento com Inteligência Artificial

### Como foi criado:

- **Scrapers automatizados** para coleta de dados das redes concorrentes
- **Sistema de geocodificação** para mapeamento geográfico
- **Banco de dados estruturado** para análise comparativa
- **Scripts de análise** para insights de mercado

### Por que pode parecer "amador":

- Sou **iniciante em programação** e análise de dados
- O projeto foi desenvolvido **com auxílio de IA** para acelerar o aprendizado
- Estou em processo de **desenvolvimento de habilidades técnicas**
- O foco foi na **funcionalidade** e **insights de negócio** mais que na elegância do código

## 🔄 Fluxo de Trabalho

### 1. **Smart Fit (Dados Oficiais)**

- Dados financeiros de relatórios CVM/B3
- Número de unidades e indicadores financeiros
- Análise de performance de mercado

### 2. **Concorrentes (Web Scraping)**

- Coleta automatizada de dados das principais redes:
  - **BlueFit** ✅ Funcionando
  - **Selfit** ✅ Funcionando
  - **BodyTech** ✅ Funcionando
  - **Pratique** ✅ Funcionando
  - **SkyFit** ✅ Funcionando
  - **PanoBianco** ✅ Funcionando

### 3. **Geocodificação e Mapeamento**

- Conversão de endereços em coordenadas geográficas
- Mapeamento da distribuição territorial
- Análise de densidade de unidades por região

### 4. **Análise de Mercado**

- Comparativo Smart Fit vs concorrentes
- Análise de presença regional
- Insights para estratégia de expansão

## 🏗️ Estrutura do Projeto

```
opportunity/
├── 📊 analysis/                    # Análises e notebooks Jupyter
│   ├── analise_falhas_geocode.ipynb
│   ├── df_unidades.ipynb
│   ├── listar_colunas.ipynb
│   ├── map_folium.py              # Mapeamento geográfico
│   ├── matriz_distancias.py       # 🆕 Matriz completa de distâncias
│   ├── matriz_resumida.py         # 🆕 Agregação por rede
│   ├── matriz_plotly.py           # 🆕 Visualização com heatmaps
│   └── plot_unidades_density.py   # 🆕 Análise de densidade
├── 🗄️ database/                    # Banco de dados SQLite
│   ├── db.py                      # Configuração do banco
│   └── models.py                  # Modelos de dados
├── 📤 exportados/                  # Relatórios e dados exportados
│   ├── mapa_density_unidades.html # Mapa interativo
│   ├── metrics_estado_1.0km.csv   # Métricas por estado
│   ├── unidades_proximas_1.0km.csv
│   ├── matriz_completa.pkl        # 🆕 Matriz completa de distâncias
│   ├── matriz_agregada_min.pkl    # 🆕 Matriz mínima por rede
│   ├── matriz_agregada_mean.pkl   # 🆕 Matriz média por rede
│   └── *.html                     # 🆕 Heatmaps interativos
├── 🕷️ scraping/                    # Scrapers para diferentes academias
│   ├── bluefit_scraper.py         # ✅ Funcionando
│   ├── bodytech_scraper.py        # ✅ Funcionando
│   ├── selfit_scraper.py          # ✅ Funcionando
│   ├── pratique_scraper.py        # ✅ Funcionando
│   ├── skyfit_scraper.py          # ✅ Funcionando
│   ├── panobianco_scraper.py      # ✅ Funcionando
│   └── smartfit_scraper.py        # ✅ Funcionando
├── 🛠️ utils/                       # Ferramentas auxiliares
│   ├── geocode.py                 # Geocodificação principal
│   ├── geocode_google_maps_api.py # API Google Maps
│   ├── geocode_geocodio.py        # Serviço Geocodio
│   └── reverse_geocode_nominatim.py # Nominatim
├── 📄 README.md                    # Esta documentação
├── ⚙️ config.py                    # 🆕 Configurações do projeto
└── 💾 unidades.db                  # Banco de dados
```

## 📦 Instalação e Configuração

### Requisitos:

- Python 3.9+
- pip

### Instalação:

```bash
# Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd opportunity

# Instale as dependências
pip install -r requirements.txt

# Instale o Playwright (para web scraping)
playwright install
```

## ⚙️ Como Executar

### 1. **Coleta de Dados das Concorrentes**

```bash
# Executar scrapers individualmente
python scraping/bluefit_scraper.py
python scraping/selfit_scraper.py
# ... outros scrapers
```

### 2. **Atualizar Coordenadas Geográficas**

```bash
python utils/geocode.py
```

### 3. **Gerar Análises e Relatórios**

```bash
# Abrir notebooks Jupyter
jupyter notebook analysis/

# Ou executar scripts Python
python analysis/plot_unidades_density.py
python analysis/map_folium.py

# 🆕 NOVO: Análise de distâncias entre academias
python analysis/matriz_distancias.py      # Gera matriz completa
python analysis/matriz_resumida.py        # Agrega por rede
python analysis/matriz_plotly.py          # Gera heatmaps
```

### 4. **Exportar Dados**

```bash
python exportar_db_para_csv.py
```

## 📊 Funcionalidades Implementadas

### ✅ **Scrapers Funcionais**

- **7 redes de academias** com coleta automatizada
- Sistema anti-duplicatas com banco SQLite
- Tratamento de erros e retry automático

### ✅ **Geocodificação**

- Múltiplas APIs para redundância
- Conversão automática de endereços
- Mapeamento geográfico completo

### ✅ **Análise de Dados**

- Notebooks Jupyter para exploração
- Visualizações com Folium e Plotly
- Métricas comparativas por região
- 🆕 **Matriz de distâncias** entre unidades
- 🆕 **Heatmaps interativos** para análise geográfica
- 🆕 **Agregação por rede** com métricas de proximidade

### ✅ **Exportação**

- Relatórios em CSV e HTML
- Mapa interativo das unidades
- Dados estruturados para análise

## 🎯 Insights para Análise de Investimento

### **Smart Fit (SMFT3)**

- Empresa listada na B3
- Modelo de negócio low-cost
- Expansão agressiva no Brasil

### **Análise Competitiva**

- Comparativo com concorrentes privados
- Mapeamento de presença regional
- Identificação de oportunidades de mercado

### **Métricas de Mercado**

- Densidade de unidades por região
- Análise de saturação de mercado
- Potencial de expansão geográfica
- 🆕 **Distâncias entre unidades** para análise de cobertura
- 🆕 **Identificação de unidades isoladas** ou muito próximas
- 🆕 **Análise competitiva** por proximidade geográfica

## 🔮 Próximos Passos (Melhorias Futuras)

### **Funcionalidades Técnicas**

- [ ] Dashboard interativo com Streamlit
- [ ] Relatórios automatizados periódicos
- [ ] API REST para consulta de dados
- [ ] Sistema de alertas para mudanças no mercado
- 🆕 ✅ **Análise de distâncias** entre academias
- 🆕 ✅ **Heatmaps interativos** para visualização
- 🆕 ✅ **Matrizes agregadas** por rede e estado

### **Análises de Negócio**

- [ ] Análise de preços por região
- [ ] Estudo de demografia e renda
- [ ] Análise de sazonalidade
- [ ] Projeções de crescimento

## 📚 Aprendizados e Desenvolvimento

### **O que aprendi:**

- Web scraping com Python
- Geocodificação e mapeamento
- Banco de dados SQLite
- Análise de dados com Pandas
- Visualizações geográficas
- 🆕 **Cálculo de distâncias geodésicas** com fórmula de Haversine
- 🆕 **Agregação e análise** de dados geográficos
- 🆕 **Criação de heatmaps** interativos com Plotly

### **Desafios enfrentados:**

- Tratamento de erros de scraping
- Otimização de performance
- Estruturação de dados
- Integração de diferentes APIs

## 🤝 Contribuições e Feedback

Este é um projeto de **estudo e aprendizado**. Feedback construtivo é muito bem-vindo!

### **Como contribuir:**

- Reportar bugs ou problemas
- Sugerir melhorias
- Compartilhar insights de mercado
- Ajudar com otimizações de código

## 📄 Licença

Este projeto é para fins educacionais e de análise de investimentos. Use com responsabilidade.

---

**Desenvolvido com ❤️ e 🤖 para o Desafio Opportunity**

_"A melhor forma de aprender é fazendo, mesmo que não seja perfeito desde o início"_
