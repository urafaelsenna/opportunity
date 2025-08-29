#!/usr/bin/env python3
"""
Script para verificar se o CSV tem dados CDN
"""

import pandas as pd
import os

def verificar_csv_cdn():
    """Verifica se o CSV tem dados CDN"""
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exportados', 'unidades.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV não encontrado: {csv_path}")
        return False
    
    print(f"📄 Verificando CSV: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ CSV carregado: {len(df)} linhas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Verifica se tem colunas CDN
        cdn_colunas = ['bairro(cdn)', 'cidade(cdn)', 'estado(cdn)', 'pais(cdn)']
        cdn_existem = [col for col in cdn_colunas if col in df.columns]
        
        if not cdn_existem:
            print("❌ Nenhuma coluna CDN encontrada no CSV!")
            return False
        
        print(f"✅ Colunas CDN encontradas: {cdn_existem}")
        
        # Conta dados não vazios
        for col in cdn_existem:
            nao_vazios = df[col].notna().sum()
            print(f"   {col}: {nao_vazios} valores não vazios")
        
        # Mostra exemplo
        for col in cdn_existem:
            if df[col].notna().sum() > 0:
                exemplo = df[df[col].notna()].iloc[0]
                print(f"\n📋 Exemplo com {col}:")
                print(f"   Nome: {exemplo.get('nome', 'N/A')}")
                print(f"   {col}: {exemplo.get(col, 'N/A')}")
                break
        
        return True, df
        
    except Exception as e:
        print(f"❌ Erro ao carregar CSV: {e}")
        return False, None

if __name__ == "__main__":
    print("🔍 VERIFICANDO CSV PARA DADOS CDN")
    print("=" * 50)
    
    sucesso, df = verificar_csv_cdn()
    if sucesso:
        print("\n✅ CSV contém dados CDN!")
        print("💡 Podemos usar esses dados para recuperar o banco")
    else:
        print("\n❌ CSV não contém dados CDN")
        print("🔍 Verificando outras fontes...")
