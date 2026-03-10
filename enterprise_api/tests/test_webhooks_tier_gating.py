import pytest
from httpx import AsyncClient
from sqlalchemy import text


@pytest.mark.asyncio
async def test_webhooks_requires_business_tier_on_list(
    async_client: AsyncClient,
    professional_auth_headers: dict,
) -> None:
    response = await async_client.get("/api/v1/webhooks", headers=professional_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhooks_requires_business_tier_on_create(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/webhooks",
        json={"url": "https://example.com/webhook", "events": ["document.signed"]},
        headers=starter_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhooks_allows_business_tier_on_list(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    response = await async_client.get("/api/v1/webhooks", headers=enterprise_auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_test_rejects_untrusted_stored_url(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
    db,
    monkeypatch,
) -> None:
    webhook_id = "wh_test_poisoned_url"

    await db.execute(
        text(
            """
            INSERT INTO webhooks (
                id, organization_id, url, events, secret_hash,
                is_active, is_verified, success_count, failure_count, created_at
            )
            VALUES (
                :id, :org_id, :url, :events, NULL,
                true, false, 0, 0, NOW()
            )
            """
        ),
        {
            "id": webhook_id,
            "org_id": "org_enterprise",
            "url": "https://127.0.0.1/poisoned",
            "events": ["document.signed"],
        },
    )
    await db.commit()

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            _ = args
            _ = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            _ = exc_type
            _ = exc
            _ = tb
            return False

        async def post(self, *args, **kwargs):
            _ = args
            _ = kwargs
            raise AssertionError("Outbound request should not be attempted for untrusted webhook URL")

    import app.routers.webhooks as webhooks_module

    monkeypatch.setattr(webhooks_module, "httpx", type("_httpx", (), {"AsyncClient": FakeAsyncClient})())

    try:
        response = await async_client.post(
            f"/api/v1/webhooks/{webhook_id}/test",
            headers=enterprise_auth_headers,
        )
        assert response.status_code == 400
    finally:
        await db.execute(text("DELETE FROM webhook_deliveries WHERE webhook_id = :id"), {"id": webhook_id})
        await db.execute(text("DELETE FROM webhooks WHERE id = :id"), {"id": webhook_id})
        await db.commit()
