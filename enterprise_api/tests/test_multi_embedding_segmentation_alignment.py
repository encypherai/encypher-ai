from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

from app.utils.merkle.hashing import compute_leaf_hash
from app.utils.multi_embedding import extract_and_verify_all_embeddings


@pytest.mark.asyncio
async def test_multi_embedding_verification_matches_sentence_segmentation() -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_demo"

    segments = ["Hello world.", "Second sentence."]

    embedded_segments: list[str] = []
    for idx, segment in enumerate(segments):
        embedded_segments.append(
            UnicodeMetadata.embed_metadata(
                text=segment,
                private_key=private_key,
                signer_id=signer_id,
                metadata_format="basic",
                target=MetadataTarget.WHITESPACE,
                add_hard_binding=False,
                custom_metadata={
                    "leaf_index": idx,
                    "leaf_hash": compute_leaf_hash(segment),
                },
            )
        )

    full_doc = " ".join(embedded_segments)
    signed_doc = UnicodeMetadata.embed_metadata(
        text=full_doc,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
        add_hard_binding=True,
    )

    def resolver(_sid: str) -> Ed25519PublicKey:
        return public_key

    result = await extract_and_verify_all_embeddings(
        signed_doc,
        resolver,
        demo_signer_ids={signer_id},
    )

    assert result.total_found == 3

    basic_embeddings = [e for e in result.embeddings if e.embedding_type == "basic"]
    assert len(basic_embeddings) == 2

    for emb in basic_embeddings:
        assert emb.signature_valid is True
        assert emb.content_hash_valid is True
        assert emb.verification_status == "Success"
