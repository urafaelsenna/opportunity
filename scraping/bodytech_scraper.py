from playwright.sync_api import sync_playwright
import time
import sys
import os
import re
from urllib.parse import urlparse, parse_qs

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

def extrair_coordenadas_google_maps(url):
    """Extrai latitude e longitude de URLs do Google Maps"""
    try:
        if 'maps/dir' in url:
            # Padrão: https://maps.google.com/maps/dir/?api=1&destination=-23.5505,-46.6333
            if 'destination=' in url:
                coords = url.split('destination=')[1].split('&')[0]
                lat, lng = coords.split(',')
                return lat.strip(), lng.strip()
            
            # Padrão alternativo: https://maps.google.com/maps/dir/-23.5505,-46.6333
            elif '/maps/dir/' in url:
                coords = url.split('/maps/dir/')[1].split('/')[0]
                if ',' in coords:
                    lat, lng = coords.split(',')
                    return lat.strip(), lng.strip()
        
        return None, None
    except Exception as e:
        print(f"⚠️ Erro ao extrair coordenadas de {url}: {e}")
        return None, None

def extrair_horarios(horarios_element):
    """Extrai horários de funcionamento"""
    try:
        horarios = {}
        dias = horarios_element.query_selector_all("div.row.no-gutters.text-center")
        
        for dia in dias:
            try:
                texto = dia.inner_text().strip()
                if texto:
                    # Identifica o tipo de dia pelo texto
                    if 'seg' in texto.lower() or 'sex' in texto.lower():
                        horarios["Seg a Sex"] = texto
                    elif 'sáb' in texto.lower() or 'sab' in texto.lower():
                        horarios["Sábados"] = texto
                    elif 'dom' in texto.lower() or 'feri' in texto.lower():
                        horarios["Domingos e Feriados"] = texto
                    else:
                        # Se não conseguir identificar, usa o texto como está
                        horarios[texto] = texto
            except Exception as e:
                print(f"⚠️ Erro ao processar horário: {e}")
                continue
        
        return horarios
    except Exception as e:
        print(f"⚠️ Erro ao extrair horários: {e}")
        return {}

def extrair_servicos(servicos_element):
    """Extrai serviços disponíveis na unidade"""
    try:
        servicos = []
        icons = servicos_element.query_selector_all("div.services-separator img.benefit-icon")
        
        for icon in icons:
            try:
                alt_text = icon.get_attribute("alt")
                if alt_text and alt_text.strip():
                    servicos.append(alt_text.strip())
            except Exception as e:
                print(f"⚠️ Erro ao processar serviço: {e}")
                continue
        
        return servicos
    except Exception as e:
        print(f"⚠️ Erro ao extrair serviços: {e}")
        return []

def coletar_unidades_bodytech_incremental():
    """
    Coleta unidades da BodyTech de forma incremental, evitando duplicatas
    e salvando apenas novas unidades no banco de dados
    """
    url = "https://www.bodytech.com.br/academias"
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
        
        print("🌐 Navegando para a página da BodyTech...")
        page.goto(url)

        # Espera os cards carregarem
        print("⏳ Aguardando carregamento dos cards...")
        page.wait_for_selector("div.gym-info-container", timeout=300000)

        while True:
            # Processa os cards visíveis ATUALMENTE
            cards = page.query_selector_all("div.gym-info-container")
            novos_cards = 0
            
            for card in cards:
                try:
                    # Extrai nome da unidade
                    nome_element = card.query_selector("a.text-truncate")
                    if not nome_element:
                        continue
                    
                    nome = nome_element.inner_text().strip()
                    
                    # Evita processar o mesmo card duas vezes nesta execução
                    if nome in unidades_processadas:
                        continue
                    
                    print(f"🔍 Processando unidade: {nome}")
                    
                    # Extrai endereço completo
                    endereco_parts = []
                    endereco_elements = card.query_selector_all("p.m-0")
                    
                    for i, elem in enumerate(endereco_elements):
                        texto = elem.inner_text().strip()
                        if texto and not texto.startswith("CEP:"):
                            endereco_parts.append(texto)
                    
                    endereco_completo = " - ".join(endereco_parts) if endereco_parts else ""
                    
                    # Extrai cidade e estado do endereço
                    cidade = ""
                    estado = ""
                    if len(endereco_parts) >= 2:
                        ultima_parte = endereco_parts[-1]
                        if "," in ultima_parte:
                            cidade, estado = ultima_parte.split(",", 1)
                            cidade = cidade.strip()
                            estado = estado.strip()
                    
                    # Extrai CEP
                    cep = ""
                    for elem in endereco_elements:
                        texto = elem.inner_text().strip()
                        if texto.startswith("CEP:"):
                            cep = texto.replace("CEP:", "").strip()
                            break
                    
                    # Extrai telefone
                    telefone = ""
                    telefone_element = card.query_selector("a[href^='tel:']")
                    if telefone_element:
                        href = telefone_element.get_attribute("href")
                        telefone = href.replace("tel:", "") if href else ""
                    
                    # Extrai coordenadas do Google Maps
                    latitude = ""
                    longitude = ""
                    maps_element = card.query_selector("a[href*='maps/dir']")
                    if maps_element:
                        href = maps_element.get_attribute("href")
                        if href:
                            lat, lng = extrair_coordenadas_google_maps(href)
                            latitude = lat if lat else ""
                            longitude = lng if lng else ""
                    
                    # Extrai horários de funcionamento
                    horarios = {}
                    horarios_element = card.query_selector("app-gym-business-hours")
                    if horarios_element:
                        horarios = extrair_horarios(horarios_element)
                    
                    # Extrai serviços
                    servicos = []
                    servicos_element = card.query_selector("div.services-separator")
                    if servicos_element:
                        servicos = extrair_servicos(servicos_element)
                    
                    # Extrai link de matrícula
                    link_matricula = ""
                    matricula_element = card.query_selector("a.btn.btn-primary.w-100")
                    if matricula_element:
                        href = matricula_element.get_attribute("href")
                        link_matricula = href if href else ""
                    
                    # Monta o dicionário da unidade
                    unidade = {
                        "rede": "Bodytech",
                        "nome": nome,
                        "endereco": endereco_completo,
                        "cidade": cidade,
                        "estado": estado,
                        "cep": cep,
                        "telefone": telefone,
                        "latitude": latitude,
                        "longitude": longitude,
                        "horarios": horarios,
                        "servicos": servicos,
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
                        print(f"ℹ️ Unidade já existe: {nome}")
                    
                    unidades_processadas.add(nome)
                    novos_cards += 1
                    
                except Exception as e:
                    print(f"❌ Erro ao processar card: {e}")
                    continue

            print(f"📊 Total processado nesta execução: {len(unidades_processadas)} unidades")
            print(f"🆕 Novas unidades encontradas: {len(unidades_novas)}")
            
            # Verifica se ainda tem botão "Carregar mais"
            try:
                botao = page.query_selector("a#gym-load-more")
                if botao and botao.is_visible():
                    print("🔄 Clicando em 'Carregar mais'...")
                    botao.click()
                    time.sleep(3)  # espera novos cards carregarem
                    
                    # Se não processou novos cards após clicar, pode ter acabado
                    if novos_cards == 0:
                        print("⚠️ Nenhum novo card carregou, tentando mais uma vez...")
                        time.sleep(5)
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
    print("🚀 Iniciando coleta INCREMENTAL de unidades da BodyTech...")
    print("=" * 60)
    
    try:
        unidades_novas, estatisticas = coletar_unidades_bodytech_incremental()
        
        print("\n" + "=" * 60)
        print("🎉 COLETA INCREMENTAL FINALIZADA!")
        
        if unidades_novas:
            print(f"\n🆕 Novas unidades adicionadas:")
            for i, u in enumerate(unidades_novas, 1):
                print(f"{i:2d}. {u['nome']} - {u['cidade']}, {u['estado']}")
                if u['telefone']:
                    print(f"    📞 {u['telefone']}")
                if u['latitude'] and u['longitude']:
                    print(f"    📍 {u['latitude']}, {u['longitude']}")
        else:
            print("\nℹ️ Nenhuma nova unidade foi adicionada ao banco.")
        
        print(f"\n📊 Resumo final:")
        print(f"   Unidades no banco: {estatisticas['total_unidades']}")
        print(f"   Última atualização: {estatisticas['ultima_atualizacao']}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
