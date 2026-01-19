from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.models.response_models import VerifyVerdict


@pytest.mark.asyncio
async def test_verify_advanced_returns_verification_and_optional_merkle_outputs(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    execution = SimpleNamespace(
        is_valid=True,
        signer_id="org_business",
        manifest={"document_id": "doc_test"},
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=False,
        revocation_reason=None,
        revocation_check_status=None,
        revocation_check_error=None,
        revocation_status_list_url=None,
        revocation_bit_index=None,
        untrusted_signer=False,
        trust_status="trusted",
    )

    verdict = VerifyVerdict(
        valid=True,
        tampered=False,
        reason_code="OK",
        signer_id="org_business",
        signer_name="Business Test Organization",
        timestamp=None,
        details={"manifest": {"document_id": "doc_test"}},
        embeddings_found=0,
        all_embeddings=None,
    )

    mock_root = SimpleNamespace(
        document_id="doc_source",
        organization_id="org_business",
        root_hash="root",
        segmentation_level="sentence",
        doc_metadata={},
    )
    mock_subhash = SimpleNamespace(hash_value="deadbeef", text_content=None)

    mock_report = SimpleNamespace(
        id="rpt_1",
        target_document_id=None,
        total_segments=2,
        matched_segments=1,
        scan_timestamp="2026-01-15T00:00:00Z",
        source_documents=[
            {
                "document_id": "doc_source",
                "organization_id": "org_business",
                "segmentation_level": "sentence",
                "matched_segments": 1,
                "total_leaves": 2,
                "match_percentage": 50.0,
                "confidence_score": 0.5,
            }
        ],
        heat_map_data={
            "positions": [{"index": 0, "matched": True, "source_count": 1}],
            "total_segments": 2,
            "matched_segments": 1,
            "match_percentage": 50.0,
        },
    )

    with (
        patch("app.services.verification_logic.execute_verification", new=AsyncMock(return_value=execution)),
        patch("app.services.verification_logic.determine_reason_code", return_value="OK"),
        patch("app.services.verification_logic.build_verdict", return_value=verdict),
        patch("app.utils.quota.QuotaManager.check_quota", new=AsyncMock(return_value=True)),
        patch(
            "app.services.merkle_service.MerkleService.find_sources",
            new=AsyncMock(return_value=[(mock_subhash, mock_root)]),
        ),
        patch(
            "app.services.merkle_service.MerkleService.generate_attribution_report",
            new=AsyncMock(return_value=mock_report),
        ),
    ):
        response = await async_client.post(
            "/api/v1/verify/advanced",
            json={
                "text": "Signed content...",
                "include_attribution": True,
                "detect_plagiarism": True,
                "include_heat_map": True,
                "segmentation_level": "sentence",
                "search_scope": "organization",
            },
            headers=business_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["reason_code"] == "OK"
    assert "attribution" in payload
    assert "plagiarism" in payload


@pytest.mark.asyncio
async def test_verify_advanced_rejects_all_scope_for_non_enterprise(
    async_client: AsyncClient,
    business_auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/verify/advanced",
        json={"text": "Signed content...", "search_scope": "all"},
        headers=business_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_verify_advanced_runs_fuzzy_search_when_no_embeddings(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    execution = SimpleNamespace(
        is_valid=True,
        signer_id="org_enterprise",
        manifest={"document_id": "doc_test"},
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=False,
        revocation_reason=None,
        revocation_check_status=None,
        revocation_check_error=None,
        revocation_status_list_url=None,
        revocation_bit_index=None,
        untrusted_signer=False,
        trust_status="trusted",
    )

    verdict = VerifyVerdict(
        valid=True,
        tampered=False,
        reason_code="OK",
        signer_id="org_enterprise",
        signer_name="Enterprise Test Organization",
        timestamp=None,
        details={"manifest": {"document_id": "doc_test"}},
        embeddings_found=0,
        all_embeddings=None,
    )

    fuzzy_result = {
        "matches_found": 1,
        "matches": [{"document_id": "doc_source", "similarity": 0.92}],
        "processing_time_ms": 3,
    }

    with (
        patch("app.services.verification_logic.execute_verification", new=AsyncMock(return_value=execution)),
        patch("app.services.verification_logic.determine_reason_code", return_value="OK"),
        patch("app.services.verification_logic.build_verdict", return_value=verdict),
        patch("app.utils.quota.QuotaManager.check_quota", new=AsyncMock(return_value=True)),
        patch(
            "app.services.fuzzy_fingerprint_service.fuzzy_fingerprint_service.search",
            new=AsyncMock(return_value=fuzzy_result),
        ) as mock_search,
    ):
        response = await async_client.post(
            "/api/v1/verify/advanced",
            json={
                "text": "Unsigned content...",
                "fuzzy_search": {"enabled": True},
            },
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["fuzzy_search"]["matches_found"] == 1
    mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_advanced_returns_fuzzy_merkle_proof(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
) -> None:
    execution = SimpleNamespace(
        is_valid=True,
        signer_id="org_enterprise",
        manifest={"document_id": "doc_test"},
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=None,
        duration_ms=1,
        exception_message=None,
        document_revoked=False,
        revocation_reason=None,
        revocation_check_status=None,
        revocation_check_error=None,
        revocation_status_list_url=None,
        revocation_bit_index=None,
        untrusted_signer=False,
        trust_status="trusted",
    )

    verdict = VerifyVerdict(
        valid=True,
        tampered=False,
        reason_code="OK",
        signer_id="org_enterprise",
        signer_name="Enterprise Test Organization",
        timestamp=None,
        details={"manifest": {"document_id": "doc_test"}},
        embeddings_found=0,
        all_embeddings=None,
    )

    fuzzy_result = {
        "matches_found": 1,
        "matches": [
            {
                "document_id": "doc_source",
                "similarity": 0.92,
                "merkle_proof": {"root_hash": "root", "leaf_hash": "leaf", "proof_path": []},
            }
        ],
        "processing_time_ms": 3,
    }

    with (
        patch("app.services.verification_logic.execute_verification", new=AsyncMock(return_value=execution)),
        patch("app.services.verification_logic.determine_reason_code", return_value="OK"),
        patch("app.services.verification_logic.build_verdict", return_value=verdict),
        patch("app.utils.quota.QuotaManager.check_quota", new=AsyncMock(return_value=True)),
        patch(
            "app.services.fuzzy_fingerprint_service.fuzzy_fingerprint_service.search",
            new=AsyncMock(return_value=fuzzy_result),
        ),
    ):
        response = await async_client.post(
            "/api/v1/verify/advanced",
            json={
                "text": "Unsigned content...",
                "fuzzy_search": {"enabled": True, "include_merkle_proof": True},
            },
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    match = payload["fuzzy_search"]["matches"][0]
    assert match["merkle_proof"]["root_hash"] == "root"
