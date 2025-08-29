from playwright.sync_api import sync_playwright
import time
import sys
import os

# Adiciona o diretório pai ao path para importar os módulos do banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)

BATCH_SIZE = 100  # salva em blocos de 100 unidades

def coletar_unidades_skyfit():
    """
    Coleta unidades da Skyfit de forma incremental, salvando em blocos de 100,
    evitando duplicatas e garantindo integridade do banco.
    """
    url_base = "https://skyfitacademia.com/unidades/"
    unidades_novas = []
    unidades_processadas = set()
    
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    unidades_existentes = db.buscar_nomes_existentes()
    print(f"📊 Unidades já existentes no banco: {len(unidades_existentes)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(300000)
        page.set_default_navigation_timeout(300000)

        pagina_atual = 1
        while True:
            url = url_base if pagina_atual == 1 else f"{url_base}page/{pagina_atual}/"
            print(f"🌐 Acessando página {pagina_atual}: {url}")
            page.goto(url)
            time.sleep(2)

            cards = page.query_selector_all("article.unidade, div.unidade")
            if not cards:
                print("⚠️ Nenhum card encontrado nesta página, finalizando...")
                break

            for card in cards:
                try:
                    nome = card.query_selector("h1.elementor-heading-title").inner_text().strip()
                    endereco_raw = card.query_selector("span.elementor-icon-list-text").inner_text().strip()

                    if nome in unidades_processadas:
                        continue

                    # Cria unidade com TODAS as colunas para preservar dados existentes
                    unidade = {
                        "rede": "Skyfit",
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

                    if nome not in unidades_existentes:
                        unidades_novas.append(unidade)
                        print(f"🆕 NOVA unidade encontrada: {nome}")

                        # Salva em blocos de BATCH_SIZE
                        if len(unidades_novas) >= BATCH_SIZE:
                            print(f"\n💾 Salvando bloco de {len(unidades_novas)} unidades...")
                            db.inserir_multiplas_unidades_dinamico(unidades_novas)
                            unidades_novas = []

                    else:
                        print(f"ℹ️ Unidade já existe: {nome}")

                    unidades_processadas.add(nome)

                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")

            # Verifica se existe botão "Próximo »"
            try:
                botao_next = page.query_selector("a.page-numbers.next")
                if botao_next and botao_next.is_visible():
                    pagina_atual += 1
                else:
                    print("✅ Última página alcançada!")
                    break
            except Exception as e:
                print(f"❌ Erro ao verificar botão 'Próximo': {e}")
                break

        browser.close()

    # Salva unidades restantes
    if unidades_novas:
        print(f"\n💾 Salvando {len(unidades_novas)} unidades restantes...")
        db.inserir_multiplas_unidades_dinamico(unidades_novas)

    # Gera estatísticas e JSON atualizado
    estatisticas = db.estatisticas()
    print(f"\n📈 Estatísticas do banco:")
    print(f"   Total de unidades: {estatisticas['total_unidades']}")
    print(f"   Redes cadastradas: {', '.join(estatisticas['redes'])}")

    db.gerar_json("unidades_atualizadas.json")
    return unidades_novas, estatisticas

# Teste rápido
if __name__ == "__main__":
    print("🚀 Iniciando coleta INCREMENTAL de unidades da Skyfit...")
    print("=" * 60)
    try:
        unidades_novas, estatisticas = coletar_unidades_skyfit()
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
