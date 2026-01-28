"""Regression tests for public signature enforcement."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot


@pytest.mark.asyncio
async def test_public_verify_rejects_signature_mismatch(async_client: AsyncClient, db: AsyncSession) -> None:
    merkle_root_id = uuid.uuid4()
    merkle_root = MerkleRoot(
        id=merkle_root_id,
        organization_id="org_demo",
        document_id="doc_signature_mismatch",
        root_hash="0" * 64,
        algorithm="sha256",
        leaf_count=1,
        tree_depth=0,
        segmentation_level="sentence",
        doc_metadata={},
    )

    ref_id_int = uuid.uuid4().int & 0xFFFFFFFF
    ref_id_hex = f"{ref_id_int:08x}"

    await db.execute(text("DELETE FROM content_references WHERE id = :id"), {"id": ref_id_int})

    reference = ContentReference(
        id=ref_id_int,
        merkle_root_id=merkle_root_id,
        leaf_hash="1" * 64,
        leaf_index=0,
        organization_id="org_demo",
        document_id="doc_signature_mismatch",
        text_preview="hello",
        signature_hash="deadbeefcafebabe",
    )

    db.add(merkle_root)
    db.add(reference)
    await db.commit()

    response = await async_client.get(f"/api/v1/public/verify/{ref_id_hex}?signature=badc0ffe")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["error"] == "Invalid signature or reference not found"
    assert payload.get("document") is None


@pytest.mark.asyncio
async def test_public_verify_accepts_matching_signature_prefix(async_client: AsyncClient, db: AsyncSession) -> None:
    merkle_root_id = uuid.uuid4()
    merkle_root = MerkleRoot(
        id=merkle_root_id,
        organization_id="org_demo",
        document_id="doc_signature_match",
        root_hash="0" * 64,
        algorithm="sha256",
        leaf_count=1,
        tree_depth=0,
        segmentation_level="sentence",
        doc_metadata={},
    )

    ref_id_int = uuid.uuid4().int & 0xFFFFFFFF
    ref_id_hex = f"{ref_id_int:08x}"

    await db.execute(text("DELETE FROM content_references WHERE id = :id"), {"id": ref_id_int})

    reference = ContentReference(
        id=ref_id_int,
        merkle_root_id=merkle_root_id,
        leaf_hash="2" * 64,
        leaf_index=0,
        organization_id="org_demo",
        document_id="doc_signature_match",
        text_preview="hello",
        signature_hash="abc12345deadbeef",
    )

    db.add(merkle_root)
    db.add(reference)
    await db.commit()

    response = await async_client.get(f"/api/v1/public/verify/{ref_id_hex}?signature=abc12345")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["document"]["document_id"] == "doc_signature_match"
    assert payload["content"]["text_preview"] is None


@pytest.mark.asyncio
async def test_public_verify_batch_enforces_signature_match(async_client: AsyncClient, db: AsyncSession) -> None:
    merkle_root_id = uuid.uuid4()
    merkle_root = MerkleRoot(
        id=merkle_root_id,
        organization_id="org_demo",
        document_id="doc_signature_batch",
        root_hash="0" * 64,
        algorithm="sha256",
        leaf_count=2,
        tree_depth=0,
        segmentation_level="sentence",
        doc_metadata={},
    )

    ref_id_valid = uuid.uuid4().int & 0xFFFFFFFF
    ref_id_invalid = uuid.uuid4().int & 0xFFFFFFFF

    await db.execute(text("DELETE FROM content_references WHERE id IN (:valid_id, :invalid_id)"), {"valid_id": ref_id_valid, "invalid_id": ref_id_invalid})

    valid_reference = ContentReference(
        id=ref_id_valid,
        merkle_root_id=merkle_root_id,
        leaf_hash="3" * 64,
        leaf_index=0,
        organization_id="org_demo",
        document_id="doc_signature_batch",
        text_preview="hello",
        signature_hash="feedfacecafebeef",
    )
    invalid_reference = ContentReference(
        id=ref_id_invalid,
        merkle_root_id=merkle_root_id,
        leaf_hash="4" * 64,
        leaf_index=1,
        organization_id="org_demo",
        document_id="doc_signature_batch",
        text_preview="world",
        signature_hash="beadfeedcafef00d",
    )

    db.add(merkle_root)
    db.add(valid_reference)
    db.add(invalid_reference)
    await db.commit()

    response = await async_client.post(
        "/api/v1/public/verify/batch",
        json={
            "references": [
                {"ref_id": f"{ref_id_valid:08x}", "signature": "feedface"},
                {"ref_id": f"{ref_id_invalid:08x}", "signature": "deadbeef"},
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["valid_count"] == 1
    assert payload["invalid_count"] == 1
    assert payload["results"][0]["valid"] is True
    assert payload["results"][0]["text_preview"] is None
    assert payload["results"][1]["valid"] is False
    assert payload["results"][1]["error"] == "Invalid signature or reference not found"
