#!/usr/bin/env python3
"""
Script para corrigir a estrutura da tabela unidades no banco SQLite.
Adiciona PRIMARY KEY AUTOINCREMENT na coluna id.
"""

import sqlite3
import os
import sys

def corrigir_tabela_unidades():
    """Corrige a estrutura da tabela unidades adicionando PRIMARY KEY AUTOINCREMENT"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    print(f"🗄️ Conectando ao banco: {db_path}")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica estrutura atual
        print("\n📋 Estrutura atual da tabela:")
        cursor.execute("PRAGMA table_info(unidades)")
        colunas = cursor.fetchall()
        
        for col in colunas:
            print(f"   {col[1]} {col[2]} {'PRIMARY KEY' if col[5] else ''}")
        
        # Verifica se já tem PRIMARY KEY
        id_col = next((col for col in colunas if col[1] == 'id'), None)
        if id_col and id_col[5]:  # col[5] é pk
            print("\n✅ Coluna id já é PRIMARY KEY!")
            return True
        
        print("\n🔧 Corrigindo estrutura da tabela...")
        
        # Cria tabela temporária com estrutura correta
        print("   1. Criando tabela temporária...")
        cursor.execute("""
            CREATE TABLE unidades_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rede TEXT NOT NULL,
                nome TEXT NOT NULL UNIQUE,
                endereco TEXT NOT NULL,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                telefone TEXT,
                latitude TEXT,
                longitude TEXT,
                horarios NUMERIC,
                servicos NUMERIC,
                link_matricula TEXT,
                data_criacao NUMERIC,
                data_atualizacao NUMERIC,
                "bairro(cdn)" TEXT,
                "cidade(cdn)" TEXT,
                "estado(cdn)" TEXT,
                "pais(cdn)" TEXT
            )
        """)
        
        # Copia dados existentes
        print("   2. Copiando dados existentes...")
        cursor.execute("""
            INSERT INTO unidades_temp (
                rede, nome, endereco, cidade, estado, cep, telefone,
                latitude, longitude, horarios, servicos, link_matricula,
                data_criacao, data_atualizacao, "bairro(cdn)", "cidade(cdn)",
                "estado(cdn)", "pais(cdn)"
            )
            SELECT 
                rede, nome, endereco, cidade, estado, cep, telefone,
                latitude, longitude, horarios, servicos, link_matricula,
                data_criacao, data_atualizacao, "bairro(cdn)", "cidade(cdn)",
                "estado(cdn)", "pais(cdn)"
            FROM unidades
        """)
        
        # Remove tabela antiga
        print("   3. Removendo tabela antiga...")
        cursor.execute("DROP TABLE unidades")
        
        # Renomeia tabela temporária
        print("   4. Renomeando tabela corrigida...")
        cursor.execute("ALTER TABLE unidades_temp RENAME TO unidades")
        
        # Cria índices
        print("   5. Recriando índices...")
        cursor.execute("CREATE INDEX ix_unidades_rede ON unidades (rede)")
        cursor.execute("CREATE INDEX ix_unidades_nome ON unidades (nome)")
        cursor.execute("CREATE INDEX ix_unidades_cidade ON unidades (cidade)")
        cursor.execute("CREATE INDEX ix_unidades_estado ON unidades (estado)")
        
        # Commit das alterações
        conn.commit()
        
        # Verifica estrutura final
        print("\n📋 Nova estrutura da tabela:")
        cursor.execute("PRAGMA table_info(unidades)")
        colunas = cursor.fetchall()
        
        for col in colunas:
            pk_info = "PRIMARY KEY AUTOINCREMENT" if col[1] == 'id' and col[5] else ""
            print(f"   {col[1]} {col[2]} {pk_info}")
        
        # Verifica contagem de registros
        cursor.execute("SELECT COUNT(*) FROM unidades")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de registros preservados: {total}")
        
        print("\n✅ Tabela corrigida com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao corrigir tabela: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 CORRIGINDO ESTRUTURA DA TABELA UNIDADES")
    print("=" * 50)
    
    if corrigir_tabela_unidades():
        print("\n🎉 Correção concluída! Agora você pode executar o scraper Smartfit.")
        print("💡 Execute: python scraping/smartfit_scraper.py")
    else:
        print("\n❌ Falha na correção. Verifique os erros acima.")
        sys.exit(1)
