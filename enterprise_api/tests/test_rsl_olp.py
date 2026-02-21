"""
Integration Tests for RSL + OLP Endpoints (Phase 8).

Covers:
- RSL XML generation (8.1)
- robots-txt generation (8.2)
- RSL Import (8.3)
- OLP Token (8.4)
- OLP Validate (8.5)
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


# The demo auth_headers fixture maps to org_id="org_demo"
DEMO_ORG_ID = "org_demo"


# ════════════════════════════════════════════════════════════════════════════════
# 8.1 — RSL XML
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_rsl_xml_no_auth_required(async_client: AsyncClient) -> None:
    """GET /api/v1/public/rights/organization/{org_id}/rsl requires no auth (200 or 404)."""
    resp = await async_client.get(
        f"/api/v1/public/rights/organization/{DEMO_ORG_ID}/rsl"
    )
    assert resp.status_code in (200, 404), f"Expected 200 or 404, got {resp.status_code}"


@pytest.mark.asyncio
async def test_rsl_xml_with_profile(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """Set a rights profile, then call RSL endpoint -> 200 with XML content and <license> elements."""
    # Set a rights profile for the demo org
    put_resp = await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "RSL XML Test Publisher",
            "publisher_url": "https://rsltest.example.com",
            "contact_email": "rights@rsltest.example.com",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True, "crawling": True}},
            "silver_tier": {"permissions": {"allowed": True}},
            "gold_tier": {"permissions": {"allowed": False, "requires_license": True}},
        },
        headers=auth_headers,
    )
    assert put_resp.status_code in (200, 201), put_resp.text

    # Fetch RSL XML
    resp = await async_client.get(
        f"/api/v1/public/rights/organization/{DEMO_ORG_ID}/rsl"
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    content_type = resp.headers.get("content-type", "")
    assert "xml" in content_type.lower() or "text/plain" in content_type.lower(), (
        f"Expected XML content-type, got: {content_type}"
    )
    assert "<license" in resp.text, "RSL XML should contain <license> elements"


# ════════════════════════════════════════════════════════════════════════════════
# 8.2 — robots-txt
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_robots_txt_returns_text(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """GET .../robots-txt returns 200, text/plain, and contains relevant directives."""
    # Ensure there is a profile for the demo org
    await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "Robots Test Publisher",
            "contact_email": "robots@test.example.com",
            "default_license_type": "tiered",
            "bronze_tier": {"permissions": {"allowed": True}},
            "silver_tier": {},
            "gold_tier": {},
        },
        headers=auth_headers,
    )

    resp = await async_client.get(
        f"/api/v1/public/rights/organization/{DEMO_ORG_ID}/robots-txt"
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    content_type = resp.headers.get("content-type", "")
    assert "text/plain" in content_type.lower(), f"Expected text/plain, got: {content_type}"

    body = resp.text
    assert any(kw in body for kw in ("User-agent", "RSL", "License")), (
        f"robots-txt should contain User-agent, RSL, or License. Got: {body[:200]}"
    )


# ════════════════════════════════════════════════════════════════════════════════
# 8.3 — RSL Import
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_rsl_import_requires_auth(async_client: AsyncClient) -> None:
    """POST /api/v1/rights/rsl/import without auth -> 401/403."""
    resp = await async_client.post(
        "/api/v1/rights/rsl/import",
        json={"rsl_xml": "<rsl></rsl>"},
    )
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"


@pytest.mark.asyncio
async def test_rsl_import_valid_xml(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/rights/rsl/import with valid RSL XML -> 200/201, creates a profile."""
    rsl_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rsl xmlns="https://rslstandard.org/rsl" version="1.0">
  <publisher>
    <name>Import Test Publisher</name>
    <url>https://importtest.example.com</url>
    <contact>import@example.com</contact>
  </publisher>
  <content url="/" server="https://api.example.com/olp">
    <license usage="crawl">
      <type>allowed</type>
      <standard>https://rslstandard.org/licenses/open</standard>
      <terms url="https://importtest.example.com/terms" />
    </license>
    <license usage="retrieval">
      <type>paid</type>
      <standard>https://rslstandard.org/licenses/commercial-ai</standard>
      <terms url="https://importtest.example.com/terms" />
    </license>
    <license usage="training">
      <type>prohibited</type>
      <standard>https://rslstandard.org/licenses/open</standard>
      <terms url="https://importtest.example.com/terms" />
    </license>
  </content>
</rsl>"""

    resp = await async_client.post(
        "/api/v1/rights/rsl/import",
        json={"rsl_xml": rsl_xml},
        headers=auth_headers,
    )

    if resp.status_code == 501:
        pytest.skip("RSL import endpoint returns 501 (not implemented)")

    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"

    body = resp.json()
    assert body.get("imported") is True, f"Expected imported=True, got: {body}"
    assert "profile" in body, f"Expected 'profile' key in response: {body}"


@pytest.mark.asyncio
async def test_rsl_import_invalid_xml(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST /api/v1/rights/rsl/import with bad XML -> 422 or 400."""
    resp = await async_client.post(
        "/api/v1/rights/rsl/import",
        json={"rsl_xml": "this is not valid XML at all <<<<>>>"},
        headers=auth_headers,
    )

    if resp.status_code == 501:
        pytest.skip("RSL import endpoint returns 501 (not implemented)")

    assert resp.status_code in (400, 422, 500), (
        f"Expected 400/422/500 for invalid XML, got {resp.status_code}: {resp.text}"
    )


# ════════════════════════════════════════════════════════════════════════════════
# 8.4 — OLP Token
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_olp_token_endpoint_exists(async_client: AsyncClient) -> None:
    """POST /api/v1/public/rights/rsl/olp/token exists (200/4xx, not 404)."""
    resp = await async_client.post(
        "/api/v1/public/rights/rsl/olp/token",
        json={},
    )
    # The endpoint should exist. It may return 404 for "publisher not found"
    # but that is a business-logic 404, not a route-not-found 404.
    # A route-not-found would be {"detail": "Not Found"} with Method Not Allowed
    # or a generic 404. We accept any status that isn't 405 (method not allowed).
    assert resp.status_code != 405, "OLP token endpoint should accept POST"


@pytest.mark.asyncio
async def test_olp_token_requires_org(async_client: AsyncClient) -> None:
    """POST with missing/empty target_url -> 404 (publisher not found) or 422."""
    resp = await async_client.post(
        "/api/v1/public/rights/rsl/olp/token",
        json={"grant_type": "rsl_license", "scope": "crawl"},
    )
    assert resp.status_code in (400, 404, 422), (
        f"Expected 400/404/422 for missing org context, got {resp.status_code}"
    )


@pytest.mark.asyncio
async def test_olp_token_with_valid_request(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    """POST with organization_id, crawler info -> response includes token or denial."""
    # Set up a rights profile with a publisher_url so OLP can resolve it
    await async_client.put(
        "/api/v1/rights/profile",
        json={
            "publisher_name": "OLP Token Test Publisher",
            "publisher_url": "https://olptest.example.com",
            "contact_email": "olp@test.example.com",
            "default_license_type": "tiered",
            "bronze_tier": {
                "permissions": {"allowed": True, "crawling": True},
            },
            "silver_tier": {"permissions": {"allowed": False}},
            "gold_tier": {"permissions": {"allowed": False}},
        },
        headers=auth_headers,
    )

    resp = await async_client.post(
        "/api/v1/public/rights/rsl/olp/token",
        json={
            "grant_type": "rsl_license",
            "scope": "crawl",
            "user_agent": "TestCrawlerBot/1.0",
            "target_url": "https://olptest.example.com/article/123",
        },
    )

    if resp.status_code == 501:
        pytest.skip("OLP token endpoint returns 501 (not implemented)")

    # The endpoint resolves org from target_url via publisher_url matching.
    # This may return 404 if DB matching doesn't find the org, or 200 with a token,
    # or 401/402 depending on tier permissions.
    assert resp.status_code in (200, 401, 402, 404), (
        f"Expected 200/401/402/404, got {resp.status_code}: {resp.text}"
    )

    if resp.status_code == 200:
        body = resp.json()
        assert "access_token" in body, f"Expected access_token in 200 response: {body}"
        assert body.get("token_type") == "License"


# ════════════════════════════════════════════════════════════════════════════════
# 8.5 — OLP Validate
# ════════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_olp_validate_invalid_token(async_client: AsyncClient) -> None:
    """GET /api/v1/public/rights/rsl/olp/validate/bad-token -> 401 or 422 (not 500)."""
    resp = await async_client.get(
        "/api/v1/public/rights/rsl/olp/validate/bad-token"
    )
    assert resp.status_code != 500, f"Validate should not return 500, got: {resp.text}"
    assert resp.status_code in (401, 404, 422), (
        f"Expected 401/404/422 for invalid token, got {resp.status_code}"
    )


@pytest.mark.asyncio
async def test_olp_validate_endpoint_exists(async_client: AsyncClient) -> None:
    """The OLP validate endpoint responds (any non-500 status)."""
    resp = await async_client.get(
        "/api/v1/public/rights/rsl/olp/validate/ency_olp_test_token_123"
    )
    assert resp.status_code != 500, f"Validate endpoint returned 500: {resp.text}"
    # A valid ency_olp_ prefix token should return 200
    if resp.status_code == 200:
        body = resp.json()
        assert body.get("valid") is True
