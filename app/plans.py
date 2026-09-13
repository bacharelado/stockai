"""Regras de planos do StockAI.

A cobrança ainda não é feita aqui. Este módulo centraliza limites e textos para
que a aplicação possa evoluir para assinatura sem espalhar regras pelo código.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Plano:
    codigo: str
    nome: str
    preco_mensal: int | None
    max_produtos: int | None
    max_usuarios: int | None
    descricao: str
    destaque: bool = False


PLANOS: dict[str, Plano] = {
    "gratuito": Plano(
        codigo="gratuito",
        nome="Grátis",
        preco_mensal=0,
        max_produtos=50,
        max_usuarios=2,
        descricao="Para começar a organizar o estoque.",
    ),
    "pro": Plano(
        codigo="pro",
        nome="Pro",
        preco_mensal=None,
        max_produtos=500,
        max_usuarios=10,
        descricao="Para negócios que já precisam de mais controle.",
        destaque=True,
    ),
    "empresa": Plano(
        codigo="empresa",
        nome="Empresa",
        preco_mensal=None,
        max_produtos=None,
        max_usuarios=None,
        descricao="Para operações maiores e em crescimento.",
    ),
}


def obter_plano(codigo: str | None) -> Plano:
    """Retorna o plano informado ou Grátis quando o valor não for reconhecido."""
    return PLANOS.get((codigo or "").strip().lower(), PLANOS["gratuito"])


def limite_atingido(atual: int, limite: int | None) -> bool:
    """Indica se um limite foi atingido. None significa ilimitado."""
    return limite is not None and atual >= limite
