import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_verify_document_id_not_found_returns_html(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/verify/doc_does_not_exist")

    assert response.status_code == 410
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "ENDPOINT_DEPRECATED"


@pytest.mark.asyncio
async def test_verify_subdomain_root_document_id_not_found_returns_html(async_client: AsyncClient) -> None:
    response = await async_client.get(
        "/doc_does_not_exist",
        headers={"Host": "verify.encypherai.com"},
    )

    assert response.status_code == 404
    assert "text/html" not in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_verify_subdomain_demo_document_id_not_found_returns_html(async_client: AsyncClient) -> None:
    response = await async_client.get(
        "/demo/doc_does_not_exist",
        headers={"Host": "verify.encypherai.com"},
    )

    assert response.status_code == 404
    assert "text/html" not in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_api_root_document_id_is_not_exposed_on_api_host(async_client: AsyncClient) -> None:
    response = await async_client.get("/doc_does_not_exist")

    assert response.status_code == 404
    assert "text/html" not in response.headers.get("content-type", "")
