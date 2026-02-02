from __future__ import annotations

import uuid

import pytest


def _unique_document_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _assert_status(response, expected_status: int, label: str) -> None:
    assert response.status_code == expected_status, (
        f"{label} expected {expected_status}, got {response.status_code}. "
        f"Body: {response.text}. Headers: {dict(response.headers)}"
    )


def _assert_local_base_url(base_url: str) -> None:
    allowed_prefixes = ("http://localhost", "http://127.0.0.1", "http://0.0.0.0")
    assert base_url.startswith(allowed_prefixes), (
        "Local tests should target a local API base URL. "
        f"Got {base_url}"
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_sign_and_verify(local_client, local_auth_headers, local_api_config) -> None:
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_sign")
    original_text = "Local API verification test. This is a signed payload."

    sign_response = await local_client.post(
        "/api/v1/sign",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "document_title": "Local API Test",
            "document_type": "article",
        },
    )

    _assert_status(sign_response, 200, "POST /api/v1/sign")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True
    assert sign_payload["document_id"] == document_id
    signed_text = sign_payload["signed_text"]
    assert isinstance(signed_text, str)
    assert original_text in signed_text

    verify_response = await local_client.post(
        "/api/v1/verify",
        headers=local_auth_headers,
        json={"text": signed_text},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        "Verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Details: {verify_payload['data'].get('details')}. "
        f"Full Response: {verify_payload}"
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_local_sign_advanced_and_verify_advanced(local_client, local_auth_headers, local_api_config) -> None:
    _assert_local_base_url(local_api_config.base_url)
    document_id = _unique_document_id("local_adv")
    original_text = "Local advanced signing test. Confirm advanced verify works."

    advanced_response = await local_client.post(
        "/api/v1/sign/advanced",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "manifest_mode": "minimal_uuid",
            "segmentation_level": "sentence",
            "embedding_strategy": "single_point",
        },
    )

    _assert_status(advanced_response, 201, "POST /api/v1/sign/advanced")
    advanced_payload = advanced_response.json()
    assert advanced_payload["success"] is True
    assert advanced_payload["document_id"] == document_id
    embedded_content = advanced_payload.get("embedded_content")
    assert isinstance(embedded_content, str)

    verify_response = await local_client.post(
        "/api/v1/verify/advanced",
        headers=local_auth_headers,
        json={
            "text": embedded_content,
            "include_attribution": False,
            "detect_plagiarism": False,
            "segmentation_level": "sentence",
            "search_scope": "organization",
        },
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify/advanced")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        "Verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Details: {verify_payload['data'].get('details')}"
    )
