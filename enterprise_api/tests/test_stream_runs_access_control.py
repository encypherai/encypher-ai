from __future__ import annotations

import logging

import pytest
from httpx import AsyncClient

from app.services.session_service import session_service

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_stream_runs_requires_auth(async_client: AsyncClient) -> None:
    logger.info("step=setup run_id")
    run_id = "run_test_requires_auth"
    logger.info("step=save_stream_state run_id=%s", run_id)
    await session_service.save_stream_state(
        run_id,
        {
            "organization_id": "org_business",
            "signed_text": "secret",
        },
    )

    try:
        logger.info("step=request unauth GET /api/v1/sign/stream/runs/{run_id}")
        resp = await async_client.get(f"/api/v1/sign/stream/runs/{run_id}")
        logger.info("step=response status=%s", resp.status_code)
        assert resp.status_code == 401
    finally:
        logger.info("step=cleanup delete_stream_state run_id=%s", run_id)
        await session_service.delete_stream_state(run_id)


@pytest.mark.asyncio
async def test_stream_events_requires_auth(async_client: AsyncClient) -> None:
    logger.info("step=request unauth GET /api/v1/sign/stream/sessions/{session_id}/events initial_only=true")
    resp = await async_client.get(
        "/api/v1/sign/stream/sessions/session_test_requires_auth/events",
        params={"initial_only": True},
    )
    logger.info("step=response status=%s", resp.status_code)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_stream_events_allows_authenticated_stream(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    logger.info("step=request auth GET /api/v1/sign/stream/sessions/{session_id}/events initial_only=true")
    resp = await async_client.get(
        "/api/v1/sign/stream/sessions/session_test_allows_auth/events",
        params={"initial_only": True},
        headers=business_auth_headers,
    )
    logger.info("step=response status=%s", resp.status_code)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert "event: connected" in resp.text


@pytest.mark.asyncio
async def test_stream_runs_requires_matching_org(
    async_client: AsyncClient,
    business_auth_headers: dict,
    enterprise_auth_headers: dict,
) -> None:
    logger.info("step=setup run_id")
    run_id = "run_test_requires_matching_org"
    logger.info("step=save_stream_state run_id=%s", run_id)
    await session_service.save_stream_state(
        run_id,
        {
            "organization_id": "org_business",
            "signed_text": "secret",
        },
    )

    try:
        logger.info("step=request allowed org GET /api/v1/sign/stream/runs/{run_id}")
        allowed = await async_client.get(
            f"/api/v1/sign/stream/runs/{run_id}",
            headers=business_auth_headers,
        )
        logger.info("step=response allowed status=%s", allowed.status_code)
        assert allowed.status_code == 200
        payload = allowed.json()
        assert payload["run_id"] == run_id
        assert payload["state"]["signed_text"] == "secret"

        logger.info("step=request denied org GET /api/v1/sign/stream/runs/{run_id}")
        denied = await async_client.get(
            f"/api/v1/sign/stream/runs/{run_id}",
            headers=enterprise_auth_headers,
        )
        logger.info("step=response denied status=%s", denied.status_code)
        assert denied.status_code == 404
    finally:
        logger.info("step=cleanup delete_stream_state run_id=%s", run_id)
        await session_service.delete_stream_state(run_id)
