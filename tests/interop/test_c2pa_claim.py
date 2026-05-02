"""Unit tests for the C2PA claim v2 builder.

Tests cover:
  - Claim CBOR structure and required fields
  - Hashed assertion references in created_assertions
  - Hash correctness (assertion content hash matches claim reference)
  - No v1-only fields present
"""

from __future__ import annotations

import hashlib

import cbor2

from encypher.interop.c2pa.c2pa_claim import (
    HASH_ALG_SHA256,
    _compute_hash,
    build_claim_cbor,
)
from encypher.interop.c2pa.jumbf import build_assertion_box


class TestBuildClaimCbor:
    def _make_assertion_refs(self) -> list[tuple[str, bytes]]:
        """Build sample assertion boxes and return (label, inner_content) pairs."""
        labels_and_data = [
            ("c2pa.actions.v2", cbor2.dumps({"actions": [{"action": "c2pa.created"}]})),
            ("c2pa.hash.data", cbor2.dumps({"hash": b"\x00" * 32, "alg": "sha256"})),
        ]
        refs = []
        for label, cbor_data in labels_and_data:
            box = build_assertion_box(label, cbor_data)
            inner_content = box[8:]  # strip jumb superbox header
            refs.append((label, inner_content))
        return refs

    def test_produces_valid_cbor(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert isinstance(claim, dict)

    def test_required_fields_present(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert "instanceID" in claim
        assert claim["instanceID"].startswith("urn:uuid:")
        assert "claim_generator_info" in claim
        assert "name" in claim["claim_generator_info"]
        assert "signature" in claim
        assert "created_assertions" in claim
        assert "alg" in claim

    def test_version_included_when_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor(
            "urn:c2pa:test-1234", refs, dc_format="text/plain", product_version="2.0"
        )
        claim = cbor2.loads(claim_bytes)
        assert claim["claim_generator_info"]["version"] == "2.0"

    def test_version_absent_when_not_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert "version" not in claim["claim_generator_info"]

    def test_spec_version_included_when_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor(
            "urn:c2pa:test-1234", refs, dc_format="text/plain", spec_version="2.4"
        )
        claim = cbor2.loads(claim_bytes)
        assert claim["claim_generator_info"]["specVersion"] == "2.4"

    def test_spec_version_absent_when_not_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert "specVersion" not in claim["claim_generator_info"]

    def test_signature_reference_format(self):
        refs = self._make_assertion_refs()
        label = "urn:c2pa:test-1234"
        claim_bytes = build_claim_cbor(label, refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert claim["signature"] == f"self#jumbf={label}/c2pa.signature"

    def test_created_assertions_url_format(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assertions = claim["created_assertions"]
        assert len(assertions) == 2
        assert assertions[0]["url"] == "self#jumbf=c2pa.assertions/c2pa.actions.v2"
        assert assertions[1]["url"] == "self#jumbf=c2pa.assertions/c2pa.hash.data"

    def test_assertion_hashes_are_correct(self):
        """Each hash in created_assertions must match SHA-256 of assertion inner content."""
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        for i, (label, inner_content) in enumerate(refs):
            expected_hash = hashlib.sha256(inner_content).digest()
            actual_hash = claim["created_assertions"][i]["hash"]
            assert actual_hash == expected_hash, f"Hash mismatch for {label}"

    def test_no_v1_only_fields(self):
        """claim_generator, dc:format, assertions are v1-only and must not appear."""
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        v1_fields = ["claim_generator", "dc:format", "assertions"]
        for field in v1_fields:
            assert field not in claim, f"v1-only field '{field}' found in claim v2"

    def test_title_included_when_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor(
            "urn:c2pa:test-1234",
            refs,
            dc_format="text/plain",
            title="My Document",
        )
        claim = cbor2.loads(claim_bytes)
        assert claim.get("dc:title") == "My Document"

    def test_title_absent_when_not_provided(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain")
        claim = cbor2.loads(claim_bytes)
        assert "dc:title" not in claim

    def test_custom_claim_generator(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor(
            "urn:c2pa:test-1234",
            refs,
            dc_format="text/plain",
            claim_generator="MyApp",
        )
        claim = cbor2.loads(claim_bytes)
        assert claim["claim_generator_info"]["name"] == "MyApp"

    def test_alg_field(self):
        refs = self._make_assertion_refs()
        claim_bytes = build_claim_cbor("urn:c2pa:test-1234", refs, dc_format="text/plain", alg="sha384")
        claim = cbor2.loads(claim_bytes)
        assert claim["alg"] == "sha384"
        for a in claim["created_assertions"]:
            assert a["alg"] == "sha384"


class TestComputeHash:
    def test_sha256(self):
        data = b"hello world"
        expected = hashlib.sha256(data).digest()
        assert _compute_hash(data, HASH_ALG_SHA256) == expected

    def test_sha384(self):
        data = b"hello world"
        expected = hashlib.sha384(data).digest()
        assert _compute_hash(data, "sha384") == expected
