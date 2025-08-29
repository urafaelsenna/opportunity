import asyncio
import time
import re
from playwright.async_api import async_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Unidade

# ==============================
# Função para copiar coordenadas via clique direto (direito → esquerdo)
# ==============================
async def copiar_coords_via_click(page):
    try:
        # Clique direito no centro do mapa
        await page.mouse.click(x=640, y=360, button="right")
        await page.wait_for_timeout(200)  # Pequena pausa para o menu abrir
        
        # Clique esquerdo na mesma posição (primeira opção = copiar coordenadas)
        await page.mouse.click(x=640, y=360, button="left")
        await page.wait_for_timeout(300)  # Espera o clipboard atualizar
        
        # Ler coordenadas do clipboard
        coords_text = await page.evaluate("navigator.clipboard.readText()")
        match = re.match(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', coords_text)
        if match:
            return match.groups()
        else:
            print("   ⚠️ Coordenadas não foram extraídas corretamente")
            return None
    except Exception as e:
        print(f"   ⚠️ Erro ao copiar coordenadas via clique: {e}")
        return None

# ==============================
# Função para verificar se há múltiplos resultados
# ==============================
async def verificar_multiplos_resultados(page):
    try:
        # Cada link <a class="hfpxzc"> representa um resultado sugerido
        resultados = await page.query_selector_all('a.hfpxzc')
        # Mais de um resultado significa endereço ambíguo
        return len(resultados) > 1
    except:
        return False

# ==============================
# Processo principal
# ==============================
async def geocode_com_clique():
    print("🚀 Iniciando geocodificação com clique no Google Maps")
    print("=" * 60)

    engine = create_engine("sqlite:///./unidades.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Buscar unidades sem coordenadas
    unidades_sem_coords = (
        session.query(Unidade)
        .filter((Unidade.latitude == "") | (Unidade.latitude.is_(None)))
        .all()
    )

    print(f"📊 Total de unidades sem coordenadas: {len(unidades_sem_coords)}")
    if not unidades_sem_coords:
        print("✅ Nenhuma unidade pendente!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        await page.goto("https://www.google.com/maps", wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        # Aceitar cookies, se necessário
        try:
            await page.wait_for_selector('button[aria-label*="Aceitar"]', timeout=5000)
            await page.click('button[aria-label*="Aceitar"]')
        except:
            pass

        for idx, unidade in enumerate(unidades_sem_coords, start=1):
            print(f"\n📍 [{idx}/{len(unidades_sem_coords)}] {unidade.nome} ({unidade.rede})")
            print(f"   📍 Endereço: {unidade.endereco}")

            try:
                # Preencher endereço
                await page.fill("input#searchboxinput", "")
                await page.fill("input#searchboxinput", unidade.endereco)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(7000)  # espera mapa carregar

                # Verifica se há múltiplos resultados
                if await verificar_multiplos_resultados(page):
                    print("   ⚠️ Múltiplos resultados encontrados. Pulando sem alterar o banco.")
                    continue  # pula clique direito

                # Copiar coordenadas via clique direto
                coords = await copiar_coords_via_click(page)
                if coords:
                    lat, lng = coords
                    unidade.latitude = str(lat)
                    unidade.longitude = str(lng)
                    session.commit()
                    print(f"   ✅ Coordenadas encontradas: {lat}, {lng}")
                else:
                    print("   ❌ Não foi possível encontrar coordenadas")
                    # Mantém NULL ou "" no banco

            except Exception as e:
                print(f"   ⚠️ Erro ao processar: {e}")
                # Não altera campos no banco em caso de erro

            # Pausa para evitar bloqueios
            time.sleep(3)

        await browser.close()
    session.close()
    print("\n🎉 Geocodificação concluída!")

# ==============================
# Execução
# ==============================
if __name__ == "__main__":
    asyncio.run(geocode_com_clique())
