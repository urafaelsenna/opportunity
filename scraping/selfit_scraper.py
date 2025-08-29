from playwright.sync_api import sync_playwright
import time
import sys
import os
import re

# Adiciona o diretório pai ao path para importar os módulos do banco
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)

def extrair_endereco_cidade_estado(texto):
    """
    Extrai endereço, cidade e estado do texto padrão:
    "Avenida Abel Cabral, S/N, Nova Parnamirim, Parnamirim/RN, CEP: 59151-250"
    """
    endereco = cidade = estado = cep = ""
    try:
        # Divide por "CEP:" para separar o CEP
        if "CEP:" in texto:
            partes = texto.split("CEP:")
            cep = partes[1].strip()
            texto = partes[0].strip()
        
        # Divide por "/" para pegar cidade e estado
        if "/" in texto:
            prefixo, uf = texto.rsplit("/", 1)
            estado = uf.strip()
            cidade = prefixo.split(",")[-1].strip()
            endereco = ",".join(prefixo.split(",")[:-1]).strip()
        else:
            endereco = texto.strip()
    except Exception as e:
        print(f"⚠️ Erro ao processar endereço: {e}")
    return endereco, cidade, estado, cep

def coletar_unidades_selfit_incremental():
    url = "https://www.selfitacademias.com.br/unidades"
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
        page.goto(url)
        page.wait_for_selector("div.box-content", timeout=300000)

        while True:
            cards = page.query_selector_all("div.box-content")
            novos_cards = 0

            for card in cards:
                try:
                    nome_element = card.query_selector("h4")
                    if not nome_element:
                        continue
                    nome = nome_element.inner_text().strip()
                    if nome in unidades_processadas:
                        continue
                    print(f"🔍 Processando unidade: {nome}")

                    # Extrai endereço completo
                    endereco_element = card.query_selector("p.location.auto")
                    endereco_texto = endereco_element.inner_text().strip() if endereco_element else ""
                    endereco, cidade, estado, cep = extrair_endereco_cidade_estado(endereco_texto)

                    # Extrai link de matrícula
                    link_matricula_element = card.query_selector("a.button.red")
                    link_matricula = link_matricula_element.get_attribute("href") if link_matricula_element else ""

                    unidade = {
                        "rede": "Selfit",
                        "nome": nome,
                        "endereco": endereco,
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
                    else:
                        print(f"ℹ️ Unidade já existe: {nome}")

                    unidades_processadas.add(nome)
                    novos_cards += 1

                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")
                    continue

            print(f"📊 Total processado nesta execução: {len(unidades_processadas)} unidades")
            print(f"🆕 Novas unidades encontradas: {len(unidades_novas)}")

            # Verifica se ainda tem botão "Mostrar mais"
            try:
                botao = page.query_selector("a.more")
                if botao and botao.is_visible():
                    print("🔄 Clicando em 'Mostrar mais'...")
                    botao.click()
                    time.sleep(3)
                    if novos_cards == 0:
                        time.sleep(5)
                        continue
                else:
                    print("✅ Botão 'Mostrar mais' não encontrado - todas as unidades foram carregadas!")
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

    # Estatísticas e JSON atualizado
    estatisticas = db.estatisticas()
    print(f"\n📈 Estatísticas do banco:")
    print(f"   Total de unidades: {estatisticas['total_unidades']}")
    print(f"   Redes cadastradas: {', '.join(estatisticas['redes'])}")
    
    # Gera JSON com todas as unidades
    db.gerar_json("unidades_atualizadas.json")

    return unidades_novas, estatisticas

# Teste rápido
if __name__ == "__main__":
    print("🚀 Iniciando coleta INCREMENTAL de unidades da Selfit...")
    print("=" * 60)
    
    try:
        unidades_novas, estatisticas = coletar_unidades_selfit_incremental()
        
        print("\n" + "=" * 60)
        print("🎉 COLETA INCREMENTAL FINALIZADA!")
        
        if unidades_novas:
            print(f"\n🆕 Novas unidades adicionadas:")
            for i, u in enumerate(unidades_novas, 1):
                print(f"{i:2d}. {u['nome']} - {u['cidade']}, {u['estado']}")
                if u['cep']:
                    print(f"    📮 CEP: {u['cep']}")
                if u['link_matricula']:
                    print(f"    🔗 Matrícula: {u['link_matricula']}")
        else:
            print("\nℹ️ Nenhuma nova unidade foi adicionada ao banco.")
        
        print(f"\n📊 Resumo final:")
        print(f"   Unidades no banco: {estatisticas['total_unidades']}")
        print(f"   Última atualização: {estatisticas['ultima_atualizacao']}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
