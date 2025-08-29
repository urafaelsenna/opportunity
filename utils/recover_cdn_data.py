#!/usr/bin/env python3
"""
Script para recuperar dados das colunas CDN que foram perdidos
durante a correção da estrutura da tabela.
"""

import json
import sqlite3
import os
import sys

def verificar_dados_cdn():
    """Verifica os dados CDN disponíveis no JSON e no banco"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades.db')
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades_atualizadas.json')
    
    print("🔍 VERIFICANDO DADOS CDN PERDIDOS")
    print("=" * 50)
    
    # Verifica arquivo JSON
    if not os.path.exists(json_path):
        print(f"❌ Arquivo JSON não encontrado: {json_path}")
        return False
    
    print(f"📄 Verificando arquivo JSON: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ JSON carregado: {len(data)} unidades")
        
        # Verifica dados CDN no JSON
        cdn_count = 0
        for unidade in data:
            if (unidade.get('bairro_cdn') or unidade.get('cidade_cdn') or 
                unidade.get('estado_cdn') or unidade.get('pais_cdn')):
                cdn_count += 1
        
        print(f"📊 Unidades com dados CDN no JSON: {cdn_count}")
        
        if cdn_count == 0:
            print("❌ Nenhum dado CDN encontrado no JSON!")
            return False
        
        # Mostra exemplo
        sample = next((u for u in data if u.get('bairro_cdn') or u.get('cidade_cdn')), None)
        if sample:
            print(f"\n📋 Exemplo de unidade com dados CDN:")
            print(f"   Nome: {sample.get('nome', 'N/A')}")
            print(f"   bairro_cdn: {sample.get('bairro_cdn', 'N/A')}")
            print(f"   cidade_cdn: {sample.get('cidade_cdn', 'N/A')}")
            print(f"   estado_cdn: {sample.get('estado_cdn', 'N/A')}")
            print(f"   pais_cdn: {sample.get('pais_cdn', 'N/A')}")
        
        return True, data
        
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        return False, None

def recuperar_dados_cdn(data):
    """Recupera os dados CDN do JSON para o banco"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades.db')
    
    print(f"\n🔄 RECUPERANDO DADOS CDN PARA O BANCO")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica estrutura atual
        cursor.execute("PRAGMA table_info(unidades)")
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]
        
        print("📋 Colunas disponíveis na tabela:")
        for col in colunas:
            print(f"   {col[1]} {col[2]}")
        
        # Verifica se as colunas CDN existem
        cdn_colunas = ["bairro(cdn)", "cidade(cdn)", "estado(cdn)", "pais(cdn)"]
        for col in cdn_colunas:
            if col not in colunas_nomes:
                print(f"❌ Coluna '{col}' não encontrada na tabela!")
                return False
        
        # Conta unidades no banco
        cursor.execute("SELECT COUNT(*) FROM unidades")
        total_banco = cursor.fetchone()[0]
        print(f"\n📊 Total de unidades no banco: {total_banco}")
        
        # Atualiza dados CDN
        atualizadas = 0
        for unidade in data:
            nome = unidade.get('nome')
            if not nome:
                continue
            
            # Busca a unidade no banco pelo nome
            cursor.execute("SELECT id FROM unidades WHERE nome = ?", (nome,))
            result = cursor.fetchone()
            
            if result:
                unidade_id = result[0]
                
                # Atualiza as colunas CDN
                cursor.execute("""
                    UPDATE unidades 
                    SET "bairro(cdn)" = ?, "cidade(cdn)" = ?, "estado(cdn)" = ?, "pais(cdn)" = ?
                    WHERE id = ?
                """, (
                    unidade.get('bairro_cdn', ''),
                    unidade.get('cidade_cdn', ''),
                    unidade.get('estado_cdn', ''),
                    unidade.get('pais_cdn', ''),
                    unidade_id
                ))
                
                atualizadas += 1
                
                if atualizadas % 100 == 0:
                    print(f"   ✅ {atualizadas} unidades atualizadas...")
        
        conn.commit()
        print(f"\n✅ Total de unidades atualizadas com dados CDN: {atualizadas}")
        
        # Verifica resultado
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE \"bairro(cdn)\" IS NOT NULL AND \"bairro(cdn)\" != \"\"")
        bairro_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE \"cidade(cdn)\" IS NOT NULL AND \"cidade(cdn)\" != \"\"")
        cidade_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE \"estado(cdn)\" IS NOT NULL AND \"estado(cdn)\" != \"\"")
        estado_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE \"pais(cdn)\" IS NOT NULL AND \"pais(cdn)\" != \"\"")
        pais_count = cursor.fetchone()[0]
        
        print(f"\n📊 Dados CDN recuperados:")
        print(f"   bairro_cdn: {bairro_count} unidades")
        print(f"   cidade_cdn: {cidade_count} unidades")
        print(f"   estado_cdn: {estado_count} unidades")
        print(f"   pais_cdn: {pais_count} unidades")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recuperar dados CDN: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Função principal"""
    
    # Verifica dados disponíveis
    sucesso, data = verificar_dados_cdn()
    if not sucesso:
        print("\n❌ Não foi possível verificar os dados CDN")
        return
    
    # Pergunta se deve recuperar
    print(f"\n❓ Deseja recuperar os dados CDN para o banco? (s/n): ", end="")
    resposta = input().lower().strip()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Recupera dados
    if recuperar_dados_cdn(data):
        print("\n🎉 Dados CDN recuperados com sucesso!")
        print("💡 O banco agora contém todas as informações CDN originais")
    else:
        print("\n❌ Falha ao recuperar dados CDN")
        print("🔧 Verifique os erros acima e tente novamente")

if __name__ == "__main__":
    main()
