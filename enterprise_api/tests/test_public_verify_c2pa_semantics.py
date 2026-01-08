import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot
from app.utils.c2pa_verifier import C2PAVerificationResult


@pytest.mark.asyncio
async def test_public_verify_c2pa_is_validation_only(async_client: AsyncClient, db: AsyncSession) -> None:
    merkle_root_id = uuid.uuid4()

    merkle_root = MerkleRoot(
        id=merkle_root_id,
        organization_id="org_demo",
        document_id="doc_c2pa_semantics",
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
        document_id="doc_c2pa_semantics",
        text_preview="hello",
        signature_hash="2" * 64,
        c2pa_manifest_url="https://example.com/manifest.json",
        c2pa_manifest_hash=None,
    )

    db.add(merkle_root)
    db.add(reference)
    await db.commit()

    result = C2PAVerificationResult(
        valid=True,
        manifest_url="https://example.com/manifest.json",
        manifest_hash="abc",
        assertions=[],
        signatures=[],
        errors=[],
        warnings=[],
    )

    with patch("app.api.v1.public.verify.c2pa_verifier.verify_manifest_url", return_value=result):
        response = await async_client.get(f"/api/v1/public/verify/{ref_id_hex}?signature=aaaaaaaa")

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True

    c2pa = payload.get("c2pa")
    assert isinstance(c2pa, dict)

    assert "verified" not in c2pa
    assert c2pa["validated"] is True
    assert c2pa["validation_type"] == "non_cryptographic"
