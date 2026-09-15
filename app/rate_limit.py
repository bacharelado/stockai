"""Rate limiting compartilhado via Redis com fallback local seguro."""

from __future__ import annotations

from threading import Lock

try:
    import redis
except ImportError:  # pragma: no cover - dependencia declarada no requirements
    redis = None

from app.config import REDIS_URL


_REDIS_CONNECT_TIMEOUT = 1.0
_REDIS_SOCKET_TIMEOUT = 1.0
_REDIS_LUA_RATE_LIMIT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""
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
    """Registra uma tentativa atomica em Redis com janela fixa.

    Retorna True quando permitido, False quando excedido e None quando Redis
    nao esta configurado ou esta indisponivel. Nesse ultimo caso o chamador
    deve usar seu fallback local para manter a aplicacao funcional.
    """
    if limit < 1 or window_seconds < 1:
        raise ValueError("limit e window_seconds devem ser positivos")

    client = _get_redis()
    if client is None:
        return None

    redis_key = f"stockai:ratelimit:{key}"
    try:
        count = client.eval(_REDIS_LUA_RATE_LIMIT, 1, redis_key, window_seconds)
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
