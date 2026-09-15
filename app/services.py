from __future__ import annotations

import base64
import hashlib
import json
import secrets
from typing import Any

from sqlalchemy.orm import Session

from app import models, schemas


PERFIS_VALIDOS = {"admin", "gerente", "operador"}


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode("utf-8"), salt=sal, n=2**14, r=8, p=1)
    return "scrypt$" + base64.b64encode(sal).decode("ascii") + "$" + base64.b64encode(chave).decode("ascii")


def verificar_senha(senha: str, password_hash: str) -> bool:
    try:
        algoritmo, sal_b64, chave_b64 = password_hash.split("$", 2)
        if algoritmo != "scrypt":
            return False
        sal = base64.b64decode(sal_b64.encode("ascii"), validate=True)
        esperada = base64.b64decode(chave_b64.encode("ascii"), validate=True)
        atual = hashlib.scrypt(senha.encode("utf-8"), salt=sal, n=2**14, r=8, p=1)
        return secrets.compare_digest(atual, esperada)
    except (ValueError, TypeError):
        return False


def registrar_auditoria(db: Session, empresa_id: int, usuario_id: int | None, acao: str, entidade: str, entidade_id: int | None, detalhes: dict | None = None):
    db.add(models.Auditoria(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhes=json.dumps(detalhes, ensure_ascii=False, separators=(",", ":")) if detalhes else None,
    ))


def produto_to_out(p: models.Produto, incluir_campos_sensiveis: bool = True) -> dict:
    status = "baixo" if p.estoque_atual <= p.estoque_minimo else "ok"
    preco = p.preco or 0
    custo = p.custo or 0
    resposta = {
        "id": p.id,
        "nome": (p.nome or "").strip(),
        "categoria": (p.categoria or "").strip() if p.categoria else None,
        "preco": preco,
        "estoque_atual": p.estoque_atual,
        "estoque_minimo": p.estoque_minimo,
        "status": status,
    }
    if incluir_campos_sensiveis:
        resposta.update({
            "codigo_barras": p.codigo_barras,
            "custo": custo,
            "margem": round(((preco - custo) / preco) * 100, 2) if preco else 0,
        })
    return resposta


def validar_nome_e_categoria(nome: str | None, categoria: str | None = None):
    nome_limpo = (nome or "").strip()
    categoria_limpa = (categoria or "").strip() if categoria is not None else None
    categoria_limpa = categoria_limpa if categoria_limpa else None
    if not nome_limpo:
        raise ValueError("Nome do produto é obrigatório")
    return nome_limpo, categoria_limpa


def listar_produtos_db(db: Session, empresa_id: int):
    return db.query(models.Produto).filter(models.Produto.empresa_id == empresa_id).order_by(models.Produto.nome).all()


def buscar_produto_db(db: Session, empresa_id: int, produto_id: int):
    return db.query(models.Produto).filter(models.Produto.id == produto_id, models.Produto.empresa_id == empresa_id).first()


def listar_movimentacoes_db(db: Session, empresa_id: int):
    return (
        db.query(models.Movimentacao)
        .join(models.Produto)
        .filter(models.Movimentacao.empresa_id == empresa_id)
        .order_by(models.Movimentacao.data.desc())
        .limit(100)
        .all()
    )


def csv_seguro(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    if texto.startswith(("=", "+", "-", "@")):
        return "'" + texto
    return texto
