"""Tests for whitelabel portal branding (TEAM_255 Gap 2).

Verifies that:
1. whitelabel=true + org display name -> shows org name, no Encypher
2. whitelabel=false -> shows "Verified by Encypher Verification Service"
3. Auth-service failure defaults to showing Encypher branding (fail-open)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata


def _mock_db_row(signed_text: str, title: str = "Test Doc", org_id: str = "org_wl"):
    mock_row = MagicMock()
    mock_row._mapping = {
        "signed_text": signed_text,
        "title": title,
        "organization_id": org_id,
    }
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    return mock_result


def _make_signed_text():
    private_key, _public_key = generate_ed25519_key_pair()
    return UnicodeMetadata.embed_metadata(
        text="Hello world",
        private_key=private_key,
        signer_id="org_wl",
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )


def _mock_auth_response(whitelabel: bool, display_name: str = "Acme News"):
    """Build a mock httpx.Response matching auth-service internal context."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.json.return_value = {
        "success": True,
        "data": {
            "id": "org_wl",
            "name": "Acme News Corp",
            "display_name": display_name,
            "features": {"whitelabel": whitelabel},
        },
    }
    return resp


def _mock_auth_failure():
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 500
    resp.json.return_value = {"error": "internal"}
    return resp


def test_whitelabel_true_shows_org_name(client, mock_db, monkeypatch):
    """When whitelabel=true, portal footer shows org display name."""
    signed_text = _make_signed_text()
    mock_db.execute.return_value = _mock_db_row(signed_text)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_auth_response(whitelabel=True, display_name="Acme News"))

    with patch("app.api.v1.endpoints.httpx.AsyncClient", return_value=mock_client):
        response = client.get("/api/v1/verify/doc_wl1")

    assert response.status_code == 200
    assert "Verified by Acme News" in response.text
    assert "Encypher Verification Service" not in response.text


def test_whitelabel_false_shows_encypher_branding(client, mock_db, monkeypatch):
    """When whitelabel=false, portal footer shows default Encypher branding."""
    signed_text = _make_signed_text()
    mock_db.execute.return_value = _mock_db_row(signed_text)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_auth_response(whitelabel=False))

    with patch("app.api.v1.endpoints.httpx.AsyncClient", return_value=mock_client):
        response = client.get("/api/v1/verify/doc_wl2")

    assert response.status_code == 200
    assert "Verified by Encypher Verification Service" in response.text


def test_auth_service_failure_defaults_to_encypher_branding(client, mock_db, monkeypatch):
    """When auth-service is unreachable, default to showing Encypher branding."""
    signed_text = _make_signed_text()
    mock_db.execute.return_value = _mock_db_row(signed_text)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))

    with patch("app.api.v1.endpoints.httpx.AsyncClient", return_value=mock_client):
        response = client.get("/api/v1/verify/doc_wl3")

    assert response.status_code == 200
    assert "Verified by Encypher Verification Service" in response.text


def test_auth_service_500_defaults_to_encypher_branding(client, mock_db, monkeypatch):
    """When auth-service returns 500, default to showing Encypher branding."""
    signed_text = _make_signed_text()
    mock_db.execute.return_value = _mock_db_row(signed_text)

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_auth_failure())

    with patch("app.api.v1.endpoints.httpx.AsyncClient", return_value=mock_client):
        response = client.get("/api/v1/verify/doc_wl4")

    assert response.status_code == 200
    assert "Verified by Encypher Verification Service" in response.text
