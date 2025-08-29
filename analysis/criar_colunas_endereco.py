import sys
import os
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulo do banco.")
    sys.exit(1)

def adicionar_colunas():
    print("🗄️ Conectando ao banco de dados...")
    db = Database()
    engine = db.engine
    inspector = inspect(engine)

    try:
        # Verifica se a tabela 'unidades' existe
        if 'unidades' not in inspector.get_table_names():
            print("❌ Tabela 'unidades' não encontrada.")
            return

        with engine.connect() as conn:
            # Lista de colunas a criar com nomes contendo (cdn)
            colunas = ['bairro(cdn)', 'cidade(cdn)', 'estado(cdn)', 'pais(cdn)']

            # Lista colunas já existentes
            existing_cols = [col['name'] for col in inspector.get_columns('unidades')]

            for coluna in colunas:
                if coluna not in existing_cols:
                    # Coloca o nome da coluna entre aspas duplas para aceitar parênteses
                    sql = f'ALTER TABLE unidades ADD COLUMN "{coluna}" TEXT;'
                    try:
                        conn.execute(text(sql))
                        print(f"✅ Coluna '{coluna}' criada com sucesso.")
                    except OperationalError as e:
                        print(f"❌ Erro ao criar coluna '{coluna}': {e}")
                else:
                    print(f"⚠️ Coluna '{coluna}' já existe, pulando.")

        print("\n🎉 Todas as colunas foram verificadas/atualizadas com sucesso!")

    finally:
        engine.dispose()

if __name__ == "__main__":
    adicionar_colunas()
