from unittest.mock import Mock, patch

from app import rate_limit


def test_shared_rate_limit_allows_requests_until_limit():
    pipe = Mock()
    pipe.execute.return_value = (1, True)
    client = Mock()
    client.pipeline.return_value.__enter__.return_value = pipe

    with patch.object(rate_limit, "_get_redis", return_value=client):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is True

    pipe.incr.assert_called_once_with("stockai:ratelimit:login:user")
    pipe.expire.assert_called_once_with("stockai:ratelimit:login:user", 300)


def test_shared_rate_limit_blocks_when_limit_is_exceeded():
    pipe = Mock()
    pipe.execute.return_value = (3, True)
    client = Mock()
    client.pipeline.return_value.__enter__.return_value = pipe

    with patch.object(rate_limit, "_get_redis", return_value=client):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is False


def test_shared_rate_limit_falls_back_when_redis_is_unavailable():
    with patch.object(rate_limit, "_get_redis", return_value=None):
        assert rate_limit.shared_rate_limit("login:user", 2, 300) is None
