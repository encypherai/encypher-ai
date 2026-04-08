"""
Tests for the C2PA manifest validator.
"""

import struct
import unicodedata

from c2pa_text import (
    MAGIC,
    VERSION,
    ValidationCode,
    ValidationResult,
    embed_manifest,
    extract_manifest,
    find_wrapper_info,
    validate_jumbf_structure,
    validate_manifest,
    validate_wrapper_bytes,
)


class TestValidateManifest:
    """Tests for validate_manifest() - the main validation entry point."""

    def test_empty_manifest_fails(self):
        """Empty bytes should fail validation."""
        result = validate_manifest(b"")
        assert not result.valid
        assert result.primary_code == ValidationCode.EMPTY_MANIFEST

    def test_minimal_valid_jumbf(self):
        """A minimal valid JUMBF box should pass basic validation."""
        # Minimal JUMBF superbox: size (4) + type (4) = 8 bytes
        # Size of 8 means just the header, no content
        jumbf = struct.pack(">I", 8) + b"jumb"
        result = validate_manifest(jumbf)
        assert result.valid
        assert result.primary_code == ValidationCode.VALID

    def test_invalid_box_type_fails(self):
        """Non-JUMBF box type should fail."""
        # Valid box structure but wrong type
        invalid = struct.pack(">I", 8) + b"xxxx"
        result = validate_manifest(invalid)
        assert not result.valid
        assert result.primary_code == ValidationCode.INVALID_JUMBF_HEADER

    def test_truncated_jumbf_fails(self):
        """JUMBF with declared size larger than actual should fail."""
        # Declare 100 bytes but only provide 8
        truncated = struct.pack(">I", 100) + b"jumb"
        result = validate_manifest(truncated)
        assert not result.valid
        assert result.primary_code == ValidationCode.TRUNCATED_JUMBF

    def test_box_size_too_small_fails(self):
        """Box size less than 8 (except 0 and 1) should fail."""
        invalid = struct.pack(">I", 5) + b"jumb"
        result = validate_manifest(invalid)
        assert not result.valid
        assert result.primary_code == ValidationCode.INVALID_JUMBF_BOX_SIZE

    def test_extended_size_box(self):
        """Extended size (64-bit) boxes should be handled."""
        # Size = 1 indicates extended size follows
        # Extended size = 24 (16 byte header + 8 bytes content)
        extended = struct.pack(">I", 1) + b"jumb" + struct.pack(">Q", 24) + b"content!"
        result = validate_manifest(extended)
        assert result.valid

    def test_extended_size_truncated_fails(self):
        """Extended size box without enough bytes for 64-bit size should fail."""
        # Size = 1 but only 10 bytes total (need 16 minimum)
        truncated = struct.pack(">I", 1) + b"jumb" + b"xx"
        result = validate_manifest(truncated)
        assert not result.valid
        assert result.primary_code == ValidationCode.TRUNCATED_JUMBF


class TestValidateJumbfStructure:
    """Tests for validate_jumbf_structure() with strict mode."""

    def test_strict_requires_description_box(self):
        """Strict mode should check for description box."""
        # Just a superbox with no content
        jumbf = struct.pack(">I", 8) + b"jumb"
        result = validate_jumbf_structure(jumbf, strict=True)
        assert not result.valid
        assert result.primary_code == ValidationCode.MISSING_DESCRIPTION_BOX

    def test_strict_validates_description_box_type(self):
        """Strict mode should validate description box type is 'jumd'."""
        # Superbox with wrong inner box type
        inner = struct.pack(">I", 8) + b"xxxx"
        jumbf = struct.pack(">I", 8 + len(inner)) + b"jumb" + inner
        result = validate_jumbf_structure(jumbf, strict=True)
        assert not result.valid
        assert result.primary_code == ValidationCode.MISSING_DESCRIPTION_BOX

    def test_strict_with_valid_description_box(self):
        """Strict mode should pass with valid description box."""
        # Description box with C2PA UUID
        c2pa_uuid = bytes.fromhex("6332706100110010800000AA00389B71")
        desc_content = c2pa_uuid + b"\x00" * 8  # UUID + some padding
        desc_box = struct.pack(">I", 8 + len(desc_content)) + b"jumd" + desc_content
        jumbf = struct.pack(">I", 8 + len(desc_box)) + b"jumb" + desc_box
        result = validate_jumbf_structure(jumbf, strict=True)
        assert result.valid


class TestValidateWrapperBytes:
    """Tests for validate_wrapper_bytes() - validates pre-encoded wrappers."""

    def test_valid_wrapper(self):
        """A properly structured wrapper should pass."""
        jumbf = struct.pack(">I", 8) + b"jumb"
        header = struct.pack("!8sBI", MAGIC, VERSION, len(jumbf))
        wrapper = header + jumbf
        result = validate_wrapper_bytes(wrapper)
        assert result.valid
        assert result.version == VERSION
        assert result.declared_length == len(jumbf)

    def test_wrapper_too_short(self):
        """Wrapper shorter than header size should fail."""
        result = validate_wrapper_bytes(b"short")
        assert not result.valid
        assert result.primary_code == ValidationCode.CORRUPTED_WRAPPER

    def test_invalid_magic(self):
        """Wrong magic bytes should fail."""
        jumbf = struct.pack(">I", 8) + b"jumb"
        header = struct.pack("!8sBI", b"WRONGMAG", VERSION, len(jumbf))
        wrapper = header + jumbf
        result = validate_wrapper_bytes(wrapper)
        assert not result.valid
        assert result.primary_code == ValidationCode.INVALID_MAGIC

    def test_unsupported_version(self):
        """Unsupported version should fail."""
        jumbf = struct.pack(">I", 8) + b"jumb"
        header = struct.pack("!8sBI", MAGIC, 99, len(jumbf))
        wrapper = header + jumbf
        result = validate_wrapper_bytes(wrapper)
        assert not result.valid
        assert result.primary_code == ValidationCode.UNSUPPORTED_VERSION

    def test_length_mismatch(self):
        """Declared length not matching actual should fail."""
        jumbf = struct.pack(">I", 8) + b"jumb"
        # Declare 100 bytes but only have 8
        header = struct.pack("!8sBI", MAGIC, VERSION, 100)
        wrapper = header + jumbf
        result = validate_wrapper_bytes(wrapper)
        assert not result.valid
        assert result.primary_code == ValidationCode.LENGTH_MISMATCH


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_str_representation_valid(self):
        """Valid result should have clear string representation."""
        result = ValidationResult(valid=True)
        assert "passed" in str(result).lower()

    def test_str_representation_invalid(self):
        """Invalid result should list issues."""
        result = ValidationResult(valid=True)
        result.add_issue(ValidationCode.EMPTY_MANIFEST, "Test message")
        output = str(result)
        assert "failed" in output.lower()
        assert "EMPTY_MANIFEST" in output or "emptyManifest" in output

    def test_add_issue_sets_valid_false(self):
        """Adding an issue should set valid to False."""
        result = ValidationResult(valid=True)
        assert result.valid
        result.add_issue(ValidationCode.EMPTY_MANIFEST, "Test")
        assert not result.valid


class TestIntegration:
    """Integration tests combining validation with embed/extract."""

    def test_validate_before_embed(self):
        """Demonstrate validation workflow before embedding."""
        # Create a valid JUMBF-like structure
        jumbf = struct.pack(">I", 8) + b"jumb"

        # Validate first
        result = validate_manifest(jumbf)
        assert result.valid, f"Validation failed: {result}"

        # Then embed
        text = "Hello, World!"
        watermarked = embed_manifest(text, jumbf)

        # Extract and verify
        extracted, clean = extract_manifest(watermarked)
        assert extracted == jumbf
        assert clean == text

    def test_invalid_manifest_caught_before_embed(self):
        """Invalid manifest should be caught by validation."""
        # Truncated/invalid JUMBF
        invalid = struct.pack(">I", 100) + b"jumb"  # Claims 100 bytes, has 8

        result = validate_manifest(invalid)
        assert not result.valid
        assert result.primary_code == ValidationCode.TRUNCATED_JUMBF

        # Developer would see this and fix before embedding
        assert "truncated" in str(result).lower()


class TestWrapperOffsets:
    def test_wrapper_offsets_are_nfc_utf8_byte_offsets(self):
        jumbf = struct.pack(">I", 8) + b"jumb"

        decomposed = "e\u0301"
        embedded = embed_manifest(decomposed, jumbf)

        info = find_wrapper_info(embedded)
        assert info is not None
        extracted, offset, length = info[0], info[1], info[2]
        assert extracted == jumbf

        normalized_nfc = unicodedata.normalize("NFC", decomposed)
        expected_offset = len(normalized_nfc.encode("utf-8"))
        expected_length = len(embedded.encode("utf-8")) - expected_offset

        assert offset == expected_offset
        assert length == expected_length

        extracted2, clean = extract_manifest(embedded)
        assert extracted2 == jumbf
        assert clean == normalized_nfc
