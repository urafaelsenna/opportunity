# 🏋️‍♂️ ESQUELETO DO PROJETO - OPPORTUNITY

## Análise de Investimento - Smart Fit (SMFT3)

> **⚠️ Nota Importante:** Este projeto foi desenvolvido com auxílio de Inteligência Artificial (IA) como parte do meu processo de aprendizado. Como sou iniciante em programação e análise de dados, o código pode apresentar características amadoras e está em constante evolução. Este é um projeto de estudo e desenvolvimento de habilidades para o **Desafio Opportunity de Análise de Investimentos**.

## 🎯 OBJETIVO DO PROJETO

Sistema de **análise de investimento** focado na **Smart Fit (SMFT3)** - empresa listada na B3 que atua no setor de academias low-cost no Brasil.

### **Foco Principal:**

- **Análise competitiva** da Smart Fit vs concorrentes privados
- **Mapeamento geográfico** da presença de mercado
- **Insights estratégicos** para avaliação de investimento
- **Comparativo de expansão** entre diferentes redes

## 📁 ESTRUTURA DO PROJETO

```
opportunity/
├── 📊 analysis/                    # Análises e notebooks Jupyter
├── 🗄️ database/                    # Configuração e modelos do banco de dados
├── 📤 exportados/                  # Arquivos CSV e HTML exportados
├── 🕷️ scraping/                    # Scrapers para diferentes academias
├── 🛠️ utils/                       # Utilitários e ferramentas auxiliares
├── 📄 README.md                    # Documentação principal
├── 🚀 main.py                      # Arquivo principal de execução
└── 💾 unidades.db                  # Banco de dados SQLite
```

## 🎯 OBJETIVO DO PROJETO

Sistema de coleta e análise de dados de academias para **análise de investimento**, incluindo:

- **Web scraping** de informações de academias concorrentes
- **Geocodificação** de endereços para mapeamento
- **Armazenamento** em banco de dados estruturado
- **Análise comparativa** Smart Fit vs concorrentes
- **Insights de mercado** para decisões de investimento

## 📊 ANÁLISES (analysis/)

### **Notebooks Jupyter para Análise de Investimento:**

- **`analise_falhas_geocode.ipynb`** - Análise de falhas na geocodificação
- **`df_unidades.ipynb`** - Análise do dataframe de unidades e distribuição
- **`listar_colunas.ipynb`** - Listagem e análise de colunas dos dados
- **`map_folium.py`** - Mapeamento geográfico interativo das unidades
- **`plot_unidades.py`** - Gráficos e visualizações para análise de mercado

### **Scripts Python de Análise:**

- **`criar_colunas_endereco.py`** - Criação de colunas de endereço para geocodificação
- **`excluir_bairro_pais.py`** - Limpeza de dados de bairro e país
- **`academias_proximas_raio_variavel.py`** - Análise de proximidade entre unidades
- **`analise_falhas_geocode.py`** - Script para análise de falhas na geocodificação

## 🗄️ BANCO DE DADOS (database/)

- **`db.py`** - Configuração e conexão com banco SQLite
- **`models.py`** - Modelos de dados e estruturas das tabelas
- **`__init__.py`** - Inicialização do módulo

### **Estrutura das Tabelas:**

- **`unidades`** - Dados das academias (rede, nome, endereço, cidade, estado, coordenadas)
- **`geocoding_log`** - Log de tentativas de geocodificação
- **`scraping_log`** - Log de execuções dos scrapers

## 🕷️ SCRAPERS (scraping/)

Sistema de coleta de dados de diferentes redes de academias para **análise competitiva**:

### **Redes Implementadas:**

- **`bluefit_scraper.py`** - Scraper para academias BlueFit ✅
- **`bodytech_scraper.py`** - Scraper para academias BodyTech ✅
- **`panobianco_scraper.py`** - Scraper para academias PanoBianco ✅
- **`pratique_scraper.py`** - Scraper para academias Pratique ✅
- **`selfit_scraper.py`** - Scraper para academias Selfit ✅
- **`skyfit_scraper.py`** - Scraper para academias SkyFit ✅
- **`smartfit_scraper.py`** - Scraper para academias SmartFit ✅
- **`__init__.py`** - Inicialização do módulo

### **Funcionalidades dos Scrapers:**

- Coleta automática de dados das unidades
- Sistema anti-duplicatas
- Tratamento de erros e retry
- Log de execução para auditoria

## 🛠️ UTILITÁRIOS (utils/)

### **Geocodificação (Core da Análise Geográfica):**

- **`geocode.py`** - Utilitário principal de geocodificação
- **`geocode_google_maps_api.py`** - Geocodificação via Google Maps API
- **`geocode_googlemaps_scraper.py`** - Geocodificação via scraping do Google Maps
- **`geocode_geocodio.py`** - Geocodificação via serviço Geocodio
- **`reverse_geocode_nominatim.py`** - Geocodificação reversa via Nominatim

### **Banco de Dados e Manutenção:**

- **`fix_db.py`** - Correções e manutenção do banco
- **`check_sqlite_sequence.py`** - Verificação de sequências SQLite
- **`test_dynamic_insert.py`** - Testes de inserção dinâmica
- **`check_smartfit_count.py`** - Verificação de contagem SmartFit
- **`check_csv_cdn.py`** - Verificação de dados CSV CDN
- **`recover_cdn_data.py`** - Recuperação de dados CDN

### **Processamento de Dados:**

- **`normalize_column_names.py`** - Normalização de nomes de colunas
- **`preencher_unidades.py`** - Preenchimento de dados de unidades

## 📤 EXPORTAÇÃO (exportados/)

### **Relatórios para Análise de Investimento:**

- **`unidades.csv`** - Dados das unidades exportados em CSV
- **`mapa_density_unidades.html`** - Mapa interativo da densidade de unidades
- **`metrics_estado_1.0km.csv`** - Métricas por estado (raio de 1km)
- **`metrics_estado_rede_1.0km.csv`** - Métricas por estado e rede
- **`metrics_rede_1.0km.csv`** - Métricas por rede
- **`unidades_proximas_1.0km.csv`** - Unidades próximas (raio de 1km)

## 🚀 ARQUIVOS PRINCIPAIS

- **`main.py`** - Ponto de entrada principal do sistema
- **`exportar_db_para_csv.py`** - Script para exportar banco para CSV
- **`unidades_atualizadas.json`** - Dados atualizados em formato JSON
- **`unidades.db`** - Banco de dados SQLite com todas as informações

## 🔧 DEPENDÊNCIAS PRINCIPAIS

- **Python 3.x**
- **Jupyter Notebook** (para análises e exploração de dados)
- **SQLite3** (banco de dados local)
- **Pandas** (manipulação e análise de dados)
- **Requests** (requisições HTTP para scraping)
- **BeautifulSoup** (parsing HTML)
- **Folium** (mapeamento geográfico)
- **Plotly** (visualizações interativas)
- **Google Maps API** (geocodificação premium)

## 📋 FUNCIONALIDADES PRINCIPAIS

### **1. Coleta de Dados Competitivos**

- Scraping automático de sites de academias concorrentes
- Sistema robusto com tratamento de erros
- Coleta incremental para evitar duplicatas

### **2. Geocodificação e Mapeamento**

- Conversão de endereços em coordenadas geográficas
- Múltiplas APIs para redundância e confiabilidade
- Mapeamento visual da distribuição territorial

### **3. Análise de Mercado**

- Comparativo Smart Fit vs concorrentes
- Análise de densidade de unidades por região
- Identificação de oportunidades de expansão

### **4. Relatórios para Investimento**

- Exportação em múltiplos formatos (CSV, HTML, JSON)
- Mapa interativo das unidades
- Métricas comparativas por região e rede

## 🚀 COMO USAR

### **1. Configuração Inicial**

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar Playwright para web scraping
playwright install
```

### **2. Execução do Sistema**

```bash
# Executar fluxo completo
python main.py

# Ou executar componentes individuais
python scraping/bluefit_scraper.py
python utils/geocode.py
```

### **3. Análise e Exploração**

```bash
# Abrir notebooks Jupyter
jupyter notebook analysis/

# Executar scripts de análise
python analysis/plot_unidades.py
python analysis/map_folium.py
```

### **4. Geração de Relatórios**

```bash
# Exportar dados para análise
python exportar_db_para_csv.py
```

## 🎯 INSIGHTS PARA ANÁLISE DE INVESTIMENTO

### **Smart Fit (SMFT3) - Empresa Analisada**

- **Modelo de negócio:** Low-cost fitness
- **Expansão:** Agressiva no Brasil
- **Vantagem:** Economia de escala e presença nacional

### **Análise Competitiva**

- **Concorrentes privados:** BlueFit, Selfit, BodyTech, Pratique, SkyFit, PanoBianco
- **Mapeamento de presença regional**
- **Identificação de mercados saturados vs. oportunidades**

### **Métricas de Mercado**

- **Densidade de unidades** por região
- **Análise de saturação** de mercado
- **Potencial de expansão** geográfica
- **Concentração regional** das redes

## 🔮 PRÓXIMOS PASSOS (MELHORIAS FUTURAS)

### **Funcionalidades Técnicas**

- [ ] Dashboard interativo com Streamlit
- [ ] Relatórios automatizados periódicos
- [ ] API REST para consulta de dados
- [ ] Sistema de alertas para mudanças no mercado
- [ ] Integração com dados financeiros da Smart Fit

### **Análises de Negócio**

- [ ] Análise de preços por região
- [ ] Estudo de demografia e renda
- [ ] Análise de sazonalidade
- [ ] Projeções de crescimento
- [ ] Análise de custos operacionais por região

## 📚 APRENDIZADOS E DESENVOLVIMENTO

### **O que aprendi com este projeto:**

- **Web scraping** com Python e Playwright
- **Geocodificação** e mapeamento geográfico
- **Banco de dados** SQLite e SQLAlchemy
- **Análise de dados** com Pandas e Jupyter
- **Visualizações** geográficas com Folium
- **Estruturação** de projetos Python

### **Desafios enfrentados:**

- Tratamento de erros de scraping
- Otimização de performance
- Estruturação de dados
- Integração de diferentes APIs
- Gestão de dependências

## 🤝 CONTRIBUIÇÕES E FEEDBACK

Este é um projeto de **estudo e aprendizado** para o Desafio Opportunity. Feedback construtivo é muito bem-vindo!

### **Como contribuir:**

- Reportar bugs ou problemas
- Sugerir melhorias técnicas
- Compartilhar insights de mercado
- Ajudar com otimizações de código
- Sugerir novas análises para investimento

## 📄 LICENÇA E USO

Este projeto é para **fins educacionais** e de **análise de investimentos**. Use com responsabilidade e sempre faça sua própria análise antes de tomar decisões de investimento.

---

**Desenvolvido com ❤️ e 🤖 para o Desafio Opportunity**

_"A melhor forma de aprender é fazendo, mesmo que não seja perfeito desde o início"_

_"Dados são o novo petróleo, mas análise é o novo motor"_
