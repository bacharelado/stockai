from app.security_headers import HSTS_VALUE


def test_hsts_value_is_safe_for_production():
    assert HSTS_VALUE == "max-age=31536000; includeSubDomains"
    assert "preload" not in HSTS_VALUE
