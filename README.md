# Análise da SmartFit e Concorrentes

Este projeto tem como objetivo analisar a rede de academias **SmartFit**, listada em bolsa de valores (capital aberto), complementando com dados obtidos das suas **principais concorrentes privadas** (Bluefit, Selfit, JustFit, entre outras).

O foco é avaliar:

- Distribuição geográfica de unidades no Brasil
- Comparativo da presença de mercado entre SmartFit e concorrentes
- Insights estratégicos de expansão

## 🔄 Fluxo de trabalho

### 1. **SmartFit (dados oficiais)**

- Dados financeiros obtidos em relatórios oficiais (CVM, B3)
- Número de unidades e indicadores financeiros

### 2. **Concorrentes (scraping)**

- Web scraping dos sites oficiais: Bluefit, Selfit, JustFit, etc.
- Coleta de informações:
  - rede, nome, endereço, cidade e estado
- Scrapers separados por rede para facilitar manutenção e expansão
- Evita duplicatas usando banco SQLite incremental

### 3. **Geocodificação (Nominatim)**

- Módulo `utils/atualizar_coords.py` consulta o banco SQLite
- Para registros sem latitude/longitude, chama Nominatim para obter coordenadas
- Permite reprocessar endereços não encontrados na primeira tentativa
- Endereços que não forem resolvidos podem ser complementados manualmente

### 4. **Banco de dados**

- Armazenamento em SQLite via SQLAlchemy
- Tabela `unidades` com colunas:
  - `rede`, `nome`, `endereco`, `cidade`, `estado`, `latitude`, `longitude`, `telefone` (opcional)
- Atualizações incrementais evitam duplicação de registros

### 5. **Análise**

- Distribuição de academias por estado e cidade
- Comparativo SmartFit vs concorrentes
- Possibilidade de visualização em mapas e estimativa de densidade de unidades
- Scripts de análise prontos em `analysis/analise.py`

## 🏗️ Estrutura do projeto

```
opportunity/
├── analysis/
│   └── analise.py                # Relatórios e análises
├── database/
│   ├── __init__.py               # Pacote Python
│   ├── db.py                     # Gerenciamento do banco
│   └── models.py                 # Modelos de dados (SQLAlchemy)
├── scraping/
│   ├── __init__.py               # Pacote Python
│   ├── bluefit_scraper.py        # Scraper Bluefit
│   ├── bodytech_scraper.py       # Scraper Bodytech (futuro)
│   └── selfit_scraper.py         # Scraper Selfit (futuro)
├── utils/
│   ├── atualizar_coords.py       # Atualização de coordenadas
│   └── geocode.py                # Funções de geocodificação
├── main.py                        # Orquestrador do fluxo completo
├── README.md                      # Documentação
├── unidades.db                     # Banco de dados SQLite
└── unidades_atualizadas.json       # Exportação JSON
```

## 📦 Instalação

Requisitos:

- Python 3.9+
- pip

Instale os pacotes necessários:

```bash
pip install playwright sqlalchemy pandas requests
playwright install
```

## ⚙️ Como rodar

1. **Scraper de concorrentes**

```bash
python scraping/bluefit_scraper.py
```

2. **Atualizar coordenadas**

```bash
python utils/atualizar_coords.py
```

3. **Gerar análises**

```bash
python analysis/analise.py
```

4. **Executar fluxo completo**

```bash
python main.py
```

## ✅ Funcionalidades

- Scraper Bluefit totalmente funcional
- Banco de dados incremental com SQLite + SQLAlchemy
- Export JSON atualizado automaticamente
- Estrutura modular pronta para novas redes
- Geocodificação integrada
- Scripts de análise e relatórios

## 🔮 Próximos passos

- Adicionar scrapers de outras redes: SmartFit, Selfit, Bodytech
- Criar dashboards interativos com Plotly ou Streamlit
- Automatizar relatórios periódicos de mercado
