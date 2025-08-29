import sqlite3
import pandas as pd
import os

def exportar_tabela_para_csv(banco_dados, nome_tabela, pasta_saida="."):
    # Conecta ao banco
    con = sqlite3.connect(banco_dados)

    # Verifica se a tabela existe
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
    
    if not cursor.fetchone():
        print(f"⚠️ Tabela '{nome_tabela}' não encontrada no banco de dados.")
        con.close()
        return

    # Cria a pasta de saída, se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Exporta a tabela específica
    df = pd.read_sql_query(f"SELECT * FROM {nome_tabela};", con)
    caminho_arquivo = os.path.join(pasta_saida, f"{nome_tabela}.csv")
    df.to_csv(caminho_arquivo, index=False, encoding="utf-8-sig")
    print(f"✅ Tabela '{nome_tabela}' exportada para: {caminho_arquivo}")
    print(f"📊 Total de registros: {len(df)}")

    con.close()
    print(f"\n🎉 Exportação da tabela '{nome_tabela}' concluída com sucesso!")

def exportar_sqlite_para_csv(banco_dados, pasta_saida="."):
    # Conecta ao banco
    con = sqlite3.connect(banco_dados)

    # Descobre todas as tabelas do banco
    tabelas = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", con)

    if tabelas.empty:
        print("⚠️ Nenhuma tabela encontrada no banco de dados.")
        return

    # Cria a pasta de saída, se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Exporta cada tabela
    for tabela in tabelas['name']:
        df = pd.read_sql_query(f"SELECT * FROM {tabela};", con)
        caminho_arquivo = os.path.join(pasta_saida, f"{tabela}.csv")
        df.to_csv(caminho_arquivo, index=False, encoding="utf-8-sig")
        print(f"✅ Tabela '{tabela}' exportada para: {caminho_arquivo}")

    con.close()
    print("\n🎉 Exportação concluída com sucesso!")

if __name__ == "__main__":
    # Caminho para seu banco de dados
    banco = "./unidades.db"
    # Pasta onde os CSVs serão salvos
    pasta = "./exportados"
    # Nome da tabela a ser exportada
    tabela = "unidades"

    exportar_tabela_para_csv(banco, tabela, pasta)
