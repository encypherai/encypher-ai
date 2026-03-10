from __future__ import annotations

# TEAM_054: Regression tests for C2PA text manifest exclusions using byte offsets.
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.payloads import deserialize_c2pa_payload_from_cbor, deserialize_jumbf_payload
from encypher.core.signing import extract_payload_from_cose_sign1
from encypher.core.unicode_metadata import UnicodeMetadata
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
    text = "Cafe\u0301 ☕ and emoji 😀"

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

    manifest_store = deserialize_jumbf_payload(manifest_bytes)
    assert isinstance(manifest_store, dict)
    cose_sign1_b64 = manifest_store.get("cose_sign1")
    assert isinstance(cose_sign1_b64, str)

    cose_bytes = base64.b64decode(cose_sign1_b64)
    cbor_payload = extract_payload_from_cose_sign1(cose_bytes)
    assert cbor_payload is not None
    c2pa_manifest = deserialize_c2pa_payload_from_cbor(cbor_payload)

    assertions = c2pa_manifest.get("assertions", [])
    hard_binding = next((a for a in assertions if isinstance(a, dict) and a.get("label") == "c2pa.hash.data.v1"), None)
    assert hard_binding is not None
    hard_binding_data = hard_binding.get("data", {})
    exclusions = hard_binding_data.get("exclusions")
    assert isinstance(exclusions, list)
    assert exclusions
    first = exclusions[0]
    assert isinstance(first, dict)

    assert first.get("start") == wrapper_start_byte
    assert first.get("length") == wrapper_length_byte

    expected_hash = hard_binding_data.get("hash")
    assert isinstance(expected_hash, str)

    actual_hash = compute_normalized_hash(
        signed_text,
        exclusions=[(wrapper_start_byte, wrapper_length_byte)],
    ).hexdigest
    assert actual_hash == expected_hash
