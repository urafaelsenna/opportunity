import requests
import time
import sys
import os
from sqlalchemy import or_

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
    from database.models import Unidade
except ImportError:
    print("❌ Erro ao importar módulos do banco.")
    sys.exit(1)


def geocodificar_unidades():
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    session = db.Session()

    try:
        # Busca unidades sem coordenadas
        unidades_sem_coords = session.query(Unidade).filter(
            or_(
                Unidade.latitude.is_(None),
                Unidade.longitude.is_(None),
                Unidade.latitude == "",
                Unidade.longitude == ""
            )
        ).all()

        total = len(unidades_sem_coords)
        print(f"📊 Total de unidades sem coordenadas: {total}")

        sucessos = 0
        falhas = 0

        for i, u in enumerate(unidades_sem_coords, 1):
            endereco = u.endereco.strip()
            if not endereco:
                print(f"[{i}/{total}] ❌ Endereço vazio, pulando: {u.nome}")
                falhas += 1
                continue

            print(f"[{i}/{total}] Geocodificando: {endereco}")

            # Requisição ao Nominatim usando somente o endereço
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': endereco, 'format': 'json', 'limit': 1}
            headers = {'User-Agent': 'OpportunityGeocoder/1.0'}

            try:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data:
                    lat = data[0].get('lat')
                    lon = data[0].get('lon')
                    if lat and lon:
                        u.latitude = lat
                        u.longitude = lon
                        session.commit()
                        print(f"    ✅ Coordenadas: {lat}, {lon}")
                        sucessos += 1
                    else:
                        print(f"    ❌ Nenhum resultado encontrado")
                        falhas += 1
                else:
                    print(f"    ❌ Nenhum resultado encontrado")
                    falhas += 1

                time.sleep(3)  # respeita limite de 1 requisição por segundo

            except requests.exceptions.RequestException as e:
                print(f"    ❌ Erro na requisição: {e}")
                falhas += 1
            except Exception as e:
                print(f"    ❌ Erro inesperado: {e}")
                session.rollback()
                falhas += 1

        print(f"\n🎉 Geocodificação concluída! Sucessos: {sucessos}, Falhas: {falhas}")

    finally:
        session.close()


if __name__ == "__main__":
    geocodificar_unidades()
