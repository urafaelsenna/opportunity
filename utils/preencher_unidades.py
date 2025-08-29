import os
import sqlite3
import sys

# ===========================
# CONFIGURAÇÃO INICIAL
# ===========================
# Coluna para preenchimento manual:
# - "coords" para preencher latitude e longitude juntas
# - ou qualquer coluna CDN: bairro_cdn, cidade_cdn, estado_cdn, pais_cdn
coluna_filtrar = "coords"

# Caminho do banco (ajuste se necessário)
db_path = os.path.join(os.path.dirname(__file__), "../unidades.db")

# ===========================
# Checa se o banco existe
# ===========================
if not os.path.isfile(db_path):
    print(f"❌ Banco de dados não encontrado em: {db_path}")
    sys.exit(1)

# ===========================
# Conecta ao banco
# ===========================
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ===========================
# Checa se a tabela existe
# ===========================
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unidades';")
if not cursor.fetchone():
    print("❌ Tabela 'unidades' não encontrada no banco.")
    conn.close()
    sys.exit(1)

# ===========================
# Busca registros faltantes
# ===========================
if coluna_filtrar == "coords":
    query = """
    SELECT id, rede, nome, endereco, latitude, longitude
    FROM unidades
    WHERE latitude IS NULL OR latitude = '' OR longitude IS NULL OR longitude = ''
    """
else:
    query = f"""
    SELECT id, rede, nome, endereco, {coluna_filtrar}
    FROM unidades
    WHERE {coluna_filtrar} IS NULL OR {coluna_filtrar} = ''
    """

cursor.execute(query)
registros = cursor.fetchall()
total = len(registros)

print(f"\n📊 Total de registros com '{coluna_filtrar}' faltando: {total}\n")

if total == 0:
    print("Nada para preencher manualmente. Saindo...")
    conn.close()
    sys.exit(0)

# ===========================
# Loop de preenchimento manual
# ===========================
for i, registro in enumerate(registros, 1):
    if coluna_filtrar == "coords":
        uid, rede, nome, endereco, lat, lon = registro
        print(f"[{i}/{total}] {rede} - {nome}")
        print(f"    Endereço: {endereco}")
        print(f"    Latitude atual: {lat}, Longitude atual: {lon}")
        entrada = input("    Digite nova LAT e LONG separadas por vírgula (ou ENTER para pular): ").strip()
        if entrada:
            try:
                nova_lat_str, nova_lon_str = map(str.strip, entrada.split(","))
                nova_lat = float(nova_lat_str)
                nova_lon = float(nova_lon_str)
                cursor.execute("""
                    UPDATE unidades
                    SET latitude = ?, longitude = ?
                    WHERE id = ?
                """, (nova_lat, nova_lon, uid))
                conn.commit()
                print(f"    ✅ Atualizado para: Latitude={nova_lat}, Longitude={nova_lon}\n")
            except ValueError:
                print("    ❌ Entrada inválida. Deve ser dois números separados por vírgula. Pulando...\n")
        else:
            print("    ⏭ Pulado\n")
    else:
        uid, rede, nome, endereco, valor_atual = registro
        print(f"[{i}/{total}] {rede} - {nome}")
        print(f"    Endereço: {endereco}")
        print(f"    Valor atual ({coluna_filtrar}): {valor_atual}")
        novo_valor = input(f"    Digite o novo valor para '{coluna_filtrar}' (ou ENTER para pular): ").strip()
        if novo_valor:
            cursor.execute(f"""
                UPDATE unidades
                SET {coluna_filtrar} = ?
                WHERE id = ?
            """, (novo_valor, uid))
            conn.commit()
            print(f"    ✅ Atualizado para: {novo_valor}\n")
        else:
            print("    ⏭ Pulado\n")

# ===========================
# Fechamento
# ===========================
conn.close()
print("🎉 Preenchimento manual concluído!")
