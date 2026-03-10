from __future__ import annotations

import uuid

import pytest


def _unique_document_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _assert_status(response, expected_status: int | tuple[int, ...], label: str) -> None:
    allowed = expected_status if isinstance(expected_status, tuple) else (expected_status,)
    assert (
        response.status_code in allowed
    ), f"{label} expected one of {allowed}, got {response.status_code}. Body: {response.text}. Headers: {dict(response.headers)}"


def _extract_document_payload(payload: dict) -> dict:
    document_payload = payload.get("data", {}).get("document")
    if isinstance(document_payload, dict):
        return document_payload
    return payload


def _extract_signed_text(payload: dict) -> str:
    document_payload = _extract_document_payload(payload)
    signed_text = document_payload.get("signed_text") or document_payload.get("embedded_content")
    assert isinstance(signed_text, str) and signed_text, f"Expected signed text in response payload, got: {payload}"
    return signed_text


def _assert_local_base_url(base_url: str) -> None:
    allowed_prefixes = ("http://localhost", "http://127.0.0.1", "http://0.0.0.0")
    assert base_url.startswith(allowed_prefixes), f"Local tests should target a local API base URL. Got {base_url}"


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

    _assert_status(sign_response, (200, 201), "POST /api/v1/sign")
    sign_payload = sign_response.json()
    sign_document = _extract_document_payload(sign_payload)
    assert sign_payload["success"] is True
    assert sign_document.get("document_id") == document_id
    signed_text = _extract_signed_text(sign_payload)
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
        "/api/v1/sign",
        headers=local_auth_headers,
        json={
            "document_id": document_id,
            "text": original_text,
            "options": {
                "manifest_mode": "micro",
                "segmentation_level": "sentence",
                "embedding_strategy": "single_point",
            },
        },
    )

    _assert_status(advanced_response, (200, 201), "POST /api/v1/sign")
    advanced_payload = advanced_response.json()
    advanced_document = _extract_document_payload(advanced_payload)
    assert advanced_payload["success"] is True
    assert advanced_document.get("document_id") == document_id
    signed_text = _extract_signed_text(advanced_payload)

    verify_response = await local_client.post(
        "/api/v1/verify/advanced",
        headers=local_auth_headers,
        json={
            "text": signed_text,
            "include_attribution": False,
            "detect_plagiarism": False,
            "segmentation_level": "sentence",
            "search_scope": "organization",
        },
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify/advanced")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert (
        verify_payload["data"]["valid"] is True
    ), f"Verification failed. Reason: {verify_payload['data'].get('reason_code')}. Details: {verify_payload['data'].get('details')}"
