from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_builtin_c2pa_templates_list_requires_business(async_client: AsyncClient, starter_auth_headers: dict) -> None:
    resp = await async_client.get(
        "/api/v1/enterprise/c2pa/templates",
        headers=starter_auth_headers,
    )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_builtin_c2pa_templates_are_listed(async_client: AsyncClient, business_auth_headers: dict) -> None:
    resp = await async_client.get(
        "/api/v1/enterprise/c2pa/templates",
        headers=business_auth_headers,
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert "templates" in payload

    template_ids = {template["id"] for template in payload["templates"]}
    assert "tmpl_builtin_all_rights_reserved_v1" in template_ids
    assert "tmpl_builtin_no_ai_training_v1" in template_ids
    assert "tmpl_builtin_rag_allowed_with_attribution_v1" in template_ids
    assert "tmpl_builtin_realtime_quotes_with_attribution_v1" in template_ids
