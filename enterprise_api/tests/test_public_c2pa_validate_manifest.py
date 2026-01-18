# Tests for public C2PA manifest validation endpoint.
#
# Endpoint: POST /api/v1/public/c2pa/validate-manifest
#
# Behavior:
# - Anonymous requests are allowed but strictly IP rate-limited
# - Requests with a valid API key bypass the public rate limiter
# - Endpoint validates manifest structure and assertion payloads (non-cryptographic)

import copy
import pytest
from httpx import AsyncClient
from app.middleware.public_rate_limiter import public_rate_limiter


def _valid_manifest_payload() -> dict:
    return {
        "manifest": {
            "claim_generator": "encypher-tests",
            "assertions": [
                {
                    "label": "c2pa.location.v1",
                    "data": {"latitude": 37.0, "longitude": -122.0},
                }
            ],
        }
    }


@pytest.mark.asyncio
async def test_validate_manifest_anonymous_valid(async_client: AsyncClient) -> None:
    payload = _valid_manifest_payload()

    response = await async_client.post(
        "/api/v1/public/c2pa/validate-manifest",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.10"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["errors"] == []
    assert isinstance(data["assertions"], list)
    assert data["assertions"][0]["label"] == "c2pa.location.v1"


@pytest.mark.asyncio
async def test_validate_manifest_missing_required_field(async_client: AsyncClient) -> None:
    payload = _valid_manifest_payload()
    del payload["manifest"]["claim_generator"]

    response = await async_client.post(
        "/api/v1/public/c2pa/validate-manifest",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.11"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("claim_generator" in e for e in data["errors"])


@pytest.mark.asyncio
async def test_validate_manifest_custom_schema_validation(async_client: AsyncClient) -> None:
    payload = {
        "manifest": {
            "claim_generator": "encypher-tests",
            "assertions": [
                {
                    "label": "com.example.custom.v1",
                    "data": {"x": 1},
                }
            ],
        },
        "schemas": {
            "com.example.custom.v1": {
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            }
        },
    }

    response = await async_client.post(
        "/api/v1/public/c2pa/validate-manifest",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.12"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["assertions"][0]["valid"] is True


@pytest.mark.asyncio
async def test_validate_manifest_anonymous_rate_limited(async_client: AsyncClient) -> None:
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["c2pa_validate_manifest"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("203.0.113.13")

        payload = _valid_manifest_payload()
        first = await async_client.post(
            "/api/v1/public/c2pa/validate-manifest",
            json=payload,
            headers={"X-Forwarded-For": "203.0.113.13"},
        )
        assert first.status_code == 200

        second = await async_client.post(
            "/api/v1/public/c2pa/validate-manifest",
            json=payload,
            headers={"X-Forwarded-For": "203.0.113.13"},
        )
        assert second.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("203.0.113.13")


@pytest.mark.asyncio
async def test_validate_manifest_authenticated_bypasses_public_rate_limit(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["c2pa_validate_manifest"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("203.0.113.14")

        payload = _valid_manifest_payload()
        headers = {**auth_headers, "X-Forwarded-For": "203.0.113.14"}

        first = await async_client.post(
            "/api/v1/public/c2pa/validate-manifest",
            json=payload,
            headers=headers,
        )
        assert first.status_code == 200

        second = await async_client.post(
            "/api/v1/public/c2pa/validate-manifest",
            json=payload,
            headers=headers,
        )
        assert second.status_code == 200
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("203.0.113.14")
