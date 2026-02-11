from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_webhook_create_limit_enforced(
    async_client: AsyncClient,
    db: AsyncSession,
    enterprise_auth_headers: dict,
) -> None:
    org_id = "org_enterprise"

    # Ensure clean state for this org
    await db.execute(text("DELETE FROM webhooks WHERE organization_id = :org"), {"org": org_id})
    await db.commit()

    webhook_ids: list[str] = []
    try:
        for _ in range(10):
            webhook_id = f"wh_test_{uuid.uuid4().hex[:12]}"
            webhook_ids.append(webhook_id)
            await db.execute(
                text(
                    """
                    INSERT INTO webhooks (
                        id, organization_id, url, events, secret_hash,
                        is_active, is_verified, success_count, failure_count, created_at
                    ) VALUES (
                        :id, :org, :url, :events, NULL,
                        true, false, 0, 0, NOW()
                    )
                    """
                ),
                {
                    "id": webhook_id,
                    "org": org_id,
                    "url": f"https://example.com/{webhook_id}",
                    "events": ["document.signed"],
                },
            )
        await db.commit()

        resp = await async_client.post(
            "/api/v1/webhooks",
            json={"url": "https://example.com/overflow", "events": ["document.signed"]},
            headers=enterprise_auth_headers,
        )

        assert resp.status_code == 403
        payload = resp.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == "WEBHOOK_LIMIT_REACHED"
    finally:
        for webhook_id in webhook_ids:
            await db.execute(text("DELETE FROM webhooks WHERE id = :id"), {"id": webhook_id})
        await db.commit()
