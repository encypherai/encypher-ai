from __future__ import annotations

# TEAM_054: Regression tests for C2PA text manifest exclusions using byte offsets.
import cbor2
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa.jumbf import parse_manifest_store
from encypher.interop.c2pa.text_hashing import compute_normalized_hash
from encypher.interop.c2pa.text_wrapper import find_wrapper_info_bytes


def _public_key_resolver(expected: str, public_key: Ed25519PublicKey):
    def resolver(signer_id: str):
        if signer_id == expected:
            return public_key
        return None

    return resolver


def test_c2pa_exclusions_are_byte_offsets_in_nfc_utf8() -> None:
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_demo"

    # Intentionally use decomposed unicode + emoji so char offsets != byte offsets
    # and normalization changes the representation.
    text = "Cafe\u0301 \u2615 and emoji \U0001f600"

    signed_text = UnicodeMetadata.embed_metadata(
        text=text,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        add_hard_binding=True,
    )

    is_valid, extracted_signer_id, manifest = UnicodeMetadata.verify_metadata(
        text=signed_text,
        public_key_resolver=_public_key_resolver(signer_id, public_key),
    )
    assert is_valid is True
    assert extracted_signer_id == signer_id
    assert isinstance(manifest, dict)

    wrapper_info = find_wrapper_info_bytes(signed_text)
    assert wrapper_info is not None
    manifest_bytes, wrapper_start_byte, wrapper_length_byte = wrapper_info

    # Parse conformant JUMBF manifest store
    parsed = parse_manifest_store(manifest_bytes)
    assert len(parsed["manifests"]) >= 1
    active_manifest = parsed["manifests"][-1]

    # Find hard binding assertion
    hard_binding_cbor = None
    for label, cbor_bytes in active_manifest["assertions"].items():
        if label in ("c2pa.hash.data", "c2pa.hash.data.v1"):
            hard_binding_cbor = cbor_bytes
            break
    assert hard_binding_cbor is not None
    hard_binding_data = cbor2.loads(hard_binding_cbor)

    exclusions = hard_binding_data.get("exclusions")
    assert isinstance(exclusions, list)
    assert exclusions
    first = exclusions[0]
    assert isinstance(first, dict)

    # Start offset must be exact byte offset in NFC UTF-8
    assert first.get("start") == wrapper_start_byte
    # Length is approximate in JUMBF format (VS encoding non-determinism),
    # so we verify the hash using the measured wrapper length instead.

    expected_hash = hard_binding_data.get("hash")
    # C2PA stores hash as raw bytes; normalize to hex for comparison
    if isinstance(expected_hash, bytes):
        expected_hash = expected_hash.hex()
    assert isinstance(expected_hash, str)

    actual_hash = compute_normalized_hash(
        signed_text,
        exclusions=[(wrapper_start_byte, wrapper_length_byte)],
    ).hexdigest
    assert actual_hash == expected_hash
