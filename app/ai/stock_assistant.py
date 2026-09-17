"""Orquestração do assistente de estoque com os dados do tenant atual."""

from sqlalchemy.orm import Session

from app.ai.client import AIClient
from app.ai.prompts import INSTRUCOES_ASSISTENTE_ESTOQUE, montar_contexto_estoque
from app.services import listar_movimentacoes_db, listar_produtos_db, produto_to_out


def construir_contexto(db: Session, empresa_id: int) -> str:
    produtos = [produto_to_out(item) for item in listar_produtos_db(db, empresa_id)]
    movimentacoes = [
        {
            "id": item.id,
            "produto_id": item.produto_id,
            "produto": item.produto.nome,
            "tipo": item.tipo,
            "quantidade": item.quantidade,
            "data": item.data.isoformat() if item.data else None,
        }
        for item in listar_movimentacoes_db(db, empresa_id)
    ]
    return montar_contexto_estoque(produtos, movimentacoes)


def perguntar(db: Session, empresa_id: int, pergunta: str) -> str:
    contexto = construir_contexto(db, empresa_id)
    entrada = f"{contexto}\nPERGUNTA DO USUÁRIO:\n{pergunta.strip()}"
    return AIClient().gerar_resposta(
        instrucoes=INSTRUCOES_ASSISTENTE_ESTOQUE,
        entrada=entrada,
    )
