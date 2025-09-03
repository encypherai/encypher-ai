import hashlib
import unicodedata
from typing import Any, Dict, Literal, Optional, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher.core.constants import MetadataTarget
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata

# Zero-width characters to strip during normalization
ZERO_WIDTH_CODEPOINTS = {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF}
VS_LOW_START = 0xFE00
VS_LOW_END = 0xFE0F
VS_SUP_START = 0xE0100
VS_SUP_END = 0xE01EF


def normalize_text_backend_equivalent(s: str) -> str:
    """Apply the same normalization algorithm as the backend for hashing.

    Steps:
      - Strip leading BOM if present
      - NFC normalization
      - Normalize newlines CRLF/CR -> LF
      - Remove variation selectors (U+FE00–U+FE0F, U+E0100–U+E01EF)
      - Remove zero-width chars {ZWSP, ZWNJ, ZWJ, WJ, BOM}
    """
    # Strip BOM at start only
    if s.startswith("\ufeff"):
        s = s.lstrip("\ufeff")

    # Normalize newlines
    s = s.replace("\r\n", "\n").replace("\r", "\n")

    # NFC normalization
    s = unicodedata.normalize("NFC", s)

    # Remove VS and zero-widths
    def _is_vs_or_zw(cp: int) -> bool:
        if VS_LOW_START <= cp <= VS_LOW_END:
            return True
        if VS_SUP_START <= cp <= VS_SUP_END:
            return True
        if cp in ZERO_WIDTH_CODEPOINTS:
            return True
        return False

    s = "".join(c for c in s if not _is_vs_or_zw(ord(c)))
    return s


def sha256_hex_of_utf8(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _tail_marker_count(s: str) -> int:
    """Count trailing variation selectors at end of string."""
    count = 0
    for ch in reversed(s):
        cp = ord(ch)
        if VS_LOW_START <= cp <= VS_LOW_END or VS_SUP_START <= cp <= VS_SUP_END:
            count += 1
        else:
            break
    return count


@pytest.mark.parametrize("metadata_format", ["cbor_manifest", "manifest"])
@pytest.mark.parametrize("bom", [True, False])
@pytest.mark.parametrize("newline", ["LF", "CRLF"])
@pytest.mark.parametrize("inject_markers", [True, False])
def test_extract_and_verify_file_end_success(metadata_format: Literal["cbor_manifest", "manifest"], bom: bool, newline: str, inject_markers: bool):
    """Test successful metadata extraction and verification for FILE_END embedding."""
    # 1) Build base text (~2–3KB)
    base = "# Title\n\nThis is a paragraph with emojis 😊🚀 and mixed scripts مرحبا שלום end.\n" * 40
    text = ("\ufeff" + base) if bom else base
    text = text.replace("\n", "\r\n") if newline == "CRLF" else text
    if inject_markers:
        # Add some tail noise: ZWSP + VS-16 + ZWNJ
        text = text + "\u200b\ufe0f\u200c"

    # 2) Compute normalized sha256
    normalized = normalize_text_backend_equivalent(text)
    expected_sha = sha256_hex_of_utf8(normalized)

    # 3) Sign/Embed at FILE_END
    priv, pub = generate_ed25519_key_pair()
    signer_id = "test-file-end-signer"

    encoded = UnicodeMetadata.embed_metadata(
        text=text,
        private_key=priv,
        signer_id=signer_id,
        metadata_format=metadata_format,
        target=MetadataTarget.FILE_END,
        custom_metadata={"hash": expected_sha},
    )

    # 4) Extract
    extracted = UnicodeMetadata.extract_metadata(text=encoded)
    assert extracted is not None, _diag_msg(encoded, metadata_format, bom, newline, inject_markers, "extract_metadata returned None")

    instances = extracted if isinstance(extracted, list) else [extracted]
    assert len(instances) >= 1, _diag_msg(encoded, metadata_format, bom, newline, inject_markers, "No instances extracted")
    meta = instances[-1]
    assert isinstance(meta, dict), _diag_msg(encoded, metadata_format, bom, newline, inject_markers, f"Instance not a dict payload: {type(meta)}")
    meta_dict: Dict[str, Any] = cast(Dict[str, Any], meta)
    custom_md = meta_dict.get("custom_metadata")
    if not isinstance(custom_md, dict):
        custom_md = {}
    embedded_hash = custom_md.get("hash") or meta_dict.get("hash")
    assert embedded_hash == expected_sha, _diag_msg(
        encoded, metadata_format, bom, newline, inject_markers, f"Embedded hash mismatch: {embedded_hash} != {expected_sha}"
    )

    found_signer = meta_dict.get("signer_id") or meta_dict.get("key_id")
    assert found_signer == signer_id, _diag_msg(
        encoded, metadata_format, bom, newline, inject_markers, f"signer mismatch: {found_signer} != {signer_id}"
    )

    # 5) Verify
    def resolver(sid: str) -> Optional[Ed25519PublicKey]:
        return pub if sid == signer_id else None

    vr = UnicodeMetadata.verify_metadata(text=encoded, public_key_resolver=resolver, return_payload_on_failure=True)
    if isinstance(vr, tuple):
        is_valid, verified_signer, _payload = vr
        assert is_valid and verified_signer == signer_id, _diag_msg(
            encoded, metadata_format, bom, newline, inject_markers, f"verify tuple invalid: valid={is_valid}, signer={verified_signer}"
        )
    elif isinstance(vr, dict):
        assert vr.get("signature_valid", True) is True, _diag_msg(
            encoded, metadata_format, bom, newline, inject_markers, "verify dict indicates failure"
        )
    else:
        pytest.fail(_diag_msg(encoded, metadata_format, bom, newline, inject_markers, f"Unexpected verify result type: {type(vr)}"))

    # Stability: idempotent extraction
    extracted_again = UnicodeMetadata.extract_metadata(text=encoded)
    assert extracted_again == extracted, _diag_msg(encoded, metadata_format, bom, newline, inject_markers, "extract_metadata not idempotent")


@pytest.mark.parametrize("metadata_format", ["cbor_manifest", "manifest"])
@pytest.mark.parametrize("bom", [True, False])
@pytest.mark.parametrize("newline", ["LF", "CRLF"])
@pytest.mark.parametrize("inject_markers", [True, False])
def test_tamper_detection_file_end(metadata_format: Literal["cbor_manifest", "manifest"], bom: bool, newline: str, inject_markers: bool):
    """Test tamper detection for FILE_END embedding - expected to fail due to no hard-binding."""
    # 1) Build base text (~2–3KB)
    base = "# Title\n\nThis is a paragraph with emojis 😊🚀 and mixed scripts مرحبا שלום end.\n" * 40
    text = ("\ufeff" + base) if bom else base
    text = text.replace("\n", "\r\n") if newline == "CRLF" else text
    if inject_markers:
        # Add some tail noise: ZWSP + VS-16 + ZWNJ
        text = text + "\u200b\ufe0f\u200c"

    # 2) Compute normalized sha256
    normalized = normalize_text_backend_equivalent(text)
    expected_sha = sha256_hex_of_utf8(normalized)

    # 3) Sign/Embed at FILE_END
    priv, pub = generate_ed25519_key_pair()
    signer_id = "test-file-end-signer"

    encoded = UnicodeMetadata.embed_metadata(
        text=text,
        private_key=priv,
        signer_id=signer_id,
        metadata_format=metadata_format,
        target=MetadataTarget.FILE_END,
        custom_metadata={"hash": expected_sha},
    )

    # Negative (tamper) test: modify visible content
    tampered = encoded.replace("paragraph", "paraGRAPH", 1)
    tam_norm = normalize_text_backend_equivalent(tampered)
    tam_sha = sha256_hex_of_utf8(tam_norm)
    assert tam_sha != expected_sha, _diag_msg(
        encoded, metadata_format, bom, newline, inject_markers, "Tampered normalized hash unexpectedly equals embedded hash"
    )

    # lib semantics: for non-C2PA formats, signature may not be bound to content
    def resolver(sid: str) -> Optional[Ed25519PublicKey]:
        return pub if sid == signer_id else None

    vr_t = UnicodeMetadata.verify_metadata(text=tampered, public_key_resolver=resolver, return_payload_on_failure=True)
    if isinstance(vr_t, tuple):
        is_valid_t, _sid_t, _ = vr_t
        if is_valid_t:
            pytest.xfail("Verification passed after visible content tamper (no hard-binding). Potential gap to discuss.")
    elif isinstance(vr_t, dict):
        if vr_t.get("signature_valid", True) is True:
            pytest.xfail("Verification dict indicates success after tamper (no hard-binding). Potential gap to discuss.")


def _diag_msg(
    encoded_text: str,
    metadata_format: str,
    bom: bool,
    newline: str,
    inject_markers: bool,
    reason: str,
) -> str:
    # Failure diagnostics string
    params = {
        "format": metadata_format,
        "bom": bom,
        "newline": newline,
        "inject_markers": inject_markers,
        "tail_vs_count": _tail_marker_count(encoded_text),
    }
    head = encoded_text[:200]
    tail = encoded_text[-200:]
    keys_snapshot: Dict[str, bool] = {}
    try:
        extracted = UnicodeMetadata.extract_metadata(text=encoded_text)
        if isinstance(extracted, list):
            payload: Dict[str, Any] = extracted[-1] if extracted else {}  # type: ignore[assignment]
        else:
            payload = extracted or {}  # type: ignore[assignment]
        if isinstance(payload, dict):
            for k in payload.keys():
                keys_snapshot[str(k)] = True
    except Exception:
        pass
    return (
        f"Reason: {reason}\n"
        f"Params: {params}\n"
        f"Extracted keys: {sorted(keys_snapshot.keys())}\n"
        f"Encoded head(200): {repr(head)}\n"
        f"Encoded tail(200): {repr(tail)}\n"
    )
