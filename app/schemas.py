from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    categoria: Optional[str] = Field(None, max_length=80)
    preco: float = Field(0.0, ge=0, le=100000000)
    custo: float = Field(0.0, ge=0, le=100000000)
    codigo_barras: Optional[str] = Field(None, max_length=64)
    estoque_atual: int = Field(0, ge=0, le=100000000)
    estoque_minimo: int = Field(0, ge=0, le=100000000)


class ProdutoUpdate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    categoria: Optional[str] = Field(None, max_length=80)
    preco: float = Field(..., ge=0, le=100000000)
    custo: float = Field(..., ge=0, le=100000000)
    codigo_barras: Optional[str] = Field(..., max_length=64)
    estoque_minimo: int = Field(..., ge=0, le=100000000)


class ProdutoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    categoria: Optional[str]
    codigo_barras: Optional[str]
    preco: float
    custo: float
    margem: float
    estoque_atual: int
    estoque_minimo: int
    status: str


class MovimentacaoCreate(BaseModel):
    quantidade: int = Field(..., gt=0, le=100000000)
    observacao: Optional[str] = Field(None, max_length=500)


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    username: str = Field(..., min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9._-]+$")
    senha: str = Field(..., min_length=12, max_length=256)
    perfil: str = Field("operador", pattern=r"^(admin|gerente|operador)$")


class UsuarioOut(BaseModel):
    id: int
    nome: str
    username: str
    perfil: str
    ativo: bool


class FilialCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)


class FornecedorCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    documento: Optional[str] = Field(None, max_length=32)
    email: Optional[str] = Field(None, max_length=254)
    telefone: Optional[str] = Field(None, max_length=32)
