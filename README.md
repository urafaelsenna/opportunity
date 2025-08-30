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
│   └── plot_unidades.py           # Gráficos e visualizações
├── 🗄️ database/                    # Banco de dados SQLite
│   ├── db.py                      # Configuração do banco
│   └── models.py                  # Modelos de dados
├── 📤 exportados/                  # Relatórios e dados exportados
│   ├── mapa_density_unidades.html # Mapa interativo
│   ├── metrics_estado_1.0km.csv   # Métricas por estado
│   └── unidades_proximas_1.0km.csv
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
├── 🚀 main.py                      # Execução principal
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
# Executar todos os scrapers
python main.py

# Ou executar individualmente
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
python analysis/plot_unidades.py
python analysis/map_folium.py
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

## 🔮 Próximos Passos (Melhorias Futuras)

### **Funcionalidades Técnicas**

- [ ] Dashboard interativo com Streamlit
- [ ] Relatórios automatizados periódicos
- [ ] API REST para consulta de dados
- [ ] Sistema de alertas para mudanças no mercado

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
