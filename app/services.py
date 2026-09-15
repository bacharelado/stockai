from __future__ import annotations

import base64
import hashlib
import json
import secrets
from typing import Any

from sqlalchemy.orm import Session

from app import models, schemas


PERFIS_VALIDOS = {"admin", "gerente", "operador"}
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1

# Used when a username does not exist. It must be a fixed valid hash so the
# nonexistent-user path performs the same expensive KDF as a real user.
DUMMY_PASSWORD_HASH = "scrypt$Xypti5weSnPR8LbC6KSXMQ==$l6L/RtSxgSmuSytu+uKHyDTF7ouEhry85IlQkMjZaGjgpIpU2Ccyb97Adt58oIL6N2ounDYGMWo6/ZfBT2NVqw=="


def gerar_hash_senha(senha: str) -> str:
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode("utf-8"), salt=sal, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
    return "scrypt$" + base64.b64encode(sal).decode("ascii") + "$" + base64.b64encode(chave).decode("ascii")


def verificar_senha(senha: str, password_hash: str) -> bool:
    try:
        algoritmo, sal_b64, chave_b64 = password_hash.split("$", 2)
        if algoritmo != "scrypt":
            return False
        sal = base64.b64decode(sal_b64.encode("ascii"), validate=True)
        esperada = base64.b64decode(chave_b64.encode("ascii"), validate=True)
        atual = hashlib.scrypt(senha.encode("utf-8"), salt=sal, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
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


def produto_to_out(p: models.Produto) -> dict:
    status = "baixo" if p.estoque_atual <= p.estoque_minimo else "ok"
    preco = p.preco or 0
    custo = p.custo or 0
    return {
        "id": p.id,
        "nome": (p.nome or "").strip(),
        "categoria": (p.categoria or "").strip() if p.categoria else None,
        "codigo_barras": p.codigo_barras,
        "preco": preco,
        "custo": custo,
        "margem": round(((preco - custo) / preco) * 100, 2) if preco else 0,
        "estoque_atual": p.estoque_atual,
        "estoque_minimo": p.estoque_minimo,
        "status": status,
    }


def validar_nome_e_categoria(nome: str | None, categoria: str | None = None):
    nome_limpo = (nome or "").strip()
    categoria_limpa = (categoria or "").strip() if categoria is not None else None
    categoria_limpa = categoria_limpa if categoria_limpa else None
    if not nome_limpo:
        raise ValueError("Nome do produto é obrigatório")
    return nome_limpo, categoria_limpa


def _produtos_base_query(db: Session, empresa_id: int):
    return db.query(models.Produto).filter(
        models.Produto.empresa_id == empresa_id,
        models.Produto.ativo.is_(True),
    )


def listar_produtos_db(db: Session, empresa_id: int, limit: int | None = None, offset: int = 0):
    query = _produtos_base_query(db, empresa_id).order_by(models.Produto.nome)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    return query.all()


def contar_produtos_db(db: Session, empresa_id: int) -> int:
    return _produtos_base_query(db, empresa_id).count()


def listar_produtos_paginado_db(
    db: Session,
    empresa_id: int,
    *,
    page: int,
    page_size: int,
    busca: str | None = None,
    status: str = "todos",
    categoria: str | None = None,
    ordenar_por: str = "nome",
    ordem: str = "asc",
):
    query = _produtos_base_query(db, empresa_id)
    if busca:
        termo = f"%{busca.strip()}%"
        query = query.filter(
            models.Produto.nome.ilike(termo) |
            models.Produto.categoria.ilike(termo)
        )
    if categoria:
        query = query.filter(models.Produto.categoria == categoria)
    if status == "baixo":
        query = query.filter(models.Produto.estoque_atual <= models.Produto.estoque_minimo)
    elif status == "ok":
        query = query.filter(models.Produto.estoque_atual > models.Produto.estoque_minimo)

    campos = {
        "nome": models.Produto.nome,
        "preco": models.Produto.preco,
        "estoque_atual": models.Produto.estoque_atual,
    }
    coluna = campos.get(ordenar_por, models.Produto.nome)
    query = query.order_by(coluna.desc() if ordem == "desc" else coluna.asc(), models.Produto.id.asc())

    total = query.count()
    produtos = query.offset((page - 1) * page_size).limit(page_size).all()
    return produtos, total


def listar_movimentacoes_db(db: Session, empresa_id: int, limit: int = 100, offset: int = 0):
    return (
        db.query(models.Movimentacao)
        .join(models.Produto)
        .filter(
            models.Movimentacao.empresa_id == empresa_id,
            models.Produto.empresa_id == empresa_id,
        )
        .order_by(models.Movimentacao.data.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def csv_seguro(valor: Any) -> str:
    texto = "" if valor is None else str(valor)
    if texto.startswith(("=", "+", "-", "@")):
        return "'" + texto
    return texto
