from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.crud import merkle as merkle_crud
from app.models.response_models import VerifyVerdict
from app.utils.merkle import MerkleTree
from app.utils.segmentation import HierarchicalSegmenter


async def _seed_merkle_root(
    *,
    content_db,
    organization_id: str,
    document_id: str,
    text: str,
    segmentation_level: str = "sentence",
) -> None:
    segmenter = HierarchicalSegmenter(text, include_words=False)
    segments = segmenter.get_segments(segmentation_level)
    tree = MerkleTree(segments, segmentation_level=segmentation_level)

    root = await merkle_crud.create_merkle_root(
        db=content_db,
        organization_id=organization_id,
        document_id=document_id,
        root_hash=tree.root.hash,
        tree_depth=tree.tree_depth,
        leaf_count=tree.total_leaves,
        segmentation_level=segmentation_level,
        metadata={},
    )

    subhashes_data = []
    for node in tree.leaves:
        subhashes_data.append(
            {
                "hash_value": node.hash,
                "root_id": root.id,
                "node_type": "leaf",
                "depth_level": node.depth,
                "position_index": node.position,
                "parent_hash": None,
                "left_child_hash": None,
                "right_child_hash": None,
                "text_content": None,
                "segment_metadata": node.metadata,
            }
        )

    await merkle_crud.bulk_create_merkle_subhashes(content_db, subhashes_data)


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

    scan_timestamp = datetime.now(timezone.utc)
    mock_report = SimpleNamespace(
        id="rpt_1",
        target_document_id=None,
        total_segments=2,
        matched_segments=1,
        scan_timestamp=scan_timestamp,
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
    assert payload["attribution"]["query_preview"] == "Signed content..."[:200]
    assert "text_content" not in payload["attribution"]["sources"][0]
    assert payload["plagiarism"]["scan_timestamp"] == scan_timestamp.isoformat()


@pytest.mark.asyncio
async def test_verify_advanced_reports_tamper_detection_and_localization(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
    content_db,
) -> None:
    text = "First sentence. Second sentence."
    document_id = "doc_tamper_match"
    await _seed_merkle_root(
        content_db=content_db,
        organization_id="org_enterprise",
        document_id=document_id,
        text=text,
    )

    execution = SimpleNamespace(
        is_valid=True,
        signer_id="org_enterprise",
        manifest={"custom_metadata": {"document_id": document_id, "organization_id": "org_enterprise"}},
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
        details={"manifest": {"document_id": document_id}},
        embeddings_found=0,
        all_embeddings=None,
    )

    with (
        patch("app.services.verification_logic.execute_verification", new=AsyncMock(return_value=execution)),
        patch("app.services.verification_logic.determine_reason_code", return_value="OK"),
        patch("app.services.verification_logic.build_verdict", return_value=verdict),
    ):
        response = await async_client.post(
            "/api/v1/verify/advanced",
            json={"text": text, "segmentation_level": "sentence"},
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tamper_detection"]["status"] == "computed"
    assert payload["tamper_detection"]["root_match"] is True
    assert payload["tamper_localization"]["counts"] == {"changed": 0, "inserted": 0, "deleted": 0}
    assert payload["tamper_localization"]["events"] == []


@pytest.mark.asyncio
async def test_verify_advanced_localization_detects_changes(
    async_client: AsyncClient,
    enterprise_auth_headers: dict,
    content_db,
) -> None:
    stored_text = "First sentence. Second sentence."
    tampered_text = "First sentence. Altered sentence."
    document_id = "doc_tamper_changed"
    await _seed_merkle_root(
        content_db=content_db,
        organization_id="org_enterprise",
        document_id=document_id,
        text=stored_text,
    )

    execution = SimpleNamespace(
        is_valid=True,
        signer_id="org_enterprise",
        manifest={"custom_metadata": {"document_id": document_id, "organization_id": "org_enterprise"}},
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
        valid=False,
        tampered=True,
        reason_code="SIGNATURE_INVALID",
        signer_id="org_enterprise",
        signer_name="Enterprise Test Organization",
        timestamp=None,
        details={"manifest": {"document_id": document_id}},
        embeddings_found=0,
        all_embeddings=None,
    )

    with (
        patch("app.services.verification_logic.execute_verification", new=AsyncMock(return_value=execution)),
        patch("app.services.verification_logic.determine_reason_code", return_value="SIGNATURE_INVALID"),
        patch("app.services.verification_logic.build_verdict", return_value=verdict),
    ):
        response = await async_client.post(
            "/api/v1/verify/advanced",
            json={"text": tampered_text, "segmentation_level": "sentence"},
            headers=enterprise_auth_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tamper_detection"]["root_match"] is False
    assert payload["tamper_localization"]["counts"]["changed"] > 0
    previews = [preview for event in payload["tamper_localization"]["events"] for preview in event.get("request_previews", [])]
    assert any("Altered sentence" in preview for preview in previews)


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
    assert payload["soft_match"] == payload["fuzzy_search"]
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
