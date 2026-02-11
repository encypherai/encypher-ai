from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_builtin_c2pa_templates_available_to_free_tier(async_client: AsyncClient, starter_auth_headers: dict) -> None:
    """TEAM_166: Templates are available to all tiers."""
    resp = await async_client.get(
        "/api/v1/enterprise/c2pa/templates",
        headers=starter_auth_headers,
    )

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_builtin_c2pa_templates_are_listed(async_client: AsyncClient, enterprise_auth_headers: dict) -> None:
    resp = await async_client.get(
        "/api/v1/enterprise/c2pa/templates",
        headers=enterprise_auth_headers,
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert "templates" in payload

    template_ids = {template["id"] for template in payload["templates"]}
    assert "tmpl_builtin_all_rights_reserved_v1" in template_ids
    assert "tmpl_builtin_no_ai_training_v1" in template_ids
    assert "tmpl_builtin_rag_allowed_with_attribution_v1" in template_ids
    assert "tmpl_builtin_realtime_quotes_with_attribution_v1" in template_ids
    assert "tmpl_builtin_cc_by_4_0_v1" in template_ids
    assert "tmpl_builtin_cc_by_nc_4_0_v1" in template_ids
    assert "tmpl_builtin_academic_open_access_v1" in template_ids
    assert "tmpl_builtin_news_wire_syndication_v1" in template_ids
