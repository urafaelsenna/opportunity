# ESQUELETO DO PROJETO - OPPORTUNITY

## 📁 ESTRUTURA DO PROJETO

```
opportunity/
├── 📊 analysis/                    # Análises e notebooks Jupyter
├── 🗄️ database/                    # Configuração e modelos do banco de dados
├── 📤 exportados/                  # Arquivos CSV exportados
├── 🕷️ scraping/                    # Scrapers para diferentes academias
├── 🛠️ utils/                       # Utilitários e ferramentas auxiliares
├── 📄 README.md                    # Documentação principal
├── 🚀 main.py                      # Arquivo principal de execução
└── 💾 unidades.db                  # Banco de dados SQLite
```

## 🎯 OBJETIVO DO PROJETO

Sistema de coleta e análise de dados de academias, incluindo:

- Web scraping de informações de academias
- Geocodificação de endereços
- Armazenamento em banco de dados
- Análise e exportação de dados

## 📊 ANÁLISES (analysis/)

### Notebooks Jupyter:

- **`analise_falhas_geocode.ipynb`** - Análise de falhas na geocodificação
- **`df_unidades.ipynb`** - Análise do dataframe de unidades
- **`listar_colunas.ipynb`** - Listagem e análise de colunas dos dados

### Scripts Python:

- **`criar_colunas_endereco.py`** - Criação de colunas de endereço
- **`excluir_bairro_pais.py`** - Limpeza de dados de bairro e país

## 🗄️ BANCO DE DADOS (database/)

- **`db.py`** - Configuração e conexão com banco SQLite
- **`models.py`** - Modelos de dados e estruturas das tabelas
- **`__init__.py`** - Inicialização do módulo

## 🕷️ SCRAPERS (scraping/)

Sistema de coleta de dados de diferentes redes de academias:

- **`bluefit_scraper.py`** - Scraper para academias BlueFit
- **`bodytech_scraper.py`** - Scraper para academias BodyTech
- **`panobianco_scraper.py`** - Scraper para academias PanoBianco
- **`pratique_scraper.py`** - Scraper para academias Pratique
- **`selfit_scraper.py`** - Scraper para academias Selfit
- **`skyfit_scraper.py`** - Scraper para academias SkyFit
- **`smartfit_scraper.py`** - Scraper para academias SmartFit
- **`__init__.py`** - Inicialização do módulo

## 🛠️ UTILITÁRIOS (utils/)

### Geocodificação:

- **`geocode.py`** - Utilitário principal de geocodificação
- **`geocode_google_maps_api.py`** - Geocodificação via Google Maps API
- **`geocode_googlemaps_scraper.py`** - Geocodificação via scraping do Google Maps
- **`geocode_geocodio.py`** - Geocodificação via serviço Geocodio
- **`reverse_geocode_nominatim.py`** - Geocodificação reversa via Nominatim

### Banco de Dados:

- **`fix_db.py`** - Correções e manutenção do banco
- **`check_sqlite_sequence.py`** - Verificação de sequências SQLite
- **`test_dynamic_insert.py`** - Testes de inserção dinâmica
- **`check_smartfit_count.py`** - Verificação de contagem SmartFit
- **`check_csv_cdn.py`** - Verificação de dados CSV CDN
- **`recover_cdn_data.py`** - Recuperação de dados CDN

### Processamento de Dados:

- **`normalize_column_names.py`** - Normalização de nomes de colunas
- **`preencher_unidades.py`** - Preenchimento de dados de unidades

## 📤 EXPORTAÇÃO (exportados/)

- **`unidades.csv`** - Dados das unidades exportados em CSV

## 🚀 ARQUIVOS PRINCIPAIS

- **`main.py`** - Ponto de entrada principal do sistema
- **`exportar_db_para_csv.py`** - Script para exportar banco para CSV
- **`unidades_atualizadas.json`** - Dados atualizados em formato JSON
- **`unidades.db`** - Banco de dados SQLite com todas as informações

## 🔧 DEPENDÊNCIAS PRINCIPAIS

- **Python 3.x**
- **Jupyter Notebook** (para análises)
- **SQLite3** (banco de dados)
- **Pandas** (manipulação de dados)
- **Requests** (requisições HTTP)
- **BeautifulSoup** (parsing HTML)
- **Google Maps API** (geocodificação)

## 📋 FUNCIONALIDADES PRINCIPAIS

1. **Coleta de Dados**: Scraping automático de sites de academias
2. **Geocodificação**: Conversão de endereços em coordenadas geográficas
3. **Armazenamento**: Banco de dados SQLite para persistência
4. **Análise**: Notebooks Jupyter para exploração de dados
5. **Exportação**: Geração de relatórios em CSV e JSON
6. **Manutenção**: Ferramentas para correção e limpeza de dados

## 🚀 COMO USAR

1. **Configuração**: Instalar dependências Python
2. **Execução**: Rodar `main.py` para iniciar o sistema
3. **Análise**: Abrir notebooks Jupyter na pasta `analysis/`
4. **Exportação**: Usar `exportar_db_para_csv.py` para gerar relatórios

## 📝 NOTAS PARA A EQUIPE

- Todos os scrapers seguem padrão similar para facilitar manutenção
- Sistema de geocodificação com múltiplas APIs para redundância
- Banco de dados centralizado com backup automático
- Notebooks de análise para exploração e validação de dados
- Utilitários modulares para facilitar extensões futuras

---

_Projeto criado para coleta e análise de dados de academias_
_Última atualização: [DATA_ATUAL]_
