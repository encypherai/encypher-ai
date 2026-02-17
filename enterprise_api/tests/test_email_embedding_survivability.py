"""Email survivability tests for micro mode (ecc=True) VS256-RS markers vs zero-width markers.

These tests simulate common email-processor transformations (Unicode normalization,
character sanitization) to measure whether embedded signatures remain detectable
and verifiable.
"""

from __future__ import annotations

import re
import uuid
import unicodedata

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.vs256_rs_crypto import (
    create_minimal_signed_uuid as create_micro_ecc_signature,
    derive_signing_key_from_private_key as derive_micro_ecc_signing_key,
    embed_signature_safely as embed_micro_ecc_safely,
    find_all_minimal_signed_uuids as find_micro_ecc_signatures,
    verify_minimal_signed_uuid as verify_micro_ecc_signature,
)
from app.utils.zw_crypto import (
    create_minimal_signed_uuid as create_zw_signature,
    derive_signing_key_from_private_key as derive_zw_signing_key,
    embed_signature_safely as embed_zw_safely,
    find_all_minimal_signed_uuids as find_zw_signatures,
    verify_minimal_signed_uuid as verify_zw_signature,
)


def _transform_identity(text: str) -> str:
    return text


def _transform_unicode_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _transform_strip_supplementary_vs(text: str) -> str:
    return "".join(
        ch
        for ch in text
        if not (0xE0100 <= ord(ch) <= 0xE01EF)
    )


def _transform_strip_all_variation_selectors(text: str) -> str:
    return "".join(
        ch
        for ch in text
        if not ((0xFE00 <= ord(ch) <= 0xFE0F) or (0xE0100 <= ord(ch) <= 0xE01EF))
    )


def _transform_strip_format_controls(text: str) -> str:
    # Common aggressive sanitization behavior for zero-width controls.
    return re.sub(r"[\u200C\u200D\u034F\u180E\u200B\u2060\uFEFF]", "", text)


def _build_embedded_texts(base_text: str) -> tuple[str, bytes, str, bytes, uuid.UUID, uuid.UUID]:
    private_key = Ed25519PrivateKey.generate()

    micro_key = derive_micro_ecc_signing_key(private_key)
    micro_uuid = uuid.uuid4()
    micro_sig = create_micro_ecc_signature(micro_uuid, micro_key)
    micro_text = embed_micro_ecc_safely(base_text, micro_sig)

    zw_key = derive_zw_signing_key(private_key)
    zw_uuid = uuid.uuid4()
    zw_sig = create_zw_signature(zw_uuid, zw_key)
    zw_text = embed_zw_safely(base_text, zw_sig)

    return micro_text, micro_key, zw_text, zw_key, micro_uuid, zw_uuid


def test_email_identity_transform_preserves_both_embedding_types() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, micro_key, zw_text, zw_key, micro_uuid, zw_uuid = _build_embedded_texts(base_text)

    micro_processed = _transform_identity(micro_text)
    zw_processed = _transform_identity(zw_text)

    micro_sigs = find_micro_ecc_signatures(micro_processed)
    zw_sigs = find_zw_signatures(zw_processed)

    assert len(micro_sigs) == 1
    assert len(zw_sigs) == 1

    micro_valid, micro_extracted_uuid = verify_micro_ecc_signature(micro_sigs[0][2], micro_key)
    zw_valid, zw_extracted_uuid = verify_zw_signature(zw_sigs[0][2], zw_key)

    assert micro_valid is True
    assert zw_valid is True
    assert micro_extracted_uuid == micro_uuid
    assert zw_extracted_uuid == zw_uuid


def test_email_unicode_nfc_transform_preserves_both_embedding_types() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, micro_key, zw_text, zw_key, _, _ = _build_embedded_texts(base_text)

    micro_processed = _transform_unicode_nfc(micro_text)
    zw_processed = _transform_unicode_nfc(zw_text)

    micro_sigs = find_micro_ecc_signatures(micro_processed)
    zw_sigs = find_zw_signatures(zw_processed)

    assert len(micro_sigs) == 1
    assert len(zw_sigs) == 1

    micro_valid, _ = verify_micro_ecc_signature(micro_sigs[0][2], micro_key)
    zw_valid, _ = verify_zw_signature(zw_sigs[0][2], zw_key)

    assert micro_valid is True
    assert zw_valid is True


def test_email_strip_supplementary_variation_selectors_breaks_micro_ecc_markers() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, _, _, _, _, _ = _build_embedded_texts(base_text)

    micro_processed = _transform_strip_supplementary_vs(micro_text)
    micro_sigs = find_micro_ecc_signatures(micro_processed)

    # micro (ecc) magic prefix and many payload chars depend on supplementary VS.
    assert len(micro_sigs) == 0


def test_email_strip_all_variation_selectors_breaks_micro_ecc_markers() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, _, _, _, _, _ = _build_embedded_texts(base_text)

    micro_processed = _transform_strip_all_variation_selectors(micro_text)
    micro_sigs = find_micro_ecc_signatures(micro_processed)

    assert len(micro_sigs) == 0


def test_email_strip_format_controls_breaks_zero_width_embedding() -> None:
    base_text = "Email survivability sentence for Encypher."
    _, _, zw_text, _, _, _ = _build_embedded_texts(base_text)

    zw_processed = _transform_strip_format_controls(zw_text)
    zw_sigs = find_zw_signatures(zw_processed)

    assert len(zw_sigs) == 0
