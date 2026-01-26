"""Regression tests for trusted proxy handling in public rate limiter."""

from unittest.mock import Mock

import pytest
from fastapi import Request

from app.middleware.public_rate_limiter import PublicAPIRateLimiter


def _make_request(headers: dict, client_host: str) -> Request:
    request = Mock(spec=Request)
    request.headers = headers
    request.client = Mock()
    request.client.host = client_host
    return request


def test_get_client_ip_ignores_forwarded_headers_when_untrusted():
    limiter = PublicAPIRateLimiter()

    request = _make_request({"X-Forwarded-For": "10.0.0.1", "X-Real-IP": "10.0.0.2"}, "192.168.1.1")

    ip = limiter._get_client_ip(request)

    assert ip == "192.168.1.1"


def test_get_client_ip_trusts_forwarded_headers_for_trusted_proxy():
    limiter = PublicAPIRateLimiter(trusted_proxy_ips={"192.168.1.1"})

    request = _make_request({"X-Forwarded-For": "10.0.0.1", "X-Real-IP": "10.0.0.2"}, "192.168.1.1")

    ip = limiter._get_client_ip(request)

    assert ip == "10.0.0.1"


@pytest.mark.parametrize("header_value", ["", "unknown", "bad-ip"])
def test_get_client_ip_uses_client_host_when_forwarded_header_invalid(header_value: str):
    limiter = PublicAPIRateLimiter(trusted_proxy_ips={"192.168.1.1"})

    request = _make_request({"X-Forwarded-For": header_value}, "192.168.1.1")

    ip = limiter._get_client_ip(request)

    assert ip == "192.168.1.1"
