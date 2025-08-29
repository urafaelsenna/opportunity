from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .models import Base, Unidade
import json
from datetime import datetime

class Database:
    def __init__(self, db_url="sqlite:///unidades.db"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas se não existirem"""
        Base.metadata.create_all(self.engine)
    
    def buscar_nomes_existentes(self):
        """Retorna um set com todos os nomes de unidades já cadastradas"""
        session = self.Session()
        try:
            unidades = session.query(Unidade.nome).all()
            return {nome[0] for nome in unidades}
        finally:
            session.close()
    
    def inserir_unidade(self, unidade_data):
        """Insere uma única unidade no banco"""
        session = self.Session()
        try:
            unidade = Unidade(**unidade_data)
            session.add(unidade)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()
    
    def inserir_multiplas_unidades(self, unidades_data, batch_size=100):
        """
        Insere múltiplas unidades de uma vez usando inserção em blocos
        para evitar problemas com muitos registros simultâneos
        """
        if not unidades_data:
            return 0
        
        total_inseridas = 0
        session = self.Session()
        
        try:
            for i in range(0, len(unidades_data), batch_size):
                batch = unidades_data[i:i + batch_size]
                print(f"    📦 Processando bloco {i//batch_size + 1}/{(len(unidades_data) + batch_size - 1)//batch_size} ({len(batch)} unidades)")
                
                try:
                    unidades_batch = [Unidade(**data) for data in batch]
                    session.add_all(unidades_batch)
                    session.commit()
                    total_inseridas += len(batch)
                    print(f"    ✅ Bloco {i//batch_size + 1} inserido com sucesso")
                    
                except IntegrityError as e:
                    session.rollback()
                    print(f"    ❌ Erro no bloco {i//batch_size + 1}: {e}")
                    for j, data in enumerate(batch):
                        try:
                            unidade = Unidade(**data)
                            session.add(unidade)
                            session.commit()
                            total_inseridas += 1
                        except IntegrityError as e2:
                            session.rollback()
                            print(f"       ❌ Falha na unidade {data.get('nome', 'N/A')}: {e2}")
                        except Exception as e2:
                            session.rollback()
                            print(f"       ❌ Erro inesperado na unidade {data.get('nome', 'N/A')}: {e2}")
                
                except Exception as e:
                    session.rollback()
                    print(f"    ❌ Erro geral no bloco {i//batch_size + 1}: {e}")
                    for j, data in enumerate(batch):
                        try:
                            unidade = Unidade(**data)
                            session.add(unidade)
                            session.commit()
                            total_inseridas += 1
                        except Exception as e2:
                            session.rollback()
                            print(f"       ❌ Falha na unidade {data.get('nome', 'N/A')}: {e2}")
        
        finally:
            session.close()
        
        return total_inseridas
    
    def inserir_multiplas_unidades_dinamico(self, unidades_data, batch_size=100):
        """
        Insere múltiplas unidades de forma dinâmica e segura.
        Detecta automaticamente as colunas da tabela e filtra dados inválidos.
        """
        if not unidades_data:
            return 0
        
        session = self.Session()
        
        try:
            cursor = session.execute(text("PRAGMA table_info(unidades)"))
            colunas_existentes = [row[1] for row in cursor.fetchall()]
            
            print(f"🔍 Colunas detectadas na tabela: {len(colunas_existentes)}")
            print(f"   {', '.join(colunas_existentes)}")
            
            campos_ignorados_totais = set()
            total_inseridas = 0
            
            for i in range(0, len(unidades_data), batch_size):
                batch = unidades_data[i:i + batch_size]
                print(f"\n📦 Processando bloco {i//batch_size + 1}/{(len(unidades_data) + batch_size - 1)//batch_size} ({len(batch)} unidades)")
                
                try:
                    unidades_batch = []
                    
                    for unidade_data in batch:
                        dados_filtrados = {k: v for k, v in unidade_data.items() if k in colunas_existentes}
                        campos_ignorados = set(unidade_data.keys()) - set(dados_filtrados.keys())
                        campos_ignorados_totais.update(campos_ignorados)
                        
                        if not dados_filtrados.get('nome'):
                            print(f"   ⚠️ Unidade sem nome ignorada")
                            continue
                        
                        unidade = Unidade(**dados_filtrados)
                        unidades_batch.append(unidade)
                    
                    if unidades_batch:
                        session.add_all(unidades_batch)
                        session.commit()
                        total_inseridas += len(unidades_batch)
                        print(f"   ✅ Bloco {i//batch_size + 1} inserido com sucesso ({len(unidades_batch)} unidades)")
                    else:
                        print(f"   ⚠️ Bloco {i//batch_size + 1} sem unidades válidas")
                        
                except IntegrityError as e:
                    session.rollback()
                    print(f"   ❌ Erro no bloco {i//batch_size + 1}: {e}")
                    for unidade_data in batch:
                        try:
                            dados_filtrados = {k: v for k, v in unidade_data.items() if k in colunas_existentes}
                            if dados_filtrados.get('nome'):
                                unidade = Unidade(**dados_filtrados)
                                session.add(unidade)
                                session.commit()
                                total_inseridas += 1
                        except IntegrityError as e2:
                            session.rollback()
                            print(f"      ❌ Falha na unidade {unidade_data.get('nome', 'N/A')}: {e2}")
                        except Exception as e2:
                            session.rollback()
                            print(f"      ❌ Erro inesperado na unidade {unidade_data.get('nome', 'N/A')}: {e2}")
                
                except Exception as e:
                    session.rollback()
                    print(f"   ❌ Erro geral no bloco {i//batch_size + 1}: {e}")
                    for unidade_data in batch:
                        try:
                            dados_filtrados = {k: v for k, v in unidade_data.items() if k in colunas_existentes}
                            if dados_filtrados.get('nome'):
                                unidade = Unidade(**dados_filtrados)
                                session.add(unidade)
                                session.commit()
                                total_inseridas += 1
                        except Exception as e2:
                            session.rollback()
                            print(f"      ❌ Falha na unidade {unidade_data.get('nome', 'N/A')}: {e2}")
            
            if campos_ignorados_totais:
                print(f"\n⚠️ CAMPOS IGNORADOS (não existem na tabela):")
                for campo in sorted(campos_ignorados_totais):
                    print(f"   - {campo}")
                print(f"\n💡 Dica: Considere adicionar esses campos à tabela se forem importantes")
            
            return total_inseridas
            
        finally:
            session.close()
    
    def buscar_todas_unidades(self):
        session = self.Session()
        try:
            return session.query(Unidade).all()
        finally:
            session.close()
    
    def buscar_unidades_por_rede(self, rede):
        session = self.Session()
        try:
            return session.query(Unidade).filter(Unidade.rede == rede).all()
        finally:
            session.close()
    
    def buscar_unidades_por_cidade(self, cidade):
        session = self.Session()
        try:
            return session.query(Unidade).filter(Unidade.cidade == cidade).all()
        finally:
            session.close()
    
    def buscar_unidades_por_estado(self, estado):
        session = self.Session()
        try:
            return session.query(Unidade).filter(Unidade.estado == estado).all()
        finally:
            session.close()
    
    def buscar_unidades_sem_coordenadas(self):
        session = self.Session()
        try:
            return session.query(Unidade).filter(
                (Unidade.latitude.is_(None)) | 
                (Unidade.latitude == '') |
                (Unidade.longitude.is_(None)) | 
                (Unidade.longitude == '')
            ).all()
        finally:
            session.close()
    
    def atualizar_coordenadas(self, unidade_id, latitude, longitude):
        session = self.Session()
        try:
            unidade = session.query(Unidade).filter_by(id=unidade_id).first()
            if unidade:
                unidade.latitude = str(latitude)
                unidade.longitude = str(longitude)
                unidade.data_atualizacao = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def atualizar_endereco_detalhado(self, unidade_id, cidade, estado, cep):
        session = self.Session()
        try:
            unidade = session.query(Unidade).filter_by(id=unidade_id).first()
            if unidade:
                unidade.cidade = cidade
                unidade.estado = estado
                unidade.cep = cep
                unidade.data_atualizacao = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def estatisticas(self):
        session = self.Session()
        try:
            total_unidades = session.query(Unidade).count()
            redes = session.query(Unidade.rede).distinct().all()
            redes = [rede[0] for rede in redes]
            ultima = session.query(Unidade.data_atualizacao).order_by(Unidade.data_atualizacao.desc()).first()
            ultima_atualizacao = ultima[0] if ultima else None
            return {
                'total_unidades': total_unidades,
                'redes': redes,
                'ultima_atualizacao': ultima_atualizacao
            }
        finally:
            session.close()
    
    def gerar_json(self, nome_arquivo):
        unidades = self.buscar_todas_unidades()
        dados = [unidade.to_dict() for unidade in unidades]
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        print(f"📄 JSON gerado: {nome_arquivo} ({len(dados)} unidades)")
    
    def limpar_duplicatas(self):
        session = self.Session()
        try:
            duplicatas = session.query(Unidade.nome).group_by(Unidade.nome).having(
                text('COUNT(*) > 1')
            ).all()
            total_removidas = 0
            for (nome,) in duplicatas:
                unidades = session.query(Unidade).filter_by(nome=nome).order_by(Unidade.id).all()
                for unidade in unidades[1:]:
                    session.delete(unidade)
                    total_removidas += 1
            session.commit()
            return total_removidas
        finally:
            session.close()

    # ============================================================
    # 🔍 Métodos utilitários dinâmicos
    # ============================================================
    def obter_colunas_tabela(self, tabela="unidades"):
        """Retorna todas as colunas da tabela informada"""
        session = self.Session()
        try:
            resultado = session.execute(text(f"PRAGMA table_info({tabela})"))
            return [row[1] for row in resultado.fetchall()]
        finally:
            session.close()

    def adicionar_coluna(self, tabela, coluna, tipo="TEXT"):
        """Adiciona dinamicamente uma coluna na tabela se não existir"""
        session = self.Session()
        try:
            colunas = self.obter_colunas_tabela(tabela)
            if coluna not in colunas:
                print(f"⚡ Adicionando coluna '{coluna}' na tabela '{tabela}'...")
                session.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}"))
                session.commit()
        finally:
            session.close()
