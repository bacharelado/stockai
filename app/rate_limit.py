"""Rate limiting compartilhado via Redis com fallback local seguro."""

from __future__ import annotations

import os
from threading import Lock

try:
    import redis
except ImportError:  # pragma: no cover - dependencia declarada no requirements
    redis = None


REDIS_URL = os.getenv("STOCKAI_REDIS_URL")
_REDIS_CONNECT_TIMEOUT = 1.0
_REDIS_SOCKET_TIMEOUT = 1.0
_redis_client = None
_redis_lock = Lock()


def _get_redis():
    """Cria o cliente Redis sob demanda, sem bloquear o boot da aplicacao."""
    global _redis_client
    if not REDIS_URL or redis is None:
        return None
    if _redis_client is None:
        with _redis_lock:
            if _redis_client is None:
                _redis_client = redis.Redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=_REDIS_CONNECT_TIMEOUT,
                    socket_timeout=_REDIS_SOCKET_TIMEOUT,
                )
    return _redis_client


def redis_configured() -> bool:
    return bool(REDIS_URL and redis is not None)


def shared_rate_limit(key: str, limit: int, window_seconds: int) -> bool | None:
    """Registra uma tentativa de forma atomica em Redis.

    Retorna True quando permitido, False quando excedido e None quando Redis
    nao esta configurado ou esta indisponivel. Nesse ultimo caso o chamador
    deve usar seu fallback local para manter a aplicacao funcional.
    """
    client = _get_redis()
    if client is None:
        return None

    redis_key = f"stockai:ratelimit:{key}"
    try:
        with client.pipeline(transaction=True) as pipe:
            pipe.incr(redis_key)
            pipe.expire(redis_key, window_seconds)
            count, _ = pipe.execute()
        return int(count) <= limit
    except Exception:
        # Falha no Redis nao deve derrubar autenticacao ou cadastro.
        return None


def clear_shared_rate_limit(key: str) -> None:
    client = _get_redis()
    if client is None:
        return
    try:
        client.delete(f"stockai:ratelimit:{key}")
    except Exception:
        pass


def redis_healthcheck() -> bool:
    client = _get_redis()
    if client is None:
        return False
    try:
        return bool(client.ping())
    except Exception:
        return False
