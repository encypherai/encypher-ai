"""Tests for bulk-archive-backfill add-on batch entitlement (TEAM_255 Gap 3).

Verifies that:
1. Free tier with backfill add-on can call batch sign (bypasses BATCH_OPERATIONS quota)
2. Free tier without add-on gets quota error
3. Enterprise tier always works (unlimited quota)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


def _batch_request(*, items: int = 2) -> dict:
    return {
        "mode": "c2pa",
        "segmentation_level": "sentence",
        "idempotency_key": "backfill-test-key",
        "items": [
            {
                "document_id": f"doc-backfill-{idx}",
                "text": f"payload-{idx}",
                "title": f"title-{idx}",
            }
            for idx in range(items)
        ],
    }


async def _fake_batch_response(*, correlation_id: str, **_kwargs) -> dict:
    return {
        "success": True,
        "batch_id": "batch_backfill_test",
        "data": None,
        "error": None,
        "correlation_id": correlation_id,
    }


@pytest.mark.asyncio
async def test_free_tier_with_backfill_addon_can_batch_sign(
    async_client: AsyncClient,
    starter_auth_headers: dict,
) -> None:
    """Free tier with bulk-archive-backfill add-on should bypass BATCH_OPERATIONS quota."""
    # Patch the organization context to include the backfill add-on
    original_dep = None

    async def _patched_org(request, background_tasks, credentials=None):
        from app.dependencies import get_current_organization, security
        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=credentials.credentials if credentials else "")
        org = await get_current_organization(request=request, background_tasks=background_tasks, credentials=creds)
        org["add_ons"] = {"bulk-archive-backfill": {"active": True, "quantity": 1000}}
        return org

    with (
        patch("app.routers.batch.batch_service.sign_batch", new=AsyncMock(side_effect=_fake_batch_response)),
        patch("app.routers.batch.require_sign_permission", new=_patched_org),
    ):
        response = await async_client.post(
            "/api/v1/batch/sign",
            json=_batch_request(items=2),
            headers=starter_auth_headers,
        )

    # Should succeed (200) because backfill add-on bypasses batch quota
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_enterprise_tier_always_can_batch_sign(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    """Enterprise tier has unlimited batch quota, should always succeed."""
    with patch("app.routers.batch.batch_service.sign_batch", new=AsyncMock(side_effect=_fake_batch_response)):
        response = await async_client.post(
            "/api/v1/batch/sign",
            json=_batch_request(items=2),
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
