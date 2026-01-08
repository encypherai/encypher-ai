from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.verification_logic import VerificationExecution


@pytest.mark.asyncio
async def test_verify_surfaces_training_mining_rights_signals(async_client: AsyncClient) -> None:
    execution = VerificationExecution(
        is_valid=True,
        signer_id="org_business",
        manifest={
            "assertions": [
                {
                    "label": "c2pa.training-mining.v1",
                    "data": {
                        "use": {
                            "ai_training": False,
                            "ai_inference": True,
                            "data_mining": False,
                        },
                        "constraint_info": {
                            "license": "All Rights Reserved",
                            "license_url": "https://example.com/license",
                        },
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

    training_mining = rights.get("training_mining")
    assert training_mining is not None
    assert training_mining["use"]["ai_training"] is False
    assert training_mining["use"]["ai_inference"] is True
    assert training_mining["use"]["data_mining"] is False
    assert training_mining["constraint_info"]["license"] == "All Rights Reserved"
    assert training_mining["constraint_info"]["license_url"] == "https://example.com/license"
