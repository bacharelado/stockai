from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


def agora_utc():
    return datetime.now(timezone.utc)


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    documento = Column(String(32), unique=True, nullable=True)
    ativa = Column(Boolean, nullable=False, default=True)
    plano = Column(String(24), nullable=False, default="gratuito")
    status_assinatura = Column(String(24), nullable=False, default="ativa")
    criada_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    usuarios = relationship("Usuario", back_populates="empresa")
    produtos = relationship("Produto", back_populates="empresa")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    username = Column(String(80), nullable=False, unique=True, index=True)
    email = Column(String(254), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    perfil = Column(String(24), nullable=False, default="operador")
    ativo = Column(Boolean, nullable=False, default=True)
    plataforma_admin = Column(Boolean, nullable=False, default=False)
    session_version = Column(Integer, nullable=False, default=1)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc, onupdate=agora_utc)

    empresa = relationship("Empresa", back_populates="usuarios")
    movimentacoes = relationship("Movimentacao", back_populates="usuario")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="usuario", cascade="all, delete-orphan")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    usuario = relationship("Usuario", back_populates="password_reset_tokens")


class Filial(Base):
    __tablename__ = "filiais"
    __table_args__ = (UniqueConstraint("empresa_id", "nome", name="uq_filial_empresa_nome"),)

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    ativa = Column(Boolean, nullable=False, default=True)
    criada_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)


class Fornecedor(Base):
    __tablename__ = "fornecedores"
    __table_args__ = (UniqueConstraint("empresa_id", "documento", name="uq_fornecedor_empresa_documento"),)

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    documento = Column(String(32), nullable=True)
    email = Column(String(254), nullable=True)
    telefone = Column(String(32), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (UniqueConstraint("empresa_id", "codigo_barras", name="uq_produto_empresa_codigo_barras"),)

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    categoria = Column(String(80), nullable=True)
    codigo_barras = Column(String(64), nullable=True)
    preco = Column(Float, nullable=False, default=0.0)
    custo = Column(Float, nullable=False, default=0.0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    empresa = relationship("Empresa", back_populates="produtos")
    movimentacoes = relationship("Movimentacao", back_populates="produto")


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    tipo = Column(String(24), nullable=False)
    quantidade = Column(Integer, nullable=False)
    observacao = Column(String(500), nullable=True)
    data = Column(DateTime(timezone=True), nullable=False, default=agora_utc)

    produto = relationship("Produto", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")


class Auditoria(Base):
    __tablename__ = "auditorias"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    acao = Column(String(80), nullable=False)
    entidade = Column(String(80), nullable=False)
    entidade_id = Column(Integer, nullable=True)
    detalhes = Column(Text, nullable=True)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=agora_utc)
