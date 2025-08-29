from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Unidade(Base):
    __tablename__ = 'unidades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rede = Column(String(100), nullable=False, index=True)
    nome = Column(String(200), nullable=False, unique=True, index=True)
    endereco = Column(Text, nullable=False)
    
    # Colunas para endereço detalhado
    cidade = Column(String(100), nullable=True, index=True)
    estado = Column(String(50), nullable=True, index=True)
    cep = Column(String(20), nullable=True)
    
    # Colunas para contato e localização
    telefone = Column(String(50), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Colunas para informações adicionais
    horarios = Column(JSON, nullable=True)  # Dicionário de horários
    servicos = Column(JSON, nullable=True)  # Lista de serviços
    link_matricula = Column(String(500), nullable=True)
    
    # Timestamps
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Colunas CDN (nomes normalizados)
    bairro_cdn = Column(String(100), nullable=True)
    cidade_cdn = Column(String(100), nullable=True)
    estado_cdn = Column(String(50), nullable=True)
    pais_cdn = Column(String(50), nullable=True)
    
    # Novas colunas para dados específicos de academias
    planos = Column(JSON, nullable=True)  # Para planos de preços
    beneficios = Column(JSON, nullable=True)  # Para benefícios oferecidos
    modalidades = Column(JSON, nullable=True)  # Para modalidades oferecidas
    horario_funcionamento = Column(String(200), nullable=True)  # Para horários específicos
    preco_mensalidade = Column(Float, nullable=True)  # Para preços
    
    # Colunas para campos dinâmicos (adicionadas automaticamente pelo sistema)
    campo_inexistente = Column(String(500), nullable=True)  # Campo de teste
    outro_campo = Column(String(500), nullable=True)  # Outro campo de teste
    
    def __repr__(self):
        return f"<Unidade(rede='{self.rede}', nome='{self.nome}', endereco='{self.endereco}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'rede': self.rede,
            'nome': self.nome,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'telefone': self.telefone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'horarios': self.horarios,
            'servicos': self.servicos,
            'link_matricula': self.link_matricula,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'bairro_cdn': self.bairro_cdn,
            'cidade_cdn': self.cidade_cdn,
            'estado_cdn': self.estado_cdn,
            'pais_cdn': self.pais_cdn
        }
