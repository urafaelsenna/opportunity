from playwright.sync_api import sync_playwright
import time
import sys
import os
import re

# Adiciona o diretório pai ao path para importar os módulos do banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
    from database.models import Unidade
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)

def extrair_cidade_estado(endereco):
    """
    Extrai cidade e estado do endereço da Pratique
    Formato típico: "Av. Saramenha, 1530 - Guarani, Belo Horizonte - MG"
    """
    cidade = estado = ""
    try:
        if not endereco:
            return cidade, estado
            
        # Procura por padrão "Cidade - UF" no final
        if " - " in endereco:
            partes = endereco.split(" - ")
            if len(partes) >= 2:
                ultima_parte = partes[-1].strip()
                if len(ultima_parte) == 2:  # Provavelmente é UF
                    estado = ultima_parte
                    if len(partes) >= 3:
                        cidade = partes[-2].strip()
                else:
                    # Tenta extrair cidade e estado de outras formas
                    if "," in endereco:
                        partes_por_virgula = endereco.split(",")
                        if len(partes_por_virgula) >= 2:
                            ultima_parte_virgula = partes_por_virgula[-1].strip()
                            if " - " in ultima_parte_virgula:
                                cidade, estado = ultima_parte_virgula.split(" - ")
                                cidade = cidade.strip()
                                estado = estado.strip()
        
        # Debug para ver o que está sendo processado
        print(f"    🔍 Endereço: '{endereco}' -> Cidade: '{cidade}', Estado: '{estado}'")
        
    except Exception as e:
        print(f"⚠️ Erro ao extrair cidade/estado de '{endereco}': {e}")
    
    return cidade, estado

def coletar_unidades_pratique_incremental():
    """
    Coleta unidades da Pratique Fitness de forma incremental, usando scroll
    e evitando duplicatas no banco de dados
    """
    url = "https://pratiquefitness.com.br/unidades"
    unidades_novas = []
    unidades_processadas = set()  # Para evitar duplicatas nesta execução
    
    # Inicializa banco e carrega unidades existentes
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    unidades_existentes = db.buscar_nomes_existentes()
    print(f"📊 Unidades já existentes no banco: {len(unidades_existentes)}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Configura timeouts explícitos para não parar
        page.set_default_timeout(300000)  # 5 minutos
        page.set_default_navigation_timeout(300000)
        
        print("🌐 Navegando para a página da Pratique Fitness...")
        page.goto(url)

        # Espera os cards carregarem
        print("⏳ Aguardando carregamento dos cards...")
        page.wait_for_selector("div.ant-card-body", timeout=300000)
        
        # Variáveis para controle do scroll
        altura_anterior = 0
        scrolls_sem_novos_cards = 0
        max_scrolls_sem_novos = 5  # Para de tentar após 5 scrolls sem novos cards
        
        print("🔄 Iniciando coleta com scroll incremental...")
        
        while scrolls_sem_novos_cards < max_scrolls_sem_novos:
            # Processa os cards visíveis ATUALMENTE
            cards = page.query_selector_all("div.ant-card-body")
            novos_cards = 0
            
            for card in cards:
                try:
                    # Extrai nome da unidade
                    nome_element = card.query_selector("h4.ant-typography.css-xx138k")
                    if not nome_element:
                        continue
                    
                    nome = nome_element.inner_text().strip()
                    
                    # Evita processar o mesmo card duas vezes nesta execução
                    if nome in unidades_processadas:
                        continue
                    
                    print(f"🔍 Processando unidade: {nome}")
                    
                    # Extrai endereço completo
                    endereco = ""
                    endereco_element = card.query_selector("div.ant-typography.css-xx138k")
                    if endereco_element:
                        endereco_raw = endereco_element.inner_text()
                        # Remove quebras de linha e espaços extras
                        endereco = " ".join(endereco_raw.splitlines()).strip()
                        print(f"    📍 Endereço extraído: '{endereco}'")
                    else:
                        print(f"    ⚠️ Não foi possível extrair endereço para {nome}")
                    
                    # Extrai cidade e estado do endereço
                    cidade, estado = extrair_cidade_estado(endereco)
                    
                    # Extrai link de matrícula/planos
                    link_matricula = ""
                    botao_element = card.query_selector("button.ant-btn")
                    if botao_element:
                        # Tenta extrair o texto do botão ou href se for um link
                        texto_botao = botao_element.inner_text().strip()
                        if texto_botao:
                            link_matricula = f"Botão: {texto_botao}"
                    
                    # Monta o dicionário da unidade
                    unidade = {
                        "rede": "Pratique Fitness",
                        "nome": nome,
                        "endereco": endereco,
                        "cidade": cidade,
                        "estado": estado,
                        "cep": "",
                        "telefone": "",
                        "latitude": "",
                        "longitude": "",
                        "horarios": {},
                        "servicos": [],
                        "link_matricula": link_matricula,
                        # Colunas CDN - preserva dados existentes se houver
                        "bairro_cdn": "",
                        "cidade_cdn": "",
                        "estado_cdn": "",
                        "pais_cdn": "",
                        # Timestamps - serão definidos automaticamente pelo modelo
                        "data_criacao": None,
                        "data_atualizacao": None
                    }
                    
                    # Verifica se é uma unidade nova (não existe no banco)
                    if nome not in unidades_existentes:
                        unidades_novas.append(unidade)
                        print(f"🆕 NOVA unidade encontrada: {nome}")
                    else:
                        # ATUALIZA a unidade existente com o endereço correto
                        print(f"🔄 ATUALIZANDO unidade existente: {nome}")
                        try:
                            # Busca a unidade existente no banco
                            session = db.Session()
                            unidade_existente = session.query(Unidade).filter_by(nome=nome).first()
                            if unidade_existente:
                                # Atualiza os campos
                                unidade_existente.endereco = endereco
                                unidade_existente.cidade = cidade
                                unidade_existente.estado = estado
                                unidade_existente.link_matricula = link_matricula
                                session.commit()
                                print(f"    ✅ Atualizada: endereço='{endereco}', cidade='{cidade}', estado='{estado}'")
                            session.close()
                        except Exception as e:
                            print(f"    ❌ Erro ao atualizar: {e}")
                            if 'session' in locals():
                                session.close()
                    
                    unidades_processadas.add(nome)
                    novos_cards += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")
                    continue

            print(f"📊 Total processado nesta execução: {len(unidades_processadas)} unidades")
            print(f"🆕 Novas unidades encontradas: {len(unidades_novas)}")
            
            # Se não encontrou novos cards, incrementa o contador
            if novos_cards == 0:
                scrolls_sem_novos_cards += 1
                print(f"⚠️ Scroll {scrolls_sem_novos_cards}/{max_scrolls_sem_novos} sem novos cards...")
            else:
                scrolls_sem_novos_cards = 0  # Reset do contador
            
            # Faz scroll incremental
            altura_atual = page.evaluate("document.documentElement.scrollHeight")
            if altura_atual > altura_anterior:
                print("🔄 Fazendo scroll incremental...")
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(2)  # Espera novos cards carregarem
                altura_anterior = altura_atual
            else:
                print("✅ Chegou ao final da página")
                break

        browser.close()
    
    # Salva as novas unidades no banco
    if unidades_novas:
        print(f"\n💾 Salvando {len(unidades_novas)} novas unidades no banco...")
        unidades_salvas = db.inserir_multiplas_unidades_dinamico(unidades_novas)
        print(f"✅ {unidades_salvas} unidades salvas com sucesso!")
    else:
        print("\nℹ️ Nenhuma nova unidade encontrada!")
    
    # Gera estatísticas e JSON atualizado
    estatisticas = db.estatisticas()
    print(f"\n📈 Estatísticas do banco:")
    print(f"   Total de unidades: {estatisticas['total_unidades']}")
    print(f"   Redes cadastradas: {', '.join(estatisticas['redes'])}")
    
    # Gera JSON com todas as unidades
    db.gerar_json("unidades_atualizadas.json")
    
    return unidades_novas, estatisticas

# Teste rápido
if __name__ == "__main__":
    print("🚀 Iniciando coleta INCREMENTAL de unidades da Pratique Fitness...")
    print("=" * 60)
    
    try:
        unidades_novas, estatisticas = coletar_unidades_pratique_incremental()
        
        print("\n" + "=" * 60)
        print("🎉 COLETA INCREMENTAL FINALIZADA!")
        
        if unidades_novas:
            print(f"\n🆕 Novas unidades adicionadas:")
            for i, u in enumerate(unidades_novas, 1):
                print(f"{i:2d}. {u['nome']} - {u['cidade']}, {u['estado']}")
                if u['endereco']:
                    print(f"    📍 {u['endereco']}")
                if u['link_matricula']:
                    print(f"    🔗 {u['link_matricula']}")
        else:
            print("\nℹ️ Nenhuma nova unidade foi adicionada ao banco.")
        
        print(f"\n📊 Resumo final:")
        print(f"   Unidades no banco: {estatisticas['total_unidades']}")
        print(f"   Última atualização: {estatisticas['ultima_atualizacao']}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
