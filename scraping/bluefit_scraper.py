from playwright.sync_api import sync_playwright
import time
import sys
import os

# Adiciona o diretório pai ao path para importar os módulos do banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulos do banco. Verificando estrutura...")
    import os
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📁 Arquivos disponíveis: {os.listdir('.')}")
    print(f"📁 Arquivos no diretório pai: {os.listdir('..')}")
    sys.exit(1)

def coletar_unidades_incremental():
    """
    Coleta unidades da Bluefit de forma incremental, evitando duplicatas
    e salvando apenas novas unidades no banco de dados
    """
    url = "https://www.bluefit.com.br/unidades"
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
        
        print("🌐 Navegando para a página da Bluefit...")
        page.goto(url)

        # Espera os cards carregarem
        print("⏳ Aguardando carregamento dos cards...")
        page.wait_for_selector("div.unidades_card", timeout=300000)

        while True:
            # Processa os cards visíveis ATUALMENTE
            cards = page.query_selector_all("div.unidades_card")
            novos_cards = 0
            
            for card in cards:
                try:
                    nome = card.query_selector("h4.is-unity-titles").inner_text().strip()
                    
                    # Evita processar o mesmo card duas vezes nesta execução
                    if nome in unidades_processadas:
                        continue
                    
                    endereco_raw = card.query_selector("div.text-size-small").inner_text().strip()
                    endereco = " ".join(endereco_raw.splitlines())
                    
                    unidade = {
                        "rede": "Bluefit",
                        "nome": nome,
                        "endereco": endereco,
                        "cidade": "",  # Bluefit não tem cidade separada
                        "estado": "",  # Bluefit não tem estado separado
                        "cep": "",     # Bluefit não tem CEP
                        "telefone": "", # Bluefit não tem telefone
                        "latitude": "",
                        "longitude": "",
                        "horarios": {},  # Bluefit não tem horários
                        "servicos": [],  # Bluefit não tem serviços
                        "link_matricula": "",  # Bluefit não tem link de matrícula
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
                        print(f"ℹ️ Unidade já existe: {nome}")
                    
                    unidades_processadas.add(nome)
                    novos_cards += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")

            print(f"📊 Total processado nesta execução: {len(unidades_processadas)} unidades")
            print(f"🆕 Novas unidades encontradas: {len(unidades_novas)}")
            
            # Verifica se ainda tem botão "Carregar mais"
            try:
                botao = page.query_selector("a#show-more")
                if botao and botao.is_visible():
                    print("🔄 Clicando em 'Carregar mais'...")
                    botao.click()
                    time.sleep(2)  # espera novos cards carregarem
                    
                    # Se não processou novos cards após clicar, pode ter acabado
                    if novos_cards == 0:
                        print("⚠️ Nenhum novo card carregou, tentando mais uma vez...")
                        time.sleep(3)
                        continue
                else:
                    print("✅ Botão 'Carregar mais' não encontrado - todas as unidades foram carregadas!")
                    break
            except Exception as e:
                print(f"❌ Erro ao clicar no botão: {e}")
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
    print("🚀 Iniciando coleta INCREMENTAL de unidades da Bluefit...")
    print("=" * 60)
    
    try:
        unidades_novas, estatisticas = coletar_unidades_incremental()
        
        print("\n" + "=" * 60)
        print("🎉 COLETA INCREMENTAL FINALIZADA!")
        
        if unidades_novas:
            print(f"\n🆕 Novas unidades adicionadas:")
            for i, u in enumerate(unidades_novas, 1):
                print(f"{i:2d}. {u['nome']} - {u['endereco']}")
        else:
            print("\nℹ️ Nenhuma nova unidade foi adicionada ao banco.")
        
        print(f"\n📊 Resumo final:")
        print(f"   Unidades no banco: {estatisticas['total_unidades']}")
        print(f"   Última atualização: {estatisticas['ultima_atualizacao']}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
