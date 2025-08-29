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

def coletar_unidades_smartfit():
    """
    Coleta todas as unidades da Smartfit, evitando duplicatas
    e salvando apenas novas unidades no banco de dados.
    """
    url = "https://www.smartfit.com.br/academias"
    unidades_novas = []
    unidades_processadas = set()  # IDs já processados nesta execução

    # Inicializa banco e carrega unidades existentes
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    unidades_existentes = db.buscar_nomes_existentes()
    print(f"📊 Unidades já existentes no banco: {len(unidades_existentes)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(300000)  # 5 minutos
        page.set_default_navigation_timeout(300000)

        print("🌐 Navegando para a página da Smartfit...")
        page.goto(url)

        while True:
            # Seleciona todos os cards visíveis
            cards = page.query_selector_all("div.locations-v4-location-card")
            novos_cards = 0

            for card in cards:
                try:
                    unidade_id = card.get_attribute("data-smart-location-id")
                    if unidade_id in unidades_processadas:
                        continue  # já processada nesta execução

                    nome = card.query_selector("smart-text[as='h3']").inner_text().strip()
                    endereco_raw = card.query_selector("smart-text.locations-v4-location-card__address").inner_text().strip()
                    
                    unidade = {
                        "rede": "Smartfit",
                        "nome": nome,
                        "endereco": endereco_raw,
                        "cidade": "",
                        "estado": "",
                        "cep": "",
                        "telefone": "",
                        "latitude": "",
                        "longitude": "",
                        "horarios": {},
                        "servicos": [],
                        "link_matricula": "",
                        # Colunas CDN - preserva dados existentes se houver
                        "bairro_cdn": "",
                        "cidade_cdn": "",
                        "estado_cdn": "",
                        "pais_cdn": "",
                        # Timestamps - serão definidos automaticamente pelo modelo
                        "data_criacao": None,
                        "data_atualizacao": None
                    }

                    # Adiciona apenas se não existir no banco
                    if nome not in unidades_existentes:
                        unidades_novas.append(unidade)
                        print(f"🆕 NOVA unidade encontrada: {nome}")
                    else:
                        print(f"ℹ️ Unidade já existe: {nome}")

                    unidades_processadas.add(unidade_id)
                    novos_cards += 1

                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")

            print(f"📊 Total processado nesta página: {len(unidades_processadas)}")
            print(f"🆕 Novas unidades encontradas até agora: {len(unidades_novas)}")

            # Verifica botão "Ver mais"
            try:
                botao = page.query_selector("button.locations-v4-pagination-button")
                if botao and botao.is_visible():
                    print("🔄 Clicando em 'Ver mais' para carregar novas unidades...")
                    botao.click()
                    time.sleep(2)
                    if novos_cards == 0:
                        print("⚠️ Nenhum novo card carregou após clicar, tentando mais uma vez...")
                        time.sleep(2)
                        continue
                else:
                    print("✅ Todas as unidades foram carregadas!")
                    break
            except Exception as e:
                print(f"❌ Erro ao clicar no botão 'Ver mais': {e}")
                break

        browser.close()

    # Salva novas unidades no banco
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

    db.gerar_json("unidades_atualizadas.json")
    return unidades_novas, estatisticas

# Teste rápido
if __name__ == "__main__":
    print("🚀 Iniciando coleta INCREMENTAL de unidades da Smartfit...")
    print("=" * 60)
    try:
        unidades_novas, estatisticas = coletar_unidades_smartfit()
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
