from playwright.sync_api import sync_playwright
import time
import sys
import os
import json

# Adiciona o diretório pai ao path para importar os módulos do banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)

def preparar_unidade_dinamica(nome, dados_coletados, db, tabela="unidades"):
    """
    Prepara um dicionário de unidade pronto para inserção.
    Cria colunas novas automaticamente se necessário.
    Serializa dict/list em JSON quando necessário.
    """
    colunas_existentes = db.obter_colunas_tabela(tabela)

    unidade_final = {}
    for coluna, valor in dados_coletados.items():
        if coluna not in colunas_existentes:
            print(f"⚡ Coluna '{coluna}' não existe, criando no banco...")
            db.adicionar_coluna(tabela, coluna, tipo="TEXT")
            colunas_existentes.append(coluna)

        # Serializar listas/dicionários para JSON
        if isinstance(valor, (dict, list)):
            unidade_final[coluna] = json.dumps(valor, ensure_ascii=False)
        else:
            unidade_final[coluna] = valor

    obrigatorias = ["bairro_cdn", "cidade_cdn", "estado_cdn", "pais_cdn", "data_criacao", "data_atualizacao"]
    for col in obrigatorias:
        if col not in unidade_final:
            unidade_final[col] = None if "data" in col else ""

    return unidade_final

def coletar_unidades_panobianco():
    url = "https://panobiancoacademia.com.br/unidades/"
    unidades_novas = []
    unidades_processadas = set()

    print("🗄️ Conectando ao banco de dados...")
    db = Database()

    # ⚡ Garantir que os campos planos e beneficios existam
    db.adicionar_coluna("unidades", "planos", "TEXT")
    db.adicionar_coluna("unidades", "beneficios", "TEXT")

    unidades_existentes = db.buscar_nomes_existentes()
    print(f"📊 Unidades já existentes no banco: {len(unidades_existentes)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(300000)
        page.set_default_navigation_timeout(300000)

        print("🌐 Navegando para a página da Panobianco Academia...")
        page.goto(url)

        while True:
            cards = page.query_selector_all("div.elementor-element-f32c1f4")
            novos_cards = 0

            for card in cards:
                try:
                    nome_el = card.query_selector("h1.elementor-heading-title a")
                    nome = nome_el.inner_text().strip() if nome_el else "Sem nome"

                    if nome in unidades_processadas:
                        continue

                    endereco_el = card.query_selector("div.elementor-widget-text-editor")
                    endereco_raw = endereco_el.inner_text().strip() if endereco_el else ""

                    link_matricula_el = card.query_selector("a.elementor-button-link")
                    link_matricula = link_matricula_el.get_attribute("href") if link_matricula_el else ""

                    # Extrair planos e benefícios
                    planos = {}
                    beneficios = []
                    try:
                        gold = card.query_selector("div#id-gold-prec h2")
                        platinum = card.query_selector("div#id-plainum-prec h2")
                        if gold: planos["Gold"] = gold.inner_text().strip()
                        if platinum: planos["Platinum"] = platinum.inner_text().strip()

                        beneficio_items = card.query_selector_all("ul.elementor-icon-list-items li")
                        for item in beneficio_items:
                            texto = item.inner_text().strip()
                            if texto:
                                beneficios.append(texto)
                    except:
                        pass

                    dados_coletados = {
                        "rede": "Panobianco",
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
                        "link_matricula": link_matricula,
                        "planos": planos,
                        "beneficios": beneficios
                    }

                    unidade = preparar_unidade_dinamica(nome, dados_coletados, db)

                    if nome not in unidades_existentes:
                        db.inserir_unidade(unidade)
                        unidades_novas.append(unidade)
                        print(f"🆕 NOVA unidade salva: {nome}")
                    else:
                        print(f"ℹ️ Unidade já existe: {nome}")

                    unidades_processadas.add(nome)
                    novos_cards += 1

                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")

            print(f"📊 Total processado nesta página: {len(unidades_processadas)}")
            print(f"🆕 Novas unidades encontradas até agora: {len(unidades_novas)}")

            try:
                botao = page.query_selector("a.page-numbers.next")
                if botao and botao.is_visible():
                    print("🔄 Indo para a próxima página...")
                    botao.click()
                    time.sleep(2)
                    if novos_cards == 0:
                        time.sleep(2)
                        continue
                else:
                    print("✅ Todas as unidades foram carregadas!")
                    break
            except Exception as e:
                print(f"❌ Erro ao clicar no botão Próximo: {e}")
                break

        browser.close()

    if unidades_novas:
        print(f"\n💾 Total de novas unidades salvas: {len(unidades_novas)}")

    estatisticas = db.estatisticas()
    print(f"\n📈 Estatísticas do banco:")
    print(f"   Total de unidades: {estatisticas['total_unidades']}")
    print(f"   Redes cadastradas: {', '.join(estatisticas['redes'])}")

    db.gerar_json("unidades_atualizadas.json")
    return unidades_novas, estatisticas

if __name__ == "__main__":
    print("🚀 Iniciando coleta de unidades da Panobianco Academia...")
    try:
        unidades_novas, estatisticas = coletar_unidades_panobianco()
        print("\n🎉 Coleta finalizada!")
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
