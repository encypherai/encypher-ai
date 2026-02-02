from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest


def _unique_document_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _assert_status(response, expected_status: int, label: str) -> None:
    assert response.status_code == expected_status, (
        f"{label} expected {expected_status}, got {response.status_code}. "
        f"Body: {response.text}. Headers: {dict(response.headers)}"
    )


async def _sign_basic(live_client, live_auth_headers, label: str, payload_overrides: dict) -> dict:
    document_id = _unique_document_id(f"live_basic_{label}")
    base_payload = {
        "document_id": document_id,
        "text": f"Live matrix sign test ({label}) - {uuid.uuid4().hex}",
        "document_title": f"Live Matrix {label}",
        "document_type": "article",
    }
    base_payload.update(payload_overrides)

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json=base_payload,
    )

    _assert_status(sign_response, 200, f"POST /api/v1/sign ({label})")
    payload = sign_response.json()
    assert payload["success"] is True
    assert payload["document_id"] == document_id
    assert isinstance(payload.get("signed_text"), str)
    return payload


async def _verify_basic(live_client, live_auth_headers, signed_text: str, label: str) -> dict:
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": signed_text},
    )

    _assert_status(verify_response, 200, f"POST /api/v1/verify ({label})")
    payload = verify_response.json()
    assert payload["success"] is True
    assert payload["data"]["valid"] is True, (
        "Verification failed. "
        f"Reason: {payload['data'].get('reason_code')}. "
        f"Details: {payload['data'].get('details')}. "
        f"Full Response: {payload}"
    )
    return payload


async def _sign_advanced(live_client, live_auth_headers, label: str, payload_overrides: dict) -> dict:
    document_id = _unique_document_id(f"live_adv_{label}")
    base_payload = {
        "document_id": document_id,
        "text": f"Live advanced matrix test ({label}) - {uuid.uuid4().hex}",
        "manifest_mode": "full",
        "segmentation_level": "sentence",
        "segmentation_levels": ["sentence", "paragraph"],
        "embedding_strategy": "single_point",
        "index_for_attribution": True,
    }
    base_payload.update(payload_overrides)

    response = await live_client.post(
        "/api/v1/sign/advanced",
        headers=live_auth_headers,
        json=base_payload,
    )

    _assert_status(response, 201, f"POST /api/v1/sign/advanced ({label})")
    payload = response.json()
    assert payload["success"] is True
    assert payload["document_id"] == document_id
    assert isinstance(payload.get("embedded_content"), str)
    return payload


async def _verify_advanced(
    live_client,
    live_auth_headers,
    label: str,
    text: str,
    payload_overrides: dict,
) -> dict:
    payload = {
        "text": text,
        "include_attribution": False,
        "detect_plagiarism": False,
        "segmentation_level": "sentence",
        "search_scope": "organization",
    }
    payload.update(payload_overrides)

    response = await live_client.post(
        "/api/v1/verify/advanced",
        headers=live_auth_headers,
        json=payload,
    )

    _assert_status(response, 200, f"POST /api/v1/verify/advanced ({label})")
    response_payload = response.json()
    assert response_payload["success"] is True
    assert response_payload["data"]["valid"] is True, (
        "Verification failed. "
        f"Reason: {response_payload['data'].get('reason_code')}. "
        f"Details: {response_payload['data'].get('details')}"
    )
    return response_payload


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_sign_option_matrix(live_client, live_auth_headers, live_api_config) -> None:
    assert live_api_config.base_url.startswith("https://api.encypherai.com"), (
        f"Live tests should target production api. Got {live_api_config.base_url}"
    )

    timestamp = datetime.now(timezone.utc).isoformat()
    actions = [
        {
            "label": "c2pa.created",
            "when": timestamp,
            "softwareAgent": "Encypher Matrix",
        }
    ]
    custom_assertions = [
        {
            "label": "c2pa.training-mining.v1",
            "data": {
                "use": {"ai_training": False, "ai_inference": True, "data_mining": False},
                "constraint_info": {"license": "Matrix"},
            },
        }
    ]

    cases = [
        (
            "article_defaults",
            {
                "document_type": "article",
                "document_title": "Matrix Article",
                "document_url": "https://example.com/matrix/article",
                "claim_generator": "encypherai/matrix-test",
            },
        ),
        (
            "legal_brief_rights",
            {
                "document_type": "legal_brief",
                "rights": {
                    "copyright_holder": "Matrix Publisher",
                    "license_url": "https://example.com/license",
                    "usage_terms": "RAG allowed with attribution",
                    "syndication_allowed": True,
                    "contact_email": "licensing@example.com",
                },
            },
        ),
        (
            "contract_template",
            {
                "document_type": "contract",
                "template_id": "tmpl_builtin_all_rights_reserved_v1",
                "validate_assertions": True,
            },
        ),
        (
            "ai_output_custom",
            {
                "document_type": "ai_output",
                "actions": actions,
                "custom_assertions": custom_assertions,
            },
        ),
    ]

    failures: list[str] = []
    for label, overrides in cases:
        try:
            sign_payload = await _sign_basic(live_client, live_auth_headers, label, overrides)
            await _verify_basic(live_client, live_auth_headers, sign_payload["signed_text"], label)
        except Exception as exc:  # pragma: no cover - network failure aggregation
            failures.append(f"{label}: {exc}")

    if failures:
        pytest.fail("\n".join(failures))


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_sign_advanced_option_matrix(live_client, live_auth_headers, live_api_config) -> None:
    assert live_api_config.base_url.startswith("https://api.encypherai.com"), (
        f"Live tests should target production api. Got {live_api_config.base_url}"
    )

    failures: list[str] = []
    baseline_payload = None
    try:
        baseline_payload = await _sign_advanced(
            live_client,
            live_auth_headers,
            "full_single_point",
            {
                "manifest_mode": "full",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
                "license": {
                    "type": "CC-BY-4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0/",
                    "contact_email": "licensing@example.com",
                },
            },
        )
        await _verify_advanced(
            live_client,
            live_auth_headers,
            "full_single_point",
            baseline_payload["embedded_content"],
            {"segmentation_level": "sentence", "search_scope": "organization"},
        )
    except Exception as exc:  # pragma: no cover - network failure aggregation
        failures.append(f"full_single_point: {exc}")

    instance_id = None
    metadata = (baseline_payload or {}).get("metadata") or {}
    if isinstance(metadata, dict):
        instance_id = metadata.get("instance_id")

    if instance_id:
        try:
            edited_payload = await _sign_advanced(
                live_client,
                live_auth_headers,
                "edited_instance",
                {
                    "manifest_mode": "full",
                    "action": "c2pa.edited",
                    "previous_instance_id": instance_id,
                    "segmentation_level": "sentence",
                },
            )
            await _verify_advanced(
                live_client,
                live_auth_headers,
                "edited_instance",
                edited_payload["embedded_content"],
                {"segmentation_level": "sentence", "search_scope": "organization"},
            )
        except Exception as exc:  # pragma: no cover - network failure aggregation
            failures.append(f"edited_instance: {exc}")

    advanced_cases = [
        (
            "lightweight_uuid",
            {
                "manifest_mode": "lightweight_uuid",
                "segmentation_level": "paragraph",
                "segmentation_levels": ["paragraph"],
                "embedding_strategy": "single_point",
                "embedding_options": {"format": "plain", "method": "comment", "include_text": True},
            },
            {"segmentation_level": "paragraph", "search_scope": "organization"},
        ),
        (
            "minimal_uuid_disable_c2pa",
            {
                "manifest_mode": "minimal_uuid",
                "disable_c2pa": True,
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence"],
                "index_for_attribution": False,
            },
            None,
        ),
        (
            "distributed_whitespace",
            {
                "manifest_mode": "minimal_uuid",
                "embedding_strategy": "distributed",
                "distribution_target": "whitespace",
                "add_dual_binding": True,
                "segmentation_level": "sentence",
            },
            {"segmentation_level": "sentence", "search_scope": "organization"},
        ),
        (
            "distributed_all_chars",
            {
                "manifest_mode": "minimal_uuid",
                "embedding_strategy": "distributed",
                "distribution_target": "all_chars",
                "segmentation_level": "paragraph",
                "segmentation_levels": ["paragraph"],
            },
            {"segmentation_level": "paragraph", "search_scope": "organization"},
        ),
        (
            "hybrid_redundant",
            {
                "manifest_mode": "hybrid",
                "embedding_strategy": "distributed_redundant",
                "distribution_target": "punctuation",
                "segmentation_level": "section",
                "segmentation_levels": ["section"],
            },
            {"segmentation_level": "section", "search_scope": "organization"},
        ),
    ]

    for label, sign_overrides, verify_overrides in advanced_cases:
        try:
            payload = await _sign_advanced(live_client, live_auth_headers, label, sign_overrides)
            if label == "minimal_uuid_disable_c2pa":
                assert (payload.get("metadata") or {}).get("instance_id") is None
                continue
            if verify_overrides is not None:
                await _verify_advanced(
                    live_client,
                    live_auth_headers,
                    label,
                    payload["embedded_content"],
                    verify_overrides,
                )
        except Exception as exc:  # pragma: no cover - network failure aggregation
            failures.append(f"{label}: {exc}")

    if failures:
        pytest.fail("\n".join(failures))


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_verify_advanced_option_matrix(live_client, live_auth_headers, live_api_config) -> None:
    assert live_api_config.base_url.startswith("https://api.encypherai.com"), (
        f"Live tests should target production api. Got {live_api_config.base_url}"
    )

    failures: list[str] = []
    signed_payload = None
    try:
        signed_payload = await _sign_advanced(
            live_client,
            live_auth_headers,
            "verify_matrix",
            {
                "manifest_mode": "full",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
            },
        )
    except Exception as exc:  # pragma: no cover - network failure aggregation
        failures.append(f"verify_matrix_sign: {exc}")

    if not signed_payload:
        pytest.fail("\n".join(failures))
        return

    text = signed_payload["embedded_content"]

    verify_cases = [
        (
            "baseline",
            {"segmentation_level": "sentence", "search_scope": "organization"},
        ),
        (
            "attribution",
            {"include_attribution": True, "segmentation_level": "sentence"},
        ),
        (
            "plagiarism",
            {
                "detect_plagiarism": True,
                "include_heat_map": True,
                "min_match_percentage": 0.0,
                "segmentation_level": "sentence",
            },
        ),
        (
            "scope_public",
            {"search_scope": "public", "segmentation_level": "sentence"},
        ),
        (
            "scope_all",
            {"search_scope": "all", "segmentation_level": "sentence"},
        ),
        (
            "segmentation_paragraph",
            {"segmentation_level": "paragraph", "search_scope": "organization"},
        ),
        (
            "fuzzy_search",
            {
                "segmentation_level": "sentence",
                "search_scope": "organization",
                "fuzzy_search": {
                    "enabled": True,
                    "algorithm": "simhash",
                    "levels": ["sentence"],
                    "similarity_threshold": 0.8,
                    "max_candidates": 5,
                    "include_merkle_proof": True,
                    "fallback_when_no_binding": False,
                },
            },
        ),
    ]

    for label, overrides in verify_cases:
        try:
            response_payload = await _verify_advanced(
                live_client,
                live_auth_headers,
                label,
                text,
                overrides,
            )
            if overrides.get("include_attribution"):
                assert "attribution" in response_payload
            if overrides.get("detect_plagiarism"):
                assert "plagiarism" in response_payload
            if overrides.get("fuzzy_search"):
                assert "fuzzy_search" in response_payload
        except Exception as exc:  # pragma: no cover - network failure aggregation
            failures.append(f"{label}: {exc}")

    if failures:
        pytest.fail("\n".join(failures))
