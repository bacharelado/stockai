from unittest.mock import Mock, patch

from app import rate_limit


def test_shared_rate_limit_allows_requests_until_limit():
    client = Mock()
    client.eval.return_value = 1

    with patch.object(rate_limit, "_get_redis", return_value=client):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is True

    client.eval.assert_called_once_with(
        rate_limit._REDIS_LUA_RATE_LIMIT,
        1,
        "stockai:ratelimit:login:user",
        300,
    )


def test_shared_rate_limit_blocks_when_limit_is_exceeded():
    client = Mock()
    client.eval.return_value = 3

    with patch.object(rate_limit, "_get_redis", return_value=client):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is False


def test_shared_rate_limit_falls_back_when_redis_is_unavailable():
    with patch.object(rate_limit, "_get_redis", return_value=None):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is None


def test_shared_rate_limit_returns_none_when_redis_fails():
    client = Mock()
    client.eval.side_effect = RuntimeError("redis unavailable")

    with patch.object(rate_limit, "_get_redis", return_value=client):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is None
