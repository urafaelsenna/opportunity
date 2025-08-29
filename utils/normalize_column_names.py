#!/usr/bin/env python3
"""
Script para normalizar os nomes das colunas do banco de dados.
Remove parênteses e caracteres especiais para evitar conflitos.
"""

import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import Database
from sqlalchemy import text

def normalizar_nomes_colunas():
    """Normaliza os nomes das colunas removendo parênteses e caracteres especiais"""
    
    print("🔧 NORMALIZANDO NOMES DAS COLUNAS")
    print("=" * 60)
    
    db = Database()
    session = db.Session()
    
    try:
        # Mapeamento de nomes antigos para novos
        mapeamento_colunas = {
            "bairro(cdn)": "bairro_cdn",
            "cidade(cdn)": "cidade_cdn", 
            "estado(cdn)": "estado_cdn",
            "pais(cdn)": "pais_cdn"
        }
        
        # Verifica colunas existentes
        cursor = session.execute(text("PRAGMA table_info(unidades)"))
        colunas_existentes = [row[1] for row in cursor.fetchall()]
        
        print(f"🔍 Colunas existentes: {len(colunas_existentes)}")
        print(f"   {', '.join(colunas_existentes)}")
        
        # Identifica colunas que precisam ser renomeadas
        colunas_para_renomear = []
        for nome_antigo, nome_novo in mapeamento_colunas.items():
            if nome_antigo in colunas_existentes and nome_novo not in colunas_existentes:
                colunas_para_renomear.append((nome_antigo, nome_novo))
        
        if not colunas_para_renomear:
            print(f"\n✅ Todas as colunas já estão normalizadas!")
            return True
        
        print(f"\n⚡ COLUNAS PARA NORMALIZAR: {len(colunas_para_renomear)}")
        
        # Renomeia as colunas uma por uma
        for nome_antigo, nome_novo in colunas_para_renomear:
            try:
                print(f"🔄 Renomeando: '{nome_antigo}' → '{nome_novo}'")
                
                # SQLite não suporta RENAME COLUMN diretamente, então criamos uma nova tabela
                # Primeiro, cria tabela temporária com estrutura correta
                cursor = session.execute(text("PRAGMA table_info(unidades)"))
                colunas_info = cursor.fetchall()
                
                # Constrói CREATE TABLE com nomes normalizados
                create_sql = "CREATE TABLE unidades_temp ("
                colunas_create = []
                
                for col_info in colunas_info:
                    nome_col = col_info[1]
                    tipo_col = col_info[2]
                    not_null = "NOT NULL" if col_info[3] else ""
                    default_val = f"DEFAULT {col_info[4]}" if col_info[4] else ""
                    pk = "PRIMARY KEY" if col_info[5] else ""
                    
                    # Aplica mapeamento se necessário
                    if nome_col in mapeamento_colunas:
                        nome_col = mapeamento_colunas[nome_col]
                    
                    col_def = f"{nome_col} {tipo_col} {not_null} {default_val} {pk}".strip()
                    colunas_create.append(col_def)
                
                create_sql += ", ".join(colunas_create) + ")"
                
                # Cria tabela temporária
                session.execute(text("DROP TABLE IF EXISTS unidades_temp"))
                session.execute(text(create_sql))
                
                # Copia dados com nomes normalizados
                colunas_originais = [col[1] for col in colunas_info]
                colunas_destino = []
                
                for col in colunas_originais:
                    if col in mapeamento_colunas:
                        colunas_destino.append(mapeamento_colunas[col])
                    else:
                        colunas_destino.append(col)
                
                # Constrói INSERT com nomes corretos
                colunas_str = ", ".join([f'"{col}"' for col in colunas_destino])
                colunas_orig_str = ", ".join([f'"{col}"' for col in colunas_originais])
                
                insert_sql = f"INSERT INTO unidades_temp ({colunas_str}) SELECT {colunas_orig_str} FROM unidades"
                session.execute(text(insert_sql))
                
                # Remove tabela antiga e renomeia a nova
                session.execute(text("DROP TABLE unidades"))
                session.execute(text("ALTER TABLE unidades_temp RENAME TO unidades"))
                
                print(f"   ✅ Coluna renomeada com sucesso!")
                
            except Exception as e:
                print(f"   ❌ Erro ao renomear coluna '{nome_antigo}': {e}")
                session.rollback()
                return False
        
        # Commit das alterações
        session.commit()
        print(f"\n✅ Normalização concluída! {len(colunas_para_renomear)} colunas renomeadas")
        
        # Verifica colunas finais
        cursor = session.execute(text("PRAGMA table_info(unidades)"))
        colunas_finais = [row[1] for row in cursor.fetchall()]
        
        print(f"\n🔍 Colunas finais: {len(colunas_finais)}")
        print(f"   {', '.join(colunas_finais)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante normalização: {e}")
        session.rollback()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    sucesso = normalizar_nomes_colunas()
    if sucesso:
        print("\n🎉 NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("💡 Agora os scrapers funcionarão perfeitamente!")
    else:
        print("\n❌ NORMALIZAÇÃO FALHOU!")
