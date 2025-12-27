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
