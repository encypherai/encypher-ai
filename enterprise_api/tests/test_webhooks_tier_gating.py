import pytest
from httpx import AsyncClient


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
    business_auth_headers: dict,
) -> None:
    response = await async_client.get("/api/v1/webhooks", headers=business_auth_headers)
    assert response.status_code == 200
