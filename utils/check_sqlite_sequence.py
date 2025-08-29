#!/usr/bin/env python3
"""
Script para verificar e corrigir a tabela sqlite_sequence.
Garante que o AUTOINCREMENT funcione corretamente no SQLite.
"""

import sqlite3
import os
import sys

def verificar_sqlite_sequence():
    """Verifica e corrige a tabela sqlite_sequence"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    print(f"🗄️ Conectando ao banco: {db_path}")
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica estrutura da tabela unidades
        print("\n📋 Estrutura da tabela unidades:")
        cursor.execute("PRAGMA table_info(unidades)")
        colunas = cursor.fetchall()
        
        id_col = None
        for col in colunas:
            print(f"   {col[1]} {col[2]} {'PRIMARY KEY' if col[5] else ''}")
            if col[1] == 'id':
                id_col = col
        
        if not id_col:
            print("❌ Coluna 'id' não encontrada!")
            return False
        
        # Verifica se é PRIMARY KEY
        if not id_col[5]:
            print("❌ Coluna 'id' não é PRIMARY KEY!")
            return False
        
        # Verifica se é INTEGER
        if id_col[2] != 'INTEGER':
            print("❌ Coluna 'id' não é INTEGER!")
            return False
        
        print(f"\n✅ Coluna 'id' configurada corretamente: {id_col[2]} PRIMARY KEY")
        
        # Verifica sqlite_sequence
        print("\n📊 Verificando sqlite_sequence:")
        cursor.execute("SELECT name, seq FROM sqlite_sequence WHERE name='unidades'")
        seq_result = cursor.fetchone()
        
        if seq_result:
            print(f"   Tabela 'unidades' na sqlite_sequence: {seq_result[1]}")
        else:
            print("   Tabela 'unidades' NÃO está na sqlite_sequence")
        
        # Verifica registros na tabela
        cursor.execute("SELECT COUNT(*) FROM unidades")
        total_registros = cursor.fetchone()[0]
        print(f"\n📈 Total de registros na tabela: {total_registros}")
        
        if total_registros > 0:
            cursor.execute("SELECT MIN(id), MAX(id) FROM unidades")
            min_max = cursor.fetchone()
            print(f"   IDs existentes: {min_max[0]} a {min_max[1]}")
            
            # Verifica se há gaps nos IDs
            cursor.execute("""
                WITH RECURSIVE 
                numbers AS (
                    SELECT 1 as id
                    UNION ALL
                    SELECT id + 1 FROM numbers WHERE id < (SELECT MAX(id) FROM unidades)
                )
                SELECT COUNT(*) FROM numbers 
                WHERE id NOT IN (SELECT id FROM unidades)
            """)
            gaps = cursor.fetchone()[0]
            print(f"   Gaps nos IDs: {gaps}")
            
            # Corrige sqlite_sequence se necessário
            if not seq_result and total_registros > 0:
                print("\n🔧 Corrigindo sqlite_sequence...")
                max_id = min_max[1]
                
                # Insere ou atualiza na sqlite_sequence
                cursor.execute("""
                    INSERT OR REPLACE INTO sqlite_sequence (name, seq) 
                    VALUES ('unidades', ?)
                """, (max_id,))
                
                conn.commit()
                print(f"   ✅ sqlite_sequence atualizada: unidades | {max_id}")
                
                # Verifica novamente
                cursor.execute("SELECT name, seq FROM sqlite_sequence WHERE name='unidades'")
                seq_result = cursor.fetchone()
                if seq_result:
                    print(f"   ✅ Confirmado: unidades | {seq_result[1]}")
                else:
                    print("   ❌ Falha ao corrigir sqlite_sequence")
                    return False
            elif seq_result and seq_result[1] < min_max[1]:
                print(f"\n⚠️ sqlite_sequence desatualizada: {seq_result[1]} < {min_max[1]}")
                print("🔧 Atualizando sqlite_sequence...")
                
                cursor.execute("""
                    UPDATE sqlite_sequence 
                    SET seq = ? 
                    WHERE name = 'unidades'
                """, (min_max[1],))
                
                conn.commit()
                print(f"   ✅ sqlite_sequence atualizada: unidades | {min_max[1]}")
        
        # Testa inserção de um registro para verificar AUTOINCREMENT
        print("\n🧪 Testando AUTOINCREMENT...")
        try:
            cursor.execute("""
                INSERT INTO unidades (rede, nome, endereco) 
                VALUES ('TESTE', 'TESTE_AUTOINCREMENT', 'Endereço de teste')
            """)
            
            novo_id = cursor.lastrowid
            print(f"   ✅ Inserção de teste bem-sucedida. Novo ID: {novo_id}")
            
            # Remove o registro de teste
            cursor.execute("DELETE FROM unidades WHERE nome = 'TESTE_AUTOINCREMENT'")
            conn.commit()
            print("   🧹 Registro de teste removido")
            
        except Exception as e:
            print(f"   ❌ Falha no teste de AUTOINCREMENT: {e}")
            return False
        
        # Verifica sqlite_sequence final
        print("\n📊 Estado final da sqlite_sequence:")
        cursor.execute("SELECT name, seq FROM sqlite_sequence WHERE name='unidades'")
        seq_final = cursor.fetchone()
        
        if seq_final:
            print(f"   ✅ unidades | {seq_final[1]}")
        else:
            print("   ❌ Tabela 'unidades' não está na sqlite_sequence")
        
        print("\n🎉 Verificação concluída!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 VERIFICANDO E CORRIGINDO SQLITE_SEQUENCE")
    print("=" * 50)
    
    if verificar_sqlite_sequence():
        print("\n✅ Sistema AUTOINCREMENT funcionando corretamente!")
        print("💡 Agora você pode executar os scrapers sem problemas de 'NULL identity key'")
    else:
        print("\n❌ Problemas encontrados na verificação.")
        print("🔧 Execute o script fix_db.py para corrigir a estrutura da tabela")
        sys.exit(1)
