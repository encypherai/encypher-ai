import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_c2pa_schema_create_requires_enterprise(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    unique_label = f"com.tests.business.blocked.{uuid.uuid4().hex[:8]}"
    schema_data = {
        "name": "Blocked Schema",
        "label": unique_label,
        "version": "1.0",
        "description": "Should be blocked for business tier",
        "is_public": False,
        "json_schema": {"type": "object", "properties": {"field": {"type": "string"}}},
    }

    response = await async_client.post(
        "/api/v1/enterprise/c2pa/schemas",
        json=schema_data,
        headers=business_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_c2pa_schema_create_allows_enterprise(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    unique_label = f"com.tests.enterprise.allowed.{uuid.uuid4().hex[:8]}"
    schema_data = {
        "name": "Allowed Schema",
        "label": unique_label,
        "version": "1.0",
        "description": "Should be allowed for enterprise tier",
        "is_public": False,
        "json_schema": {"type": "object", "properties": {"field": {"type": "string"}}},
    }

    response = await async_client.post(
        "/api/v1/enterprise/c2pa/schemas",
        json=schema_data,
        headers=enterprise_auth_headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["label"] == unique_label


@pytest.mark.asyncio
async def test_c2pa_template_create_requires_enterprise(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/enterprise/c2pa/templates",
        json={
            "name": "Blocked Template",
            "schema_id": "00000000-0000-0000-0000-000000000000",
            "template_data": {"field": "value"},
            "description": "Should be blocked for business tier",
            "category": "publisher",
            "is_public": False,
        },
        headers=business_auth_headers,
    )

    assert response.status_code == 403
