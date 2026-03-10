"""Email survivability tests for micro mode (ecc=True) VS256-RS markers vs zero-width markers.

These tests simulate common email-processor transformations (Unicode normalization,
character sanitization) to measure whether embedded signatures remain detectable
and verifiable.
"""

from __future__ import annotations

import re
import unicodedata

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.legacy_safe_crypto import (
    create_marker as create_ls_signature,
)
from app.utils.legacy_safe_crypto import (
    derive_signing_key_from_private_key as derive_ls_signing_key,
)
from app.utils.legacy_safe_crypto import (
    embed_marker_safely as embed_ls_safely,
)
from app.utils.legacy_safe_crypto import (
    find_all_markers as find_ls_signatures,
)
from app.utils.legacy_safe_crypto import (
    generate_log_id as ls_generate_log_id,
)
from app.utils.legacy_safe_crypto import (
    verify_marker as verify_ls_signature,
)
from app.utils.vs256_crypto import generate_log_id
from app.utils.vs256_rs_crypto import (
    create_signed_marker as create_micro_ecc_signature,
)
from app.utils.vs256_rs_crypto import (
    derive_signing_key_from_private_key as derive_micro_ecc_signing_key,
)
from app.utils.vs256_rs_crypto import (
    embed_signature_safely as embed_micro_ecc_safely,
)
from app.utils.vs256_rs_crypto import (
    find_all_markers as find_micro_ecc_signatures,
)
from app.utils.vs256_rs_crypto import (
    verify_signed_marker as verify_micro_ecc_signature,
)


def _transform_identity(text: str) -> str:
    return text


def _transform_unicode_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _transform_strip_supplementary_vs(text: str) -> str:
    return "".join(ch for ch in text if not (0xE0100 <= ord(ch) <= 0xE01EF))


def _transform_strip_all_variation_selectors(text: str) -> str:
    return "".join(ch for ch in text if not ((0xFE00 <= ord(ch) <= 0xFE0F) or (0xE0100 <= ord(ch) <= 0xE01EF)))


def _transform_strip_format_controls(text: str) -> str:
    # Common aggressive sanitization behavior for zero-width controls
    # (includes LRM/RLM used by legacy_safe/ZW6 encoding).
    return re.sub(r"[\u200C\u200D\u034F\u180E\u200B\u200E\u200F\u2060\uFEFF]", "", text)


def _build_embedded_texts(base_text: str) -> tuple[str, bytes, str, bytes, bytes, bytes]:
    private_key = Ed25519PrivateKey.generate()

    micro_key = derive_micro_ecc_signing_key(private_key)
    micro_log_id = generate_log_id()  # 16 random bytes (hyperscale-safe)
    micro_sig = create_micro_ecc_signature(micro_log_id, micro_key)
    micro_text = embed_micro_ecc_safely(base_text, micro_sig)

    ls_key = derive_ls_signing_key(private_key)
    ls_log_id = ls_generate_log_id()
    ls_sig = create_ls_signature(ls_log_id, ls_key)
    ls_text = embed_ls_safely(base_text, ls_sig)

    return micro_text, micro_key, ls_text, ls_key, micro_log_id, ls_log_id


def test_email_identity_transform_preserves_both_embedding_types() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, micro_key, ls_text, ls_key, micro_log_id, ls_log_id = _build_embedded_texts(base_text)

    micro_processed = _transform_identity(micro_text)
    ls_processed = _transform_identity(ls_text)

    micro_sigs = find_micro_ecc_signatures(micro_processed)
    ls_sigs = find_ls_signatures(ls_processed)

    assert len(micro_sigs) == 1
    assert len(ls_sigs) == 1

    micro_valid, micro_extracted = verify_micro_ecc_signature(micro_sigs[0][2], micro_key)
    ls_valid, ls_extracted = verify_ls_signature(ls_sigs[0][2], ls_key)

    assert micro_valid is True
    assert ls_valid is True
    assert micro_extracted == micro_log_id
    assert ls_extracted == ls_log_id


def test_email_unicode_nfc_transform_preserves_both_embedding_types() -> None:
    base_text = "Email survivability sentence for Encypher."
    micro_text, micro_key, ls_text, ls_key, _, _ = _build_embedded_texts(base_text)

    micro_processed = _transform_unicode_nfc(micro_text)
    ls_processed = _transform_unicode_nfc(ls_text)

    micro_sigs = find_micro_ecc_signatures(micro_processed)
    ls_sigs = find_ls_signatures(ls_processed)

    assert len(micro_sigs) == 1
    assert len(ls_sigs) == 1

    micro_valid, _ = verify_micro_ecc_signature(micro_sigs[0][2], micro_key)
    ls_valid, _ = verify_ls_signature(ls_sigs[0][2], ls_key)

    assert micro_valid is True
    assert ls_valid is True


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


def test_email_strip_format_controls_breaks_legacy_safe_embedding() -> None:
    base_text = "Email survivability sentence for Encypher."
    _, _, ls_text, _, _, _ = _build_embedded_texts(base_text)

    ls_processed = _transform_strip_format_controls(ls_text)
    ls_sigs = find_ls_signatures(ls_processed)

    assert len(ls_sigs) == 0
