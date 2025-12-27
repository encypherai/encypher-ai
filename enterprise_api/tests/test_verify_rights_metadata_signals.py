from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.verification_logic import VerificationExecution


@pytest.mark.asyncio
async def test_verify_surfaces_encypher_rights_metadata(async_client: AsyncClient) -> None:
    execution = VerificationExecution(
        is_valid=True,
        signer_id="org_business",
        manifest={
            "assertions": [
                {
                    "label": "com.encypher.rights.v1",
                    "data": {
                        "copyright_holder": "Example Publisher",
                        "license_url": "https://example.com/license",
                        "usage_terms": "RAG allowed with attribution.",
                        "syndication_allowed": True,
                        "contact_email": "licensing@example.com",
                    },
                }
            ]
        },
        missing_signers=set(),
        revoked_signers=set(),
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
            headers={"X-Forwarded-For": "203.0.113.252"},
        )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    details = payload["data"]["details"]
    rights = details.get("rights_signals")
    assert rights is not None

    rights_metadata = rights.get("rights")
    assert rights_metadata is not None
    assert rights_metadata["copyright_holder"] == "Example Publisher"
    assert rights_metadata["license_url"] == "https://example.com/license"
    assert rights_metadata["syndication_allowed"] is True
