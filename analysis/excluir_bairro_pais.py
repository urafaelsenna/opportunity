import sys
import os
from sqlalchemy import create_engine, text, inspect

# Adiciona raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db import Database
except ImportError:
    print("❌ Erro ao importar módulo do banco.")
    sys.exit(1)

def excluir_colunas_antigas():
    db = Database()
    engine = db.engine
    inspector = inspect(engine)
    
    # Verifica se tabela existe
    if 'unidades' not in inspector.get_table_names():
        print("❌ Tabela 'unidades' não encontrada.")
        return
    
    # Lista de colunas existentes
    existing_cols = [col['name'] for col in inspector.get_columns('unidades')]
    
    # Colunas que queremos manter
    colunas_mantidas = [col for col in existing_cols if col not in ('bairro', 'pais')]
    
    # Cria SQL para copiar dados
    colunas_str = ', '.join([f'"{c}"' for c in colunas_mantidas])
    
    with engine.connect() as conn:
        # Cria tabela temporária sem as colunas antigas
        conn.execute(text(f'CREATE TABLE unidades_temp AS SELECT {colunas_str} FROM unidades;'))
        
        # Apaga tabela antiga
        conn.execute(text('DROP TABLE unidades;'))
        
        # Renomeia tabela temporária
        conn.execute(text('ALTER TABLE unidades_temp RENAME TO unidades;'))
        
    print("✅ Colunas 'bairro' e 'pais' removidas com sucesso!")

if __name__ == "__main__":
    excluir_colunas_antigas()
