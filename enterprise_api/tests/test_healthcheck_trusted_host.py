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


@pytest.mark.asyncio
async def test_health_check_allows_internal_ip_host_header(client):
    response = await client.get(
        "/health",
        headers={"Host": "100.64.0.2"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "healthy"
