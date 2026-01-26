import pytest


@pytest.mark.asyncio
async def test_health_check_allows_railway_up_domain(client):
    response = await client.get(
        "/health",
        headers={"Host": "my-service-production.up.railway.app"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "healthy"
