import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


@pytest.mark.asyncio
async def test_sign_advanced_composed_org_missing_bootstraps_and_auto_provisions_key(
    async_client: AsyncClient,
    db: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "compose_org_context_via_auth_service", True)

    headers = {"Authorization": "Bearer ency_test_key", "Content-Type": "application/json"}
    org_id = "org_missing_private_key"

    key_context = {
        "key_id": "key_test_123",
        "organization_id": org_id,
        "permissions": ["sign"],
        "user_id": "usr_test_123",
    }
    org_data = {
        "id": org_id,
        "name": "Missing Org",
        "tier": "professional",
        "features": {},
        "monthly_api_limit": 10000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 65,
        "certificate_pem": None,
    }

    with (
        patch("app.dependencies.key_service_client.validate_key_minimal", new=AsyncMock(return_value=key_context)),
        patch("app.dependencies.auth_service_client.get_organization_context", new=AsyncMock(return_value=org_data)),
    ):
        response = await async_client.post(
            "/api/v1/sign/advanced",
            json={
                "document_id": "doc_bootstrap_001",
                "text": "Hello world. Advanced signing.",
            },
            headers=headers,
        )

    assert response.status_code == 201

    row = (
        await db.execute(
            text("SELECT private_key_encrypted, public_key FROM organizations WHERE id = :org_id"),
            {"org_id": org_id},
        )
    ).fetchone()
    assert row is not None
    assert row.private_key_encrypted
    assert row.public_key
