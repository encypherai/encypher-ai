"""Tests for public trust anchor lookup endpoint.

This endpoint enables external C2PA validators to verify Encypher-signed
content by looking up the signer's public key.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trust_anchor_demo_key(async_client: AsyncClient):
    """Test that demo/free tier key is returned for encypher.public."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/encypher.public")

    assert response.status_code == 200
    data = response.json()

    assert data["signer_id"] == "encypher.public"
    assert data["signer_name"] == "Encypher Demo / Free Tier"
    assert "-----BEGIN PUBLIC KEY-----" in data["public_key"]
    assert data["public_key_algorithm"] == "Ed25519"
    assert data["trust_anchor_type"] == "platform"
    assert data["revoked"] is False


@pytest.mark.asyncio
async def test_trust_anchor_org_demo(async_client: AsyncClient):
    """Test that org_demo returns demo key."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/org_demo")

    assert response.status_code == 200
    data = response.json()

    assert data["signer_id"] == "org_demo"
    assert "-----BEGIN PUBLIC KEY-----" in data["public_key"]
    assert data["trust_anchor_type"] == "platform"


@pytest.mark.asyncio
async def test_trust_anchor_demo_prefix(async_client: AsyncClient):
    """Test that demo-* prefix returns demo key."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/demo-test-key")

    assert response.status_code == 200
    data = response.json()

    assert data["signer_id"] == "demo-test-key"
    assert data["trust_anchor_type"] == "platform"


@pytest.mark.asyncio
async def test_trust_anchor_not_found(async_client: AsyncClient):
    """Test 404 for unknown signer."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/org_nonexistent_12345")

    assert response.status_code == 404
    data = response.json()

    # Response may have detail as dict or string depending on FastAPI version
    if isinstance(data.get("detail"), dict):
        assert data["detail"]["error"] == "SIGNER_NOT_FOUND"
    else:
        # Check that it's a 404 with some error indication
        assert "detail" in data or "error" in data


@pytest.mark.asyncio
async def test_trust_anchor_response_structure(async_client: AsyncClient):
    """Test that response has all expected fields."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/encypher.public")

    assert response.status_code == 200
    data = response.json()

    # Required fields
    assert "signer_id" in data
    assert "signer_name" in data
    assert "public_key" in data
    assert "public_key_algorithm" in data
    assert "revoked" in data
    assert "trust_anchor_type" in data

    # Optional fields (may be None)
    assert "key_id" in data
    assert "issued_at" in data
    assert "expires_at" in data


@pytest.mark.asyncio
async def test_trust_anchor_pem_format(async_client: AsyncClient):
    """Test that public key is valid PEM format."""
    response = await async_client.get("/api/v1/public/c2pa/trust-anchors/encypher.public")

    assert response.status_code == 200
    data = response.json()

    public_key_pem = data["public_key"]

    # Verify PEM structure
    assert public_key_pem.startswith("-----BEGIN PUBLIC KEY-----")
    assert public_key_pem.strip().endswith("-----END PUBLIC KEY-----")

    # Verify it can be parsed
    from cryptography.hazmat.primitives import serialization

    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    assert public_key is not None
