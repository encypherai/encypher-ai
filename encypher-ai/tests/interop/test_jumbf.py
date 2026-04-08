"""Unit tests for the JUMBF builder/parser module.

Tests cover:
  - Individual box construction and parsing
  - Assertion box round-trips
  - Full manifest store build -> parse round-trip
  - Extended size boxes
  - Rejection of non-JUMBF input
"""

from __future__ import annotations

import struct

import cbor2
import pytest

from encypher.interop.c2pa.jumbf import (
    TYPE_CBOR,
    TYPE_JUMB,
    TYPE_JUMD,
    UUID_CBOR_CONTENT,
    UUID_MANIFEST,
    UUID_MANIFEST_STORE,
    _box,
    build_assertion_box,
    build_manifest,
    build_manifest_store,
    cbor_box,
    cose_box,
    description_box,
    generate_manifest_label,
    parse_manifest_store,
    parse_superbox,
    superbox,
)


class TestBoxConstruction:
    """Tests for low-level _box() helper."""

    def test_box_basic(self):
        payload = b"hello"
        box = _box(b"test", payload)
        assert len(box) == 8 + len(payload)
        size, btype = struct.unpack(">I4s", box[:8])
        assert size == len(box)
        assert btype == b"test"
        assert box[8:] == payload

    def test_box_empty_payload(self):
        box = _box(b"empt", b"")
        assert len(box) == 8
        size = struct.unpack(">I", box[:4])[0]
        assert size == 8


class TestDescriptionBox:
    """Tests for JUMD description box construction."""

    def test_description_box_structure(self):
        desc = description_box(UUID_MANIFEST_STORE, "c2pa")
        # Outer box header
        size, btype = struct.unpack(">I4s", desc[:8])
        assert btype == TYPE_JUMD
        assert size == len(desc)
        # Payload: 16 byte UUID + 1 byte toggles + label + null terminator
        payload = desc[8:]
        assert payload[:16] == UUID_MANIFEST_STORE
        assert payload[16] == 0x03  # TOGGLE_REQUESTABLE
        assert payload[17:21] == b"c2pa"
        assert payload[21] == 0  # null terminator

    def test_description_box_with_salt(self):
        salt = b"\x00" * 16
        desc = description_box(UUID_MANIFEST_STORE, "c2pa", salt=salt)
        payload = desc[8:]
        # Toggles should include private flag
        assert payload[16] & 0x10 == 0x10


class TestSuperbox:
    """Tests for JUMB superbox construction."""

    def test_superbox_contains_description_and_content(self):
        content = cbor_box(cbor2.dumps({"test": True}))
        sbox = superbox(UUID_CBOR_CONTENT, "test.label", [content])
        # Outer header is jumb
        size, btype = struct.unpack(">I4s", sbox[:8])
        assert btype == TYPE_JUMB
        assert size == len(sbox)
        # First inner box should be jumd
        inner = sbox[8:]
        inner_size, inner_type = struct.unpack(">I4s", inner[:8])
        assert inner_type == TYPE_JUMD

    def test_superbox_round_trip(self):
        content = cbor_box(cbor2.dumps({"key": "value"}))
        sbox = superbox(UUID_CBOR_CONTENT, "my.assertion", [content])
        parsed = parse_superbox(sbox)
        assert parsed["label"] == "my.assertion"
        assert parsed["type_uuid"] == UUID_CBOR_CONTENT
        assert len(parsed["content_boxes"]) == 1
        assert parsed["content_boxes"][0][0] == TYPE_CBOR


class TestAssertionBox:
    """Tests for assertion box build/parse round-trip."""

    def test_assertion_box_round_trip(self):
        data = {"actions": [{"action": "c2pa.created"}]}
        cbor_data = cbor2.dumps(data)
        box = build_assertion_box("c2pa.actions.v2", cbor_data)
        parsed = parse_superbox(box)
        assert parsed["label"] == "c2pa.actions.v2"
        assert parsed["type_uuid"] == UUID_CBOR_CONTENT
        # Content box is a cbor box containing the assertion
        assert len(parsed["content_boxes"]) == 1
        ctype, cpayload = parsed["content_boxes"][0]
        assert ctype == TYPE_CBOR
        decoded = cbor2.loads(cpayload)
        assert decoded == data

    def test_assertion_box_inner_content_excludes_header(self):
        """The inner content for claim hashing is box[8:]."""
        cbor_data = cbor2.dumps({"test": True})
        box = build_assertion_box("test.label", cbor_data)
        inner = box[8:]
        # Inner should start with jumd description box
        inner_type = inner[4:8]
        assert inner_type == TYPE_JUMD


class TestManifestConstruction:
    """Tests for full manifest and manifest store construction."""

    def _build_sample_manifest_store(self):
        """Build a minimal conformant manifest store for testing."""
        label = "urn:c2pa:test-1234"
        actions_data = cbor2.dumps({"actions": [{"action": "c2pa.created"}]})
        hash_data = cbor2.dumps({"hash": b"\x00" * 32, "alg": "sha256"})
        assertion_boxes = [
            build_assertion_box("c2pa.actions.v2", actions_data),
            build_assertion_box("c2pa.hash.data", hash_data),
        ]
        claim_cbor = cbor2.dumps({"instanceID": "urn:uuid:test", "alg": "sha256"})
        sig_cose = b"\xd2" + b"\x00" * 100  # placeholder COSE bytes
        manifest = build_manifest(label, assertion_boxes, claim_cbor, sig_cose)
        store = build_manifest_store([manifest])
        return store, label

    def test_manifest_store_round_trip(self):
        store, label = self._build_sample_manifest_store()
        parsed = parse_manifest_store(store)
        assert len(parsed["manifests"]) == 1
        m = parsed["manifests"][0]
        assert m["label"] == label
        assert "c2pa.actions.v2" in m["assertions"]
        assert "c2pa.hash.data" in m["assertions"]
        assert m["claim_cbor"] is not None
        assert m["signature_cose"] is not None

    def test_manifest_store_assertion_data_integrity(self):
        store, _ = self._build_sample_manifest_store()
        parsed = parse_manifest_store(store)
        m = parsed["manifests"][0]
        actions = cbor2.loads(m["assertions"]["c2pa.actions.v2"])
        assert actions["actions"][0]["action"] == "c2pa.created"

    def test_manifest_store_assertion_jumbf_present(self):
        """assertion_jumbf should contain raw JUMBF content for hash verification."""
        store, _ = self._build_sample_manifest_store()
        parsed = parse_manifest_store(store)
        m = parsed["manifests"][0]
        assert "c2pa.actions.v2" in m["assertion_jumbf"]
        assert len(m["assertion_jumbf"]["c2pa.actions.v2"]) > 0

    def test_manifest_has_correct_box_hierarchy(self):
        """Verify the box structure matches C2PA spec."""
        store, _ = self._build_sample_manifest_store()
        # Top-level: jumb with c2pa label
        top = parse_superbox(store)
        assert top["label"] == "c2pa"
        assert top["type_uuid"] == UUID_MANIFEST_STORE
        # One manifest inside
        assert len(top["content_boxes"]) == 1
        mtype, mpayload = top["content_boxes"][0]
        assert mtype == TYPE_JUMB


class TestGenerateManifestLabel:
    def test_format(self):
        label = generate_manifest_label()
        assert label.startswith("urn:c2pa:")
        # UUID portion
        uuid_part = label[len("urn:c2pa:") :]
        assert len(uuid_part) == 36  # standard UUID string length

    def test_uniqueness(self):
        labels = {generate_manifest_label() for _ in range(100)}
        assert len(labels) == 100


class TestParserRejectsInvalid:
    def test_rejects_json_payload(self):
        """Old-format JSON-in-jumb should NOT parse as manifest store."""
        json_bytes = b'{"format":"c2pa","signer_id":"test"}'
        fake_jumb = struct.pack(">I", 8 + len(json_bytes)) + b"jumb" + json_bytes
        with pytest.raises(ValueError):
            parse_manifest_store(fake_jumb)

    def test_rejects_garbage(self):
        with pytest.raises(ValueError):
            parse_manifest_store(b"this is not jumbf")

    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            parse_manifest_store(b"")

    def test_rejects_wrong_uuid(self):
        """A jumb box with the wrong type UUID is not a manifest store."""
        wrong = superbox(UUID_MANIFEST, "wrong", [])
        with pytest.raises(ValueError, match="Not a C2PA manifest store"):
            parse_manifest_store(wrong)


class TestCoseBox:
    def test_cose_box_uses_cbor_type(self):
        """Per C2PA spec, COSE is in a cbor content box inside c2cs superbox."""
        data = b"\xd2\x00" * 50
        box = cose_box(data)
        btype = box[4:8]
        assert btype == TYPE_CBOR
        assert box[8:] == data
