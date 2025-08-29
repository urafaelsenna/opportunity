#!/usr/bin/env python3
"""
Script para verificar quantas unidades Smartfit temos no banco
"""

import sqlite3
import os

def verificar_contagem_smartfit():
    """Verifica a contagem de unidades Smartfit no banco"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'unidades.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    print("🔍 VERIFICANDO CONTAGEM DE UNIDADES SMARTFIT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total geral
        cursor.execute("SELECT COUNT(*) FROM unidades")
        total_geral = cursor.fetchone()[0]
        
        # Smartfit
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE rede = 'Smartfit'")
        smartfit_count = cursor.fetchone()[0]
        
        # Outras redes
        outras_count = total_geral - smartfit_count
        
        print(f"📊 TOTAL NO BANCO: {total_geral}")
        print(f"   🟦 Smartfit: {smartfit_count}")
        print(f"   🟨 Outras redes: {outras_count}")
        
        print(f"\n🎯 META SMARTFIT: 903 unidades")
        print(f"📉 FALTAM: {903 - smartfit_count} unidades")
        
        # Verifica distribuição por rede
        cursor.execute("SELECT rede, COUNT(*) FROM unidades GROUP BY rede ORDER BY COUNT(*) DESC")
        redes = cursor.fetchall()
        
        print(f"\n📋 DISTRIBUIÇÃO POR REDE:")
        for rede, count in redes:
            print(f"   {rede}: {count} unidades")
        
        # Verifica se há unidades sem nome
        cursor.execute("SELECT COUNT(*) FROM unidades WHERE nome IS NULL OR nome = ''")
        sem_nome = cursor.fetchone()[0]
        if sem_nome > 0:
            print(f"\n⚠️  Unidades sem nome: {sem_nome}")
        
        # Verifica se há nomes duplicados
        cursor.execute("""
            SELECT nome, COUNT(*) 
            FROM unidades 
            GROUP BY nome 
            HAVING COUNT(*) > 1
        """)
        duplicatas = cursor.fetchall()
        if duplicatas:
            print(f"\n⚠️  Nomes duplicados encontrados: {len(duplicatas)}")
            for nome, count in duplicatas[:5]:  # Mostra apenas os primeiros 5
                print(f"   '{nome}': {count} vezes")
        
        return smartfit_count
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    count = verificar_contagem_smartfit()
    
    if count is not None:
        if count >= 903:
            print(f"\n🎉 META ATINGIDA! Temos {count} unidades Smartfit")
        else:
            print(f"\n📊 Status: {count}/903 unidades Smartfit")
            print("💡 Execute o scraper novamente para coletar as unidades faltantes")
            print("   O scraper é incremental e não duplicará unidades existentes")
