from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.verification_logic import VerificationExecution


@pytest.mark.asyncio
async def test_verify_doc_revoked_is_not_tampered(async_client: AsyncClient) -> None:
    execution = VerificationExecution(
        is_valid=False,
        signer_id="org_business",
        manifest={"assertions": []},
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=True,
        revocation_reason="Document has been revoked by publisher",
        revocation_check_status="revoked",
        revocation_check_error=None,
        revocation_status_list_url="https://status.encypherai.com/v1/org_business/list/0",
        revocation_bit_index=123,
    )

    with (
        patch("app.routers.verification.public_rate_limiter", new=AsyncMock(return_value={})),
        patch("app.routers.verification.execute_verification", new=AsyncMock(return_value=execution)),
    ):
        resp = await async_client.post(
            "/api/v1/verify",
            json={"text": "signed"},
            headers={"X-Forwarded-For": "203.0.113.250"},
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["valid"] is False
    assert data["reason_code"] == "DOC_REVOKED"
    assert data["tampered"] is False
    assert data["details"].get("document_revoked") is True
    revocation_check = data["details"].get("revocation_check")
    assert isinstance(revocation_check, dict)
    assert revocation_check.get("status") == "revoked"
    assert revocation_check.get("status_list_url") == "https://status.encypherai.com/v1/org_business/list/0"
    assert revocation_check.get("bit_index") == 123


@pytest.mark.asyncio
async def test_verify_cert_revoked_is_not_tampered(async_client: AsyncClient) -> None:
    execution = VerificationExecution(
        is_valid=False,
        signer_id="org_business",
        manifest={"assertions": []},
        missing_signers=set(),
        revoked_signers={"org_business"},
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=False,
        revocation_reason=None,
    )

    with (
        patch("app.routers.verification.public_rate_limiter", new=AsyncMock(return_value={})),
        patch("app.routers.verification.execute_verification", new=AsyncMock(return_value=execution)),
    ):
        resp = await async_client.post(
            "/api/v1/verify",
            json={"text": "signed"},
            headers={"X-Forwarded-For": "203.0.113.251"},
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["valid"] is False
    assert data["reason_code"] == "CERT_REVOKED"
    assert data["tampered"] is False
    assert "revoked_signers" in data["details"]


@pytest.mark.asyncio
async def test_verify_revocation_unknown_is_exposed(async_client: AsyncClient) -> None:
    execution = VerificationExecution(
        is_valid=True,
        signer_id="org_business",
        manifest={"assertions": []},
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=False,
        revocation_reason=None,
        revocation_check_status="unknown",
        revocation_check_error="timeout",
        revocation_status_list_url="https://status.encypherai.com/v1/org_business/list/0",
        revocation_bit_index=42,
    )

    with (
        patch("app.routers.verification.public_rate_limiter", new=AsyncMock(return_value={})),
        patch("app.routers.verification.execute_verification", new=AsyncMock(return_value=execution)),
    ):
        resp = await async_client.post(
            "/api/v1/verify",
            json={"text": "signed"},
            headers={"X-Forwarded-For": "203.0.113.252"},
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["valid"] is True
    assert data["reason_code"] == "OK"

    revocation_check = data["details"].get("revocation_check")
    assert isinstance(revocation_check, dict)
    assert revocation_check.get("status") == "unknown"
    assert revocation_check.get("error") == "timeout"
    assert revocation_check.get("status_list_url") == "https://status.encypherai.com/v1/org_business/list/0"
    assert revocation_check.get("bit_index") == 42
