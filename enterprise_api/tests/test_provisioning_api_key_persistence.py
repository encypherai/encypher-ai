import hashlib
import json

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_auto_provision_persists_api_key_and_org(async_client, db) -> None:
    email = "provisioning-key-test@example.com"
    response = await async_client.post(
        "/api/v1/provisioning/auto-provision",
        json={
            "email": email,
            "organization_name": "Provisioning Key Test",
            "source": "sdk",
            "source_metadata": {"test": True},
            "tier": "free",
            "auto_activate": True,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    api_key = payload["api_key"]["api_key"]
    organization_id = payload["organization_id"]

    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    key_result = await db.execute(
        text(
            """
            SELECT key_hash, key_prefix, scopes, is_active
            FROM api_keys
            WHERE key_hash = :key_hash
            """
        ),
        {"key_hash": key_hash},
    )
    key_row = key_result.fetchone()

    assert key_row is not None
    assert key_row.key_prefix == api_key[:12]
    assert key_row.is_active is True

    scopes = key_row.scopes or []
    if isinstance(scopes, str):
        scopes = json.loads(scopes)
    assert "sign" in scopes
    assert "verify" in scopes

    org_result = await db.execute(
        text("SELECT id, email FROM organizations WHERE id = :org_id"),
        {"org_id": organization_id},
    )
    org_row = org_result.fetchone()

    assert org_row is not None
    assert org_row.email == email
