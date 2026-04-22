"""Integration tests for C2PA JUMBF conformance.

Validates that the text signing pipeline produces ISO 19566-5 conformant
JUMBF manifest stores with correct assertion hashes, claim references,
COSE signatures, and hard/soft binding.
"""

from __future__ import annotations

import hashlib

import cbor2

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa.c2pa_claim import _compute_hash
from encypher.interop.c2pa.jumbf import (
    UUID_MANIFEST_STORE,
    parse_manifest_store,
    parse_superbox,
)
from encypher.interop.c2pa.text_hashing import compute_normalized_hash
from encypher.interop.c2pa.text_wrapper import find_and_decode, find_wrapper_info_bytes

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _keygen():
    private_key, public_key = generate_ed25519_key_pair()
    return private_key, public_key


def _resolver(expected_id: str, public_key):
    def _resolve(signer_id: str):
        if signer_id == expected_id:
            return public_key
        return None

    return _resolve


def _sign(text: str, private_key, signer_id: str = "test-signer", **kwargs):
    return UnicodeMetadata.embed_metadata(
        text=text,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        add_hard_binding=True,
        **kwargs,
    )


def _extract_manifest_store(signed_text: str) -> tuple[dict, bytes]:
    """Extract and parse the JUMBF manifest store from signed text."""
    manifest_bytes, _clean, _span = find_and_decode(signed_text)
    assert manifest_bytes is not None, "No C2PA wrapper found in signed text"
    parsed = parse_manifest_store(manifest_bytes)
    return parsed, manifest_bytes


# ---------------------------------------------------------------------------
# JUMBF structure tests
# ---------------------------------------------------------------------------


class TestJUMBFStructure:
    """Verify the JUMBF box hierarchy matches C2PA requirements."""

    def test_manifest_store_top_level_uuid(self):
        """Top-level superbox must have UUID_MANIFEST_STORE."""
        priv, _pub = _keygen()
        signed = _sign("Structure test.", priv)
        manifest_bytes, _clean, _span = find_and_decode(signed)
        assert manifest_bytes is not None

        top = parse_superbox(manifest_bytes)
        assert top["type_uuid"] == UUID_MANIFEST_STORE
        assert top["label"] == "c2pa"

    def test_manifest_box_structure(self):
        """Each manifest must contain assertion store, claim, and signature."""
        priv, _pub = _keygen()
        signed = _sign("Box structure test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        assert len(parsed["manifests"]) == 1
        m = parsed["manifests"][0]
        assert m["label"].startswith("urn:c2pa:")
        assert m["claim_cbor"] is not None
        assert m["signature_cose"] is not None
        assert len(m["assertions"]) > 0

    def test_assertion_store_contains_required_assertions(self):
        """Assertion store must include actions, hard binding, soft binding, signer."""
        priv, _pub = _keygen()
        signed = _sign("Required assertions test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        labels = set(parsed["manifests"][0]["assertions"].keys())
        assert any(l.startswith("c2pa.actions") for l in labels)
        assert any(l.startswith("c2pa.hash.data") for l in labels)
        assert "c2pa.soft-binding" in labels
        assert "com.encypher.signer" in labels
        assert "com.encypher.context" in labels

    def test_assertions_are_valid_cbor(self):
        """All assertion content boxes must contain valid CBOR."""
        priv, _pub = _keygen()
        signed = _sign("CBOR validity test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        for label, cbor_bytes in parsed["manifests"][0]["assertions"].items():
            data = cbor2.loads(cbor_bytes)
            assert isinstance(data, dict), f"Assertion {label} CBOR did not decode to dict"

    def test_claim_is_valid_cbor_with_required_fields(self):
        """Claim CBOR must contain v2 required fields."""
        priv, _pub = _keygen()
        signed = _sign("Claim fields test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        claim = cbor2.loads(parsed["manifests"][0]["claim_cbor"])
        assert "instanceID" in claim
        assert "claim_generator_info" in claim
        assert "signature" in claim
        assert "created_assertions" in claim
        assert "alg" in claim
        assert claim["alg"] == "sha256"

    def test_signature_is_cose_sign1(self):
        """Signature box must contain a valid COSE_Sign1 structure."""
        priv, _pub = _keygen()
        signed = _sign("COSE test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        cose_bytes = parsed["manifests"][0]["signature_cose"]
        assert cose_bytes is not None
        decoded = cbor2.loads(cose_bytes)
        # COSE_Sign1 is a 4-element array [protected, unprotected, payload, signature].
        # May be CBOR tag 18 (tagged) or bare array (Ed25519-only legacy).
        if hasattr(decoded, "tag"):
            assert decoded.tag == 18
            arr = decoded.value
        else:
            arr = decoded
        assert isinstance(arr, list) and len(arr) == 4


# ---------------------------------------------------------------------------
# Claim assertion hash verification
# ---------------------------------------------------------------------------


class TestClaimAssertionHashes:
    """Verify that claim's created_assertions hashes match actual assertion boxes."""

    def test_assertion_hashes_match(self):
        """Each created_assertion hash must match the actual JUMBF content hash."""
        priv, _pub = _keygen()
        signed = _sign("Hash verification test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        m = parsed["manifests"][0]
        claim = cbor2.loads(m["claim_cbor"])
        assertion_jumbf = m.get("assertion_jumbf", {})

        for ref in claim["created_assertions"]:
            url = ref["url"]
            expected_hash = ref["hash"]
            alg = ref.get("alg", "sha256")

            # Extract label from URI: self#jumbf=c2pa.assertions/<label>
            label = url.split("c2pa.assertions/")[-1]
            assert label in assertion_jumbf, f"Assertion {label} not found in JUMBF store"

            actual_hash = _compute_hash(assertion_jumbf[label], alg)
            assert actual_hash == expected_hash, f"Hash mismatch for {label}: claim={expected_hash.hex()}, actual={actual_hash.hex()}"

    def test_claim_signature_ref_is_correct(self):
        """Claim signature reference must point to the manifest's signature box."""
        priv, _pub = _keygen()
        signed = _sign("Signature ref test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        m = parsed["manifests"][0]
        claim = cbor2.loads(m["claim_cbor"])
        sig_ref = claim["signature"]
        assert "c2pa.signature" in sig_ref
        assert m["label"] in sig_ref


# ---------------------------------------------------------------------------
# Hard binding tests
# ---------------------------------------------------------------------------


class TestHardBinding:
    """Verify hard binding exclusion offsets and hash correctness."""

    def test_exclusion_start_matches_text_byte_length(self):
        """Hard binding exclusion start must equal the NFC text byte length."""
        priv, _pub = _keygen()
        text = "Hard binding offset test with unicode: cafe\u0301"
        signed = _sign(text, priv)
        parsed, _ = _extract_manifest_store(signed)

        hb_cbor = None
        for label, cbor_bytes in parsed["manifests"][0]["assertions"].items():
            if label.startswith("c2pa.hash.data"):
                hb_cbor = cbor_bytes
                break
        assert hb_cbor is not None

        hb = cbor2.loads(hb_cbor)
        exclusions = hb["exclusions"]
        assert len(exclusions) >= 1

        from encypher.interop.c2pa.text_hashing import normalize_text

        nfc_text = normalize_text(text)
        expected_start = len(nfc_text.encode("utf-8"))
        assert exclusions[0]["start"] == expected_start

    def test_hard_binding_hash_verifies_with_measured_wrapper(self):
        """Content hash must verify when excluding the measured wrapper range."""
        priv, _pub = _keygen()
        text = "Hard binding hash verification test."
        signed = _sign(text, priv)

        info = find_wrapper_info_bytes(signed)
        assert info is not None
        _manifest_bytes, start, length = info

        parsed, _ = _extract_manifest_store(signed)
        hb_cbor = None
        for label, cbor_bytes in parsed["manifests"][0]["assertions"].items():
            if label.startswith("c2pa.hash.data"):
                hb_cbor = cbor_bytes
                break
        assert hb_cbor is not None

        hb = cbor2.loads(hb_cbor)
        expected_hash = hb["hash"]
        # C2PA stores hash as raw bytes; normalize to hex for comparison
        if isinstance(expected_hash, bytes):
            expected_hash = expected_hash.hex()

        actual = compute_normalized_hash(signed, exclusions=[(start, length)])
        assert actual.hexdigest == expected_hash

    def test_hard_binding_with_decomposed_unicode(self):
        """Hard binding must handle NFC normalization for decomposed input."""
        priv, pub = _keygen()
        # Decomposed e-acute + emoji: NFC normalization changes byte representation
        text = "Cafe\u0301 \u2615 and emoji \U0001f600"
        signed = _sign(text, priv, signer_id="nfc-test")

        is_valid, signer, _payload = UnicodeMetadata.verify_metadata(signed, _resolver("nfc-test", pub))
        assert is_valid is True
        assert signer == "nfc-test"

    def test_exclusion_length_matches_actual_wrapper_byte_length(self):
        """Exclusion length must equal the actual wrapper UTF-8 byte length (deterministic padding)."""
        priv, _pub = _keygen()
        text = "Deterministic padding test."
        signed = _sign(text, priv)

        info = find_wrapper_info_bytes(signed)
        assert info is not None
        _manifest_bytes, start, measured_length = info

        parsed, _ = _extract_manifest_store(signed)
        hb_cbor = None
        for label, cbor_bytes in parsed["manifests"][0]["assertions"].items():
            if label.startswith("c2pa.hash.data"):
                hb_cbor = cbor_bytes
                break
        assert hb_cbor is not None

        hb = cbor2.loads(hb_cbor)
        declared_length = hb["exclusions"][0]["length"]
        assert declared_length == measured_length, (
            f"Declared exclusion length ({declared_length}) != " f"measured wrapper byte length ({measured_length})"
        )

    def test_exclusion_length_deterministic_across_content(self):
        """Two different texts producing same-size manifests must have same exclusion length."""
        priv, _pub = _keygen()
        signed1 = _sign("Deterministic test A.", priv)
        signed2 = _sign("Deterministic test B.", priv)

        def _get_exclusion_length(signed_text):
            parsed, _ = _extract_manifest_store(signed_text)
            for label, cbor_bytes in parsed["manifests"][0]["assertions"].items():
                if label.startswith("c2pa.hash.data"):
                    return cbor2.loads(cbor_bytes)["exclusions"][0]["length"]
            return None

        # Both texts have identical byte length, so manifests should be same size
        len1 = _get_exclusion_length(signed1)
        len2 = _get_exclusion_length(signed2)
        assert len1 is not None
        assert len1 == len2


# ---------------------------------------------------------------------------
# Soft binding tests
# ---------------------------------------------------------------------------


class TestSoftBinding:
    """Verify soft binding hash computation."""

    def test_soft_binding_hash_is_sha256_of_assertion_cbor(self):
        """Soft binding hash must be SHA-256 of concatenated non-SB assertion CBOR."""
        priv, _pub = _keygen()
        signed = _sign("Soft binding test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        assertions = parsed["manifests"][0]["assertions"]

        # Recompute: concatenate CBOR of all non-soft-binding assertions
        sb_input = b""
        sb_hash_stored = None
        for label, cbor_bytes in assertions.items():
            if label == "c2pa.soft-binding":
                sb_hash_stored = cbor2.loads(cbor_bytes).get("hash")
            else:
                data = cbor2.loads(cbor_bytes)
                sb_input += cbor2.dumps(data)

        assert sb_hash_stored is not None
        expected = hashlib.sha256(sb_input).digest()
        assert sb_hash_stored == expected

    def test_soft_binding_alg_field(self):
        """Soft binding must declare the VS encoding algorithm."""
        priv, _pub = _keygen()
        signed = _sign("SB alg test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        sb_cbor = parsed["manifests"][0]["assertions"]["c2pa.soft-binding"]
        sb = cbor2.loads(sb_cbor)
        assert sb["alg"] == "encypher.unicode_variation_selector.v1"


# ---------------------------------------------------------------------------
# Round-trip embed -> verify
# ---------------------------------------------------------------------------


class TestEmbedVerifyRoundTrip:
    """End-to-end embed -> verify tests with conformant JUMBF."""

    def test_basic_roundtrip(self):
        """Sign and verify plain ASCII text."""
        priv, pub = _keygen()
        text = "Simple round-trip test."
        signed = _sign(text, priv, signer_id="rt-basic")

        ok, signer, payload = UnicodeMetadata.verify_metadata(signed, _resolver("rt-basic", pub))
        assert ok is True
        assert signer == "rt-basic"
        assert payload is not None

    def test_roundtrip_with_custom_actions(self):
        """Custom actions must appear in the extracted manifest."""
        priv, pub = _keygen()
        actions = [
            {"label": "c2pa.edited", "when": "2026-01-01T00:00:00Z", "softwareAgent": "TestTool/1.0"},
        ]
        signed = _sign("Custom actions.", priv, signer_id="rt-actions", actions=actions)

        ok, signer, payload = UnicodeMetadata.verify_metadata(signed, _resolver("rt-actions", pub))
        assert ok is True
        assert payload is not None
        assertion_labels = {a.get("label") for a in payload.get("assertions", [])}
        assert any(l.startswith("c2pa.actions") for l in assertion_labels)

    def test_roundtrip_with_custom_assertions(self):
        """Custom assertions must survive the embed/verify cycle."""
        priv, pub = _keygen()
        custom = [{"label": "com.test.custom", "data": {"key": "value"}}]
        signed = _sign("Custom assertion.", priv, signer_id="rt-custom", custom_assertions=custom)

        ok, signer, payload = UnicodeMetadata.verify_metadata(signed, _resolver("rt-custom", pub))
        assert ok is True
        labels = {a.get("label") for a in payload.get("assertions", [])}
        assert "com.test.custom" in labels


# ---------------------------------------------------------------------------
# Tamper detection
# ---------------------------------------------------------------------------


class TestTamperDetection:
    """Verify that tampering with signed text is detected."""

    def test_text_modification_detected(self):
        """Changing the text content must fail verification."""
        priv, pub = _keygen()
        text = "This text must not be modified."
        signed = _sign(text, priv, signer_id="tamper-test")

        tampered = signed.replace("must not", "can be")
        ok, _signer, _payload = UnicodeMetadata.verify_metadata(tampered, _resolver("tamper-test", pub))
        assert ok is False

    def test_wrong_key_fails(self):
        """Verification with wrong key must fail."""
        priv, _pub = _keygen()
        _, wrong_pub = _keygen()
        signed = _sign("Wrong key test.", priv, signer_id="wk-test")

        ok, _signer, _payload = UnicodeMetadata.verify_metadata(signed, _resolver("wk-test", wrong_pub))
        assert ok is False

    def test_text_with_surrounding_chrome(self):
        """Signed text pasted with surrounding page chrome must still verify."""
        priv, pub = _keygen()
        text = "Text for chrome test."
        signed = _sign(text, priv, signer_id="chrome-test")

        # Simulate page chrome surrounding the signed text
        with_chrome = "PAGE HEADER\n\n" + signed + "\n\nPAGE FOOTER"
        ok, signer, _payload = UnicodeMetadata.verify_metadata(with_chrome, _resolver("chrome-test", pub))
        assert ok is True
        assert signer == "chrome-test"


# ---------------------------------------------------------------------------
# Signer and context assertions
# ---------------------------------------------------------------------------


class TestSignerAndContextAssertions:
    """Verify com.encypher.signer and com.encypher.context assertions."""

    def test_signer_assertion_contains_signer_id(self):
        """com.encypher.signer assertion must carry the signer_id."""
        priv, _pub = _keygen()
        signed = _sign("Signer assertion test.", priv, signer_id="signer-abc")
        parsed, _ = _extract_manifest_store(signed)

        signer_cbor = parsed["manifests"][0]["assertions"]["com.encypher.signer"]
        signer_data = cbor2.loads(signer_cbor)
        assert signer_data["signer_id"] == "signer-abc"

    def test_context_assertion_contains_c2pa_url(self):
        """com.encypher.context assertion must carry the C2PA context URL."""
        priv, _pub = _keygen()
        signed = _sign("Context assertion test.", priv)
        parsed, _ = _extract_manifest_store(signed)

        ctx_cbor = parsed["manifests"][0]["assertions"]["com.encypher.context"]
        ctx_data = cbor2.loads(ctx_cbor)
        assert "@context" in ctx_data
        assert "c2pa.org" in ctx_data["@context"]
