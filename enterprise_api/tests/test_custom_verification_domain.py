"""Tests for custom verification domain URL generation (TEAM_255).

Verifies that:
1. Signing with verification_domain set produces custom-domain URL
2. Signing without it falls back to verify.encypherai.com
3. Demo org always uses default domain
"""

from unittest.mock import patch

from app.services.signing_executor import _build_verification_url


def _prod_settings():
    """Return a mock settings object simulating production."""
    return patch("app.services.signing_executor.settings", is_development=False, infrastructure_domain="encypherai.com")


def test_custom_domain_in_verification_url():
    """When org has verification_domain, use it in the URL."""
    org = {"verification_domain": "verify.acmenews.com"}
    with _prod_settings():
        url = _build_verification_url(document_id="doc_123", is_demo_org=False, organization=org)
    assert url == "https://verify.acmenews.com/doc_123"


def test_fallback_to_default_domain():
    """When org has no verification_domain, use verify.encypherai.com."""
    org = {"verification_domain": None}
    with _prod_settings():
        url = _build_verification_url(document_id="doc_456", is_demo_org=False, organization=org)
    assert url == "https://verify.encypherai.com/doc_456"


def test_empty_org_falls_back():
    """Empty org dict falls back to default domain."""
    with _prod_settings():
        url = _build_verification_url(document_id="doc_789", is_demo_org=False, organization={})
    assert url == "https://verify.encypherai.com/doc_789"


def test_demo_org_ignores_custom_domain():
    """Demo org always uses the default domain, even if verification_domain is set."""
    org = {"verification_domain": "verify.acmenews.com"}
    with _prod_settings():
        url = _build_verification_url(document_id="doc_demo", is_demo_org=True, organization=org)
    assert "verify.encypherai.com" in url
    assert "demo/doc_demo" in url


def test_development_mode_ignores_custom_domain():
    """In development mode, always use localhost."""
    org = {"verification_domain": "verify.acmenews.com"}
    url = _build_verification_url(document_id="doc_dev", is_demo_org=False, organization=org)
    assert "localhost" in url
    assert "doc_dev" in url
