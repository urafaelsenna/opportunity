import requests
import time
import sys
import os
from dotenv import load_dotenv
from sqlalchemy import or_

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    print("❌ Variável GOOGLE_MAPS_API_KEY não encontrada no .env")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
    from database.models import Unidade
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)


def extrair_componente(components, tipos):
    """Extrai o componente do endereço retornado pelo Google Maps."""
    for comp in components:
        for tipo in tipos:
            if tipo in comp['types']:
                return comp['long_name']
    return None


def geocode_nominatim(query=None, lat=None, lon=None):
    """Geocodificação Nominatim (forward ou reverse)."""
    url = "https://nominatim.openstreetmap.org/search" if query else "https://nominatim.openstreetmap.org/reverse"
    params = {"format": "json", "addressdetails": 1, "limit": 1, "countrycodes": "br"}
    headers = {"User-Agent": "geocode-script (contato@seudominio.com)"}

    if query:
        params["q"] = query
    else:
        params["lat"] = lat
        params["lon"] = lon

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        place = data[0] if query else data
        addr = place.get("address", {})
        return {
            "lat": place.get("lat"),
            "lon": place.get("lon"),
            "bairro": addr.get("suburb") or addr.get("neighbourhood"),
            "cidade": addr.get("city") or addr.get("town") or addr.get("municipality"),
            "estado": addr.get("state"),
            "pais": addr.get("country")
        }
    except Exception as e:
        print(f"    ❌ Erro Nominatim: {e}")
    return None


def geocode_google(query=None, lat=None, lon=None):
    """Geocodificação Google (forward ou reverse)."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"key": API_KEY, "region": "BR"}
    if query:
        params["address"] = query
    elif lat and lon:
        params["latlng"] = f"{lat},{lon}"
    else:
        return None

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data['status'] == 'OK' and data['results']:
            result = data['results'][0]
            location = result['geometry']['location']
            components = result.get('address_components', [])
            return {
                "lat": location.get('lat'),
                "lon": location.get('lng'),
                "bairro": extrair_componente(components, ['sublocality', 'sublocality_level_1', 'neighborhood']),
                "cidade": extrair_componente(components, ['locality', 'administrative_area_level_2']),
                "estado": extrair_componente(components, ['administrative_area_level_1']),
                "pais": extrair_componente(components, ['country'])
            }
    except Exception as e:
        print(f"    ❌ Erro Google: {e}")
    return None


def atualizar_unidade(u, dados):
    """Atualiza a unidade com os dados encontrados."""
    if not dados:
        return False
    u.latitude = u.latitude or dados.get("lat")
    u.longitude = u.longitude or dados.get("lon")
    u.bairro_cdn = u.bairro_cdn or dados.get("bairro")
    u.cidade_cdn = u.cidade_cdn or dados.get("cidade")
    u.estado_cdn = u.estado_cdn or dados.get("estado")
    u.pais_cdn = u.pais_cdn or dados.get("pais")
    return True


def geocodificar_unidades():
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    session = db.Session()

    try:
        # Busca unidades com alguma informação faltante
        unidades = session.query(Unidade).filter(
            or_(Unidade.latitude == None,
                Unidade.longitude == None,
                Unidade.bairro_cdn == None,
                Unidade.cidade_cdn == None,
                Unidade.estado_cdn == None,
                Unidade.pais_cdn == None)
        ).all()

        total = len(unidades)
        print(f"📊 Total de unidades a processar: {total}")

        sucessos_completos = 0
        sucessos_incompletos = 0
        falhas = 0

        for i, u in enumerate(unidades, 1):
            endereco = u.endereco.strip() if u.endereco else ""
            print(f"[{i}/{total}] Geocodificando: {endereco}")

            dados = None

            try:
                # --- 1ª tentativa: Google endereço ---
                if endereco:
                    dados = geocode_google(endereco) or geocode_nominatim(endereco)

                # --- 2ª tentativa: endereço + nome ---
                if not dados or not all([dados.get(k) for k in ["bairro","cidade","estado","pais"]]):
                    query_extra = f"{endereco}, {u.nome}"
                    extra = geocode_google(query_extra) or geocode_nominatim(query_extra)
                    if extra:
                        for k, v in extra.items():
                            if not dados.get(k):
                                dados[k] = v

                # --- 3ª tentativa: endereço + nome + rede ---
                if not dados or not all([dados.get(k) for k in ["bairro","cidade","estado","pais"]]):
                    query_extra2 = f"{endereco}, {u.nome}, {u.rede}"
                    extra2 = geocode_nominatim(query_extra2)
                    if extra2:
                        for k, v in extra2.items():
                            if not dados.get(k):
                                dados[k] = v

                # --- 4ª/5ª tentativa: reverse geocoding para complementar CDNs ---
                if u.latitude and u.longitude:
                    if not all([u.bairro_cdn, u.cidade_cdn, u.estado_cdn, u.pais_cdn]):
                        dados_rev = geocode_google(lat=u.latitude, lon=u.longitude) or geocode_nominatim(lat=u.latitude, lon=u.longitude)
                        if dados_rev:
                            for k, v in dados_rev.items():
                                if not dados.get(k):
                                    dados[k] = v

                # Atualiza e imprime status
                if atualizar_unidade(u, dados):
                    session.commit()
                    campos = [u.latitude, u.longitude, u.bairro_cdn, u.cidade_cdn, u.estado_cdn, u.pais_cdn]
                    if all(campos):
                        print(f"    ✅ Atualizado: {u.latitude}, {u.longitude}, "
                              f"{u.bairro_cdn}, {u.cidade_cdn}, {u.estado_cdn}, {u.pais_cdn}")
                        sucessos_completos += 1
                    else:
                        print(f"    ❌ Atualizado (incompleto): {u.latitude}, {u.longitude}, "
                              f"{u.bairro_cdn}, {u.cidade_cdn}, {u.estado_cdn}, {u.pais_cdn}")
                        sucessos_incompletos += 1
                else:
                    print("    ❌ Nenhum dado válido encontrado")
                    falhas += 1

                time.sleep(0.5)  # limite API

            except Exception as e:
                print(f"    ❌ Erro inesperado: {e}")
                session.rollback()
                falhas += 1

        print(f"\n🎉 Geocodificação concluída! "
              f"Sucessos completos: {sucessos_completos}, "
              f"Incompletos: {sucessos_incompletos}, "
              f"Falhas: {falhas}")

    finally:
        session.close()


if __name__ == "__main__":
    geocodificar_unidades()
