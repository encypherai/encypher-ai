from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


def _multi_extract_result(*, total_found: int, signer_ids: list[str]):
    return SimpleNamespace(
        total_found=total_found,
        embeddings=[SimpleNamespace(signer_id=signer_id) for signer_id in signer_ids],
    )


def _verified_result(*, embeddings: list[SimpleNamespace]):
    valid_count = sum(1 for emb in embeddings if emb.signature_valid)
    return SimpleNamespace(
        total_found=len(embeddings),
        embeddings=embeddings,
        all_valid=valid_count == len(embeddings),
        any_valid=valid_count > 0,
    )


@pytest.mark.asyncio
async def test_verify_scans_multiple_embeddings_all_valid(async_client: AsyncClient) -> None:
    extract_result = _multi_extract_result(total_found=2, signer_ids=["org_demo", "org_business"])
    verified_result = _verified_result(
        embeddings=[
            SimpleNamespace(
                index=0,
                signature_valid=True,
                metadata={"manifest": {"document_id": "doc-1"}},
                signer_id="org_demo",
                signer_name="Demo Org",
                span=(0, 10),
                segment_text="segment-one",
            ),
            SimpleNamespace(
                index=1,
                signature_valid=True,
                metadata={"manifest": {"document_id": "doc-2"}},
                signer_id="org_business",
                signer_name="Business Org",
                span=(11, 20),
                segment_text="segment-two",
            ),
        ]
    )

    with (
        patch("app.routers.verification.public_rate_limiter", new=AsyncMock(return_value={})),
        patch("app.routers.verification.extract_all_embeddings", return_value=extract_result),
        patch(
            "app.routers.verification.extract_and_verify_all_embeddings",
            new=AsyncMock(return_value=verified_result),
        ),
        patch("app.routers.verification.load_organization_public_key", new=AsyncMock(return_value=object())),
    ):
        response = await async_client.post(
            "/api/v1/verify",
            json={"text": "payload"},
            headers={"X-Forwarded-For": "203.0.113.200"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["embeddings_found"] == 2
    assert data["valid"] is True
    assert data["reason_code"] == "VERIFIED"
    assert len(data["all_embeddings"]) == 2
    assert data["all_embeddings"][0]["index"] == 0
    assert data["all_embeddings"][0]["valid"] is True


@pytest.mark.asyncio
async def test_verify_scans_multiple_embeddings_partial_valid(async_client: AsyncClient) -> None:
    extract_result = _multi_extract_result(total_found=2, signer_ids=["org_demo", "org_business"])
    verified_result = _verified_result(
        embeddings=[
            SimpleNamespace(
                index=0,
                signature_valid=True,
                metadata={"manifest": {"document_id": "doc-1"}},
                signer_id="org_demo",
                signer_name="Demo Org",
                span=(0, 10),
                segment_text="segment-one",
            ),
            SimpleNamespace(
                index=1,
                signature_valid=False,
                metadata={"manifest": {"document_id": "doc-2"}},
                signer_id="org_business",
                signer_name="Business Org",
                span=(11, 20),
                segment_text="segment-two",
            ),
        ]
    )

    with (
        patch("app.routers.verification.public_rate_limiter", new=AsyncMock(return_value={})),
        patch("app.routers.verification.extract_all_embeddings", return_value=extract_result),
        patch(
            "app.routers.verification.extract_and_verify_all_embeddings",
            new=AsyncMock(return_value=verified_result),
        ),
        patch("app.routers.verification.load_organization_public_key", new=AsyncMock(return_value=object())),
    ):
        response = await async_client.post(
            "/api/v1/verify",
            json={"text": "payload"},
            headers={"X-Forwarded-For": "203.0.113.201"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["embeddings_found"] == 2
    assert data["valid"] is False
    assert data["reason_code"] == "PARTIAL_VERIFICATION"
    assert "warning" in data["details"]
    assert len(data["all_embeddings"]) == 2
    assert data["all_embeddings"][1]["valid"] is False
    assert data["all_embeddings"][1]["tampered"] is True
