import requests
import time
import sys
import os
from sqlalchemy import or_
from dotenv import load_dotenv  # <-- para ler o .env

# Carrega variáveis de ambiente do arquivo .env na raiz
load_dotenv()

# Lê a chave do Geocod.io
API_KEY = os.getenv("GEOCODIO_API_KEY")
if not API_KEY:
    print("❌ ERRO: variável GEOCODIO_API_KEY não encontrada no .env")
    sys.exit(1)

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

            print(f"[{i}/{total}] Geocodificando (Geocod.io): {endereco}")

            # Requisição ao Geocod.io
            url = "https://api.geocod.io/v1.7/geocode"
            params = {"q": endereco, "api_key": API_KEY}

            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data.get("results"):
                    loc = data["results"][0]["location"]
                    lat, lon = loc["lat"], loc["lng"]

                    u.latitude = lat
                    u.longitude = lon
                    session.commit()

                    print(f"    ✅ Coordenadas: {lat}, {lon}")
                    sucessos += 1
                else:
                    print(f"    ❌ Nenhum resultado encontrado")
                    falhas += 1

                time.sleep(0.5)  # respeita limites de uso da API

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
