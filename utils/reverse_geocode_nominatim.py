import sqlite3
import requests
import time

DB_PATH = "./unidades.db"

def create_columns_if_not_exist(conn):
    """Cria colunas para reverse geocode caso ainda não existam"""
    cursor = conn.cursor()
    new_columns = ["bairro_codn", "cidade_codn", "estado_codn", "pais_codn"]
    for col in new_columns:
        cursor.execute(f"PRAGMA table_info(unidades)")
        cols = [c[1] for c in cursor.fetchall()]
        if col not in cols:
            cursor.execute(f"ALTER TABLE unidades ADD COLUMN {col} TEXT")
            print(f"✅ Coluna adicionada: {col}")
    conn.commit()

def reverse_geocode(lat, lon):
    """Consulta o Nominatim para obter bairro, cidade, estado, país"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "accept-language": "pt"
    }
    headers = {"User-Agent": "opportunity-geocoder/1.0"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        address = data.get("address", {})

        bairro = address.get("suburb") or address.get("neighbourhood") or ""
        cidade = address.get("city") or address.get("town") or address.get("municipality") or address.get("village") or ""
        estado = address.get("state", "")
        pais = address.get("country", "")

        return bairro, cidade, estado, pais

    except Exception as e:
        print(f"⚠️ Erro no reverse geocode ({lat}, {lon}): {e}")
        return None, None, None, None

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Garante que as colunas novas existam
    create_columns_if_not_exist(conn)

    # Seleciona apenas registros com coordenadas válidas
    cursor.execute("""
        SELECT id, latitude, longitude FROM unidades
        WHERE latitude IS NOT NULL AND latitude != ''
          AND longitude IS NOT NULL AND longitude != ''
    """)
    unidades = cursor.fetchall()
    print(f"📊 Total de registros com coordenadas: {len(unidades)}")

    for idx, (uid, lat, lon) in enumerate(unidades, start=1):
        print(f"\n[{idx}/{len(unidades)}] Processando ID {uid}...")
        bairro, cidade, estado, pais = reverse_geocode(lat, lon)

        if bairro or cidade or estado or pais:
            cursor.execute("""
                UPDATE unidades
                SET bairro_codn = ?, cidade_codn = ?, estado_codn = ?, pais_codn = ?
                WHERE id = ?
            """, (bairro, cidade, estado, pais, uid))
            conn.commit()
            print(f"✅ Atualizado: {bairro}, {cidade}, {estado}, {pais}")
        else:
            print("⚠️ Nenhum dado encontrado.")

        time.sleep(1)  # respeita limite de requisições do Nominatim

    conn.close()
    print("\n🎉 Reverse geocoding concluído!")

if __name__ == "__main__":
    main()
