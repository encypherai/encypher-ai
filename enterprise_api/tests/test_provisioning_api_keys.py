import hashlib
import json

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_provisioning_create_and_list_api_keys(async_client, db) -> None:
    response = await async_client.post(
        "/api/v1/provisioning/api-keys",
        json={
            "organization_id": "org_demo",
            "name": "Provisioned Key",
            "scopes": ["sign", "verify", "lookup"],
            "expires_in_days": 30,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    api_key = payload["api_key"]
    key_id = payload["key_id"]

    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    result = await db.execute(
        text(
            """
            SELECT id, key_hash, key_prefix, scopes, is_active
            FROM api_keys
            WHERE id = :key_id
            """
        ),
        {"key_id": key_id},
    )
    row = result.fetchone()

    assert row is not None
    assert row.key_hash == key_hash
    assert row.key_prefix == api_key[:12]
    assert row.is_active is True

    scopes = row.scopes or []
    if isinstance(scopes, str):
        scopes = json.loads(scopes)
    assert "sign" in scopes
    assert "verify" in scopes

    list_response = await async_client.get(
        "/api/v1/provisioning/api-keys",
        params={"organization_id": "org_demo"},
    )

    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["total"] >= 1
    assert any(key["id"] == key_id for key in list_payload["keys"])


@pytest.mark.asyncio
async def test_provisioning_revoke_api_key(async_client, db) -> None:
    response = await async_client.post(
        "/api/v1/provisioning/api-keys",
        json={
            "organization_id": "org_demo",
            "name": "Provisioned Revoke Key",
            "scopes": ["sign", "verify"],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    key_id = payload["key_id"]

    revoke_response = await async_client.request(
        "DELETE",
        f"/api/v1/provisioning/api-keys/{key_id}",
        json={"organization_id": "org_demo", "reason": "compromised"},
    )

    assert revoke_response.status_code == 204

    result = await db.execute(
        text(
            """
            SELECT revoked_at, is_active
            FROM api_keys
            WHERE id = :key_id
            """
        ),
        {"key_id": key_id},
    )
    row = result.fetchone()

    assert row is not None
    assert row.revoked_at is not None
    assert row.is_active is False
