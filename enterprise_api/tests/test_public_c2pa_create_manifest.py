import copy

import pytest
from httpx import AsyncClient

from app.middleware.public_rate_limiter import public_rate_limiter


@pytest.mark.asyncio
async def test_create_manifest_plaintext_is_compatible_with_validate_manifest(
    async_client: AsyncClient,
) -> None:
    create_response = await async_client.post(
        "/api/v1/public/c2pa/create-manifest",
        json={
            "text": "Hello world.\n\nThis is a test.",
            "document_title": "Hello Doc",
        },
        headers={"X-Forwarded-For": "203.0.113.20"},
    )

    assert create_response.status_code == 200
    create_data = create_response.json()
    assert "manifest" in create_data
    assert isinstance(create_data["manifest"], dict)

    validate_response = await async_client.post(
        "/api/v1/public/c2pa/validate-manifest",
        json={"manifest": create_data["manifest"]},
        headers={"X-Forwarded-For": "203.0.113.20"},
    )

    assert validate_response.status_code == 200
    validate_data = validate_response.json()
    assert validate_data["valid"] is True


@pytest.mark.asyncio
async def test_create_manifest_txt_filename(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/public/c2pa/create-manifest",
        json={
            "text": "Hello from a .txt file",
            "filename": "example.txt",
        },
        headers={"X-Forwarded-For": "203.0.113.21"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["manifest"]["claim_generator"]
    assert isinstance(data["manifest"].get("assertions"), list)


@pytest.mark.asyncio
async def test_create_manifest_anonymous_rate_limited(async_client: AsyncClient) -> None:
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["c2pa_create_manifest"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("203.0.113.22")

        first = await async_client.post(
            "/api/v1/public/c2pa/create-manifest",
            json={"text": "Hello"},
            headers={"X-Forwarded-For": "203.0.113.22"},
        )
        assert first.status_code == 200

        second = await async_client.post(
            "/api/v1/public/c2pa/create-manifest",
            json={"text": "Hello again"},
            headers={"X-Forwarded-For": "203.0.113.22"},
        )
        assert second.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("203.0.113.22")


@pytest.mark.asyncio
async def test_create_manifest_authenticated_bypasses_public_rate_limit(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["c2pa_create_manifest"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("203.0.113.23")

        headers = {**auth_headers, "X-Forwarded-For": "203.0.113.23"}

        first = await async_client.post(
            "/api/v1/public/c2pa/create-manifest",
            json={"text": "Hello"},
            headers=headers,
        )
        assert first.status_code == 200

        second = await async_client.post(
            "/api/v1/public/c2pa/create-manifest",
            json={"text": "Hello again"},
            headers=headers,
        )
        assert second.status_code == 200
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("203.0.113.23")


@pytest.mark.asyncio
async def test_create_manifest_output_works_with_sign_and_verify(
    async_client: AsyncClient,
    auth_headers: dict,
) -> None:
    text = "Hello world. This will be signed."

    create_response = await async_client.post(
        "/api/v1/public/c2pa/create-manifest",
        json={"text": text, "document_title": "Compat Test"},
        headers={"X-Forwarded-For": "203.0.113.24"},
    )
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert "signing" in create_data
    assert "claim_generator" in create_data["signing"]

    sign_payload = {
        "text": text,
        "document_title": "Compat Test",
        "claim_generator": create_data["signing"]["claim_generator"],
        "actions": create_data["signing"].get("actions"),
    }

    sign_response = await async_client.post(
        "/api/v1/sign",
        json=sign_payload,
        headers=auth_headers,
    )
    assert sign_response.status_code == 200
    sign_data = sign_response.json()
    assert sign_data["success"] is True
    assert isinstance(sign_data.get("signed_text"), str) and sign_data["signed_text"]

    verify_response = await async_client.post(
        "/api/v1/verify",
        json={"text": sign_data["signed_text"]},
    )
    assert verify_response.status_code == 200
    verify_data = verify_response.json()
    assert verify_data["success"] is True
    assert verify_data["data"]["valid"] is True


@pytest.mark.asyncio
async def test_create_manifest_rejects_large_payload(async_client: AsyncClient) -> None:
    oversized_text = "a" * (256 * 1024 + 1)

    response = await async_client.post(
        "/api/v1/public/c2pa/create-manifest",
        json={"text": oversized_text},
        headers={"X-Forwarded-For": "203.0.113.25"},
    )

    assert response.status_code == 413
