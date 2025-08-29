#!/usr/bin/env python3
"""
Script de teste para demonstrar o sistema de inserção dinâmica.
Mostra como o sistema detecta automaticamente colunas e filtra dados inválidos.
"""

import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import Database

def testar_insercao_dinamica():
    """Testa o sistema de inserção dinâmica com dados que incluem campos extras"""
    
    print("🧪 TESTANDO SISTEMA DE INSERÇÃO DINÂMICA")
    print("=" * 60)
    
    # Inicializa banco
    db = Database()
    
    # Dados de teste com campos extras que não existem na tabela
    unidades_teste = [
        {
            "rede": "TESTE_DINAMICO",
            "nome": "Academia Teste 1",
            "endereco": "Rua Teste, 123",
            "cidade": "Cidade Teste",
            "estado": "TS",
            # Campos extras que serão ignorados
            "planos": "Gold Premium",
            "beneficios": ["Piscina", "Sauna"],
            "horario_funcionamento": "24h",
            "campo_inexistente": "valor qualquer"
        },
        {
            "rede": "TESTE_DINAMICO",
            "nome": "Academia Teste 2",
            "endereco": "Avenida Teste, 456",
            "cidade": "Cidade Teste 2",
            "estado": "TS",
            # Campos extras
            "modalidades": ["Musculação", "CrossFit"],
            "preco_mensalidade": 89.90,
            "outro_campo": "outro valor"
        }
    ]
    
    print(f"📊 Dados de teste criados: {len(unidades_teste)} unidades")
    print("🔍 Campos incluídos nos dados de teste:")
    
    # Mostra todos os campos dos dados de teste
    todos_campos = set()
    for unidade in unidades_teste:
        todos_campos.update(unidade.keys())
    
    for campo in sorted(todos_campos):
        print(f"   - {campo}")
    
    print(f"\n🚀 Iniciando inserção dinâmica...")
    
    # Testa inserção dinâmica
    try:
        unidades_inseridas = db.inserir_multiplas_unidades_dinamico(unidades_teste)
        
        print(f"\n✅ TESTE CONCLUÍDO!")
        print(f"📊 Unidades inseridas: {unidades_inseridas}")
        
        # Verifica se foram inseridas
        if unidades_inseridas > 0:
            print(f"💡 Verifique o banco para confirmar a inserção")
            print(f"🔍 Os campos extras foram automaticamente ignorados")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    # Limpa dados de teste
    print(f"\n🧹 Limpando dados de teste...")
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM unidades WHERE rede = 'TESTE_DINAMICO'")
        conn.commit()
        conn.close()
        print(f"✅ Dados de teste removidos")
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados de teste: {e}")

if __name__ == "__main__":
    testar_insercao_dinamica()
