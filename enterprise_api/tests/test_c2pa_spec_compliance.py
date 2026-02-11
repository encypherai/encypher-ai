"""
TEAM_088: C2PA Text Manifest Wrapper spec compliance tests.

Validates the exact marketing-site /api/tools/sign flow against every
requirement in docs/c2pa/Manifests_Text.txt.

Tests the full chain:
  EncodeDecodeTool.tsx → /api/tools/sign → buildSignBasicRequest →
  enterprise API /api/v1/sign → signing_executor.execute_signing →
  UnicodeMetadata.embed_metadata(metadata_format="c2pa") → _embed_c2pa →
  encode_wrapper (c2pa_text library)
"""

import hashlib
import struct
import unicodedata
from typing import Optional

import pytest

try:
    from encypher.core.keys import generate_ed25519_key_pair
    from encypher.core.unicode_metadata import UnicodeMetadata
    from encypher.interop.c2pa.text_wrapper import find_and_decode

    ENCYPHER_AVAILABLE = True
except ImportError:
    ENCYPHER_AVAILABLE = False
    pytest.skip("encypher-ai not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# Constants from the C2PA spec (docs/c2pa/Manifests_Text.txt)
# ---------------------------------------------------------------------------
ZWNBSP = "\uFEFF"  # U+FEFF Zero-Width No-Break Space
VS_START = 0xFE00  # U+FE00 (VS1)
VS_END = 0xFE0F  # U+FE0F (VS16)
VS_SUP_START = 0xE0100  # U+E0100 (VS17)
VS_SUP_END = 0xE01EF  # U+E01EF (VS256)
MAGIC = 0x4332504154585400  # "C2PATXT\0"
VERSION = 1

# The exact text the user tests with on the marketing-site sign tool
MARKETING_SITE_TEST_TEXT = (
    "TrendSearch\n"
    "With our newest TrendSearch technology, you can search for relevant "
    "trends, topics or themes and filter by specific criteria. This provides "
    "direct access to curated trend articles. Each article delivers essential "
    "trend information and, most importantly, includes actionable "
    "recommendations \u2014 making TrendSearch your single, unified framework "
    "for market intelligence.\n"
    "\n"
    "TrendChat\n"
    "Do you need more dedicated trend advice? Then utilize our TrendChat "
    "feature. This is an advanced AI-powered chatbot that processes complex "
    "information to give you clear, actionable trend advice and specific "
    "recommendations instantly. It is your personal, on-demand consultant "
    "for turning insights into strategic action."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _is_variation_selector(cp: int) -> bool:
    return (VS_START <= cp <= VS_END) or (VS_SUP_START <= cp <= VS_SUP_END)


def _is_invisible(ch: str) -> bool:
    cp = ord(ch)
    return _is_variation_selector(cp) or cp == ord(ZWNBSP)


def _visible_text(text: str) -> str:
    return "".join(ch for ch in text if not _is_invisible(ch))


def _first_invisible_index(text: str) -> Optional[int]:
    for i, ch in enumerate(text):
        if _is_invisible(ch):
            return i
    return None


def _byte_to_vs(b: int) -> int:
    """Spec: byteToVariationSelector algorithm."""
    if 0 <= b <= 15:
        return VS_START + b
    elif 16 <= b <= 255:
        return VS_SUP_START + (b - 16)
    raise ValueError(f"Invalid byte: {b}")


def _vs_to_byte(cp: int) -> int:
    """Spec: variationSelectorToByte algorithm."""
    if VS_START <= cp <= VS_END:
        return cp - VS_START
    elif VS_SUP_START <= cp <= VS_SUP_END:
        return (cp - VS_SUP_START) + 16
    raise ValueError(f"Not a variation selector: U+{cp:04X}")


def _sign_text(text: str, **kwargs) -> str:
    """Sign text using the exact same path as the marketing-site basic flow."""
    private_key, _ = generate_ed25519_key_pair()
    defaults = dict(
        text=text,
        private_key=private_key,
        signer_id="test_signer",
        metadata_format="c2pa",
        claim_generator="encypher-enterprise-api/test",
        actions=[
            {
                "label": "c2pa.created",
                "when": "2025-01-01T00:00:00Z",
                "softwareAgent": "test",
            }
        ],
    )
    defaults.update(kwargs)
    return UnicodeMetadata.embed_metadata(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestC2PASpecPlacement:
    """Spec §Placement Rules — wrapper at end of visible text."""

    def test_wrapper_at_end_of_visible_text(self):
        """Rule 3: wrapper SHOULD be placed at end of visible text content."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        assert first_invis is not None
        assert first_invis >= len(nfc), (
            f"First invisible char at index {first_invis}, but visible text "
            f"ends at {len(nfc)}. Wrapper must be at end of visible text."
        )

    def test_visible_text_unchanged(self):
        """Visible text must be identical to NFC-normalized original."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        visible = _visible_text(signed)
        expected = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        assert visible == expected

    def test_wrapper_after_strategic_action(self):
        """Specific regression: wrapper must be AFTER 'strategic action.' not before 'action'."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        # "strategic action." ends at the very end of visible text
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        assert nfc.endswith("strategic action.")
        assert first_invis == len(nfc), (
            f"First invisible at {first_invis}, expected {len(nfc)} "
            f"(right after 'strategic action.')"
        )


class TestC2PASpecZWNBSPPrefix:
    """Spec §Placement Rules — ZWNBSP prefix."""

    def test_wrapper_prefixed_with_zwnbsp(self):
        """Rule 2: wrapper SHALL be prefixed with U+FEFF."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        assert signed[first_invis] == ZWNBSP, (
            f"First invisible char should be ZWNBSP (U+FEFF), "
            f"got U+{ord(signed[first_invis]):04X}"
        )

    def test_variation_selectors_follow_zwnbsp(self):
        """After ZWNBSP, all chars should be variation selectors."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        # Skip the ZWNBSP itself
        for i in range(first_invis + 1, len(signed)):
            cp = ord(signed[i])
            assert _is_variation_selector(cp), (
                f"Char at index {i} (U+{cp:04X}) is not a variation selector. "
                f"All chars after ZWNBSP must be variation selectors."
            )


class TestC2PASpecContiguousBlock:
    """Spec §Placement Rules — single contiguous block."""

    def test_wrapper_is_contiguous(self):
        """Rule 1: wrapper SHALL be a single, contiguous block."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        assert first_invis is not None

        # From first invisible to end, every char must be invisible
        for i in range(first_invis, len(signed)):
            assert _is_invisible(signed[i]), (
                f"Non-invisible char at index {i} (U+{ord(signed[i]):04X}) "
                f"breaks the contiguous block requirement."
            )

    def test_no_invisible_chars_in_visible_text(self):
        """Rule 4: wrapper SHALL NOT be split across multiple locations."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        # Check that no invisible chars appear within the visible text portion
        for i in range(len(nfc)):
            assert not _is_invisible(signed[i]), (
                f"Invisible char at index {i} within visible text portion. "
                f"Wrapper must not be split across locations."
            )


class TestC2PASpecMagicBytes:
    """Spec §Syntax — magic number C2PATXT\\0."""

    def test_magic_number_present(self):
        """First 8 bytes after ZWNBSP must decode to magic 0x4332504154585400."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        # Skip ZWNBSP, decode first 8 variation selectors to bytes
        vs_chars = signed[first_invis + 1:]
        decoded_bytes = bytes(_vs_to_byte(ord(vs_chars[i])) for i in range(8))
        magic_value = struct.unpack(">Q", decoded_bytes)[0]
        assert magic_value == MAGIC, (
            f"Magic number mismatch: got 0x{magic_value:016X}, "
            f"expected 0x{MAGIC:016X} ('C2PATXT\\0')"
        )

    def test_version_byte(self):
        """Byte 9 (after magic) must be version=1."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        vs_chars = signed[first_invis + 1:]
        version_byte = _vs_to_byte(ord(vs_chars[8]))
        assert version_byte == VERSION, (
            f"Version mismatch: got {version_byte}, expected {VERSION}"
        )

    def test_manifest_length_field(self):
        """Bytes 9-12 (after version) encode manifestLength as uint32."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        vs_chars = signed[first_invis + 1:]
        # magic=8 bytes, version=1 byte, manifestLength=4 bytes
        length_bytes = bytes(_vs_to_byte(ord(vs_chars[i])) for i in range(9, 13))
        manifest_length = struct.unpack(">I", length_bytes)[0]
        # Total VS chars should be: 8 (magic) + 1 (version) + 4 (length) + manifestLength
        expected_total_vs = 8 + 1 + 4 + manifest_length
        actual_vs_count = len(vs_chars)
        assert actual_vs_count == expected_total_vs, (
            f"VS count mismatch: {actual_vs_count} actual vs "
            f"{expected_total_vs} expected (manifestLength={manifest_length})"
        )


class TestC2PASpecEncodingAlgorithm:
    """Spec §Encoding and Decoding Algorithms."""

    def test_byte_to_vs_low_range(self):
        """Bytes 0-15 → U+FE00 to U+FE0F."""
        for b in range(16):
            vs = _byte_to_vs(b)
            assert vs == VS_START + b

    def test_byte_to_vs_high_range(self):
        """Bytes 16-255 → U+E0100 to U+E01EF."""
        for b in range(16, 256):
            vs = _byte_to_vs(b)
            assert vs == VS_SUP_START + (b - 16)

    def test_roundtrip_all_bytes(self):
        """Every byte 0-255 roundtrips through encode/decode."""
        for b in range(256):
            vs = _byte_to_vs(b)
            decoded = _vs_to_byte(vs)
            assert decoded == b, f"Byte {b} → VS U+{vs:04X} → {decoded}"


class TestC2PASpecNormalization:
    """Spec §Normalization — NFC normalization."""

    def test_text_is_nfc_normalized(self):
        """Producers SHALL normalize to NFC before hashing."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        visible = _visible_text(signed)
        # The visible text should already be NFC
        assert visible == unicodedata.normalize("NFC", visible), (
            "Visible text in signed output must be NFC-normalized"
        )

    def test_nfc_idempotent_for_test_text(self):
        """Our test text should be unchanged by NFC normalization."""
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        assert nfc == MARKETING_SITE_TEST_TEXT, (
            "Test text should already be in NFC form"
        )


class TestC2PASpecFindAndDecode:
    """Spec §Detection Algorithm — using c2pa_text library."""

    def test_find_and_decode_extracts_manifest(self):
        """find_and_decode must successfully extract the manifest bytes."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        manifest_bytes, clean_text, span = find_and_decode(signed)
        assert manifest_bytes is not None, "find_and_decode must find the wrapper"
        assert len(manifest_bytes) > 0, "Manifest bytes must not be empty"

    def test_clean_text_matches_original(self):
        """After removing wrapper, clean_text must match NFC-normalized original."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        _, clean_text, _ = find_and_decode(signed)
        expected = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        assert clean_text == expected

    def test_span_covers_wrapper_region(self):
        """The span returned by find_and_decode must cover the wrapper region."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        _, _, span = find_and_decode(signed)
        assert span is not None, "Span must be returned"
        start, end = span
        nfc_len = len(unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT))
        assert start >= nfc_len, (
            f"Wrapper span starts at {start}, but visible text ends at {nfc_len}"
        )


class TestC2PASpecContentBinding:
    """Spec §Content Binding — hard binding with data hash."""

    def test_verify_roundtrip(self):
        """Signed text must verify successfully with the correct public key."""
        private_key, public_key = generate_ed25519_key_pair()
        signed = UnicodeMetadata.embed_metadata(
            text=MARKETING_SITE_TEST_TEXT,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="c2pa",
            claim_generator="encypher-enterprise-api/test",
        )

        def resolver(sid):
            return public_key if sid == "test_signer" else None

        is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
            text=signed,
            public_key_resolver=resolver,
        )
        assert is_valid, "Signed text must verify successfully"
        assert signer_id == "test_signer"

    def test_tampered_text_fails_verification(self):
        """Modifying visible text must cause verification failure."""
        private_key, public_key = generate_ed25519_key_pair()
        signed = UnicodeMetadata.embed_metadata(
            text=MARKETING_SITE_TEST_TEXT,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="c2pa",
            claim_generator="encypher-enterprise-api/test",
        )

        # Tamper: replace "TrendSearch" with "TrendXearch"
        tampered = signed.replace("TrendSearch", "TrendXearch", 1)

        def resolver(sid):
            return public_key if sid == "test_signer" else None

        is_valid, _, _ = UnicodeMetadata.verify_metadata(
            text=tampered,
            public_key_resolver=resolver,
        )
        assert not is_valid, "Tampered text must fail verification"


class TestC2PASpecWithCustomAssertions:
    """Test that custom assertions (provenance) don't break spec compliance."""

    def test_with_status_assertion(self):
        """Status assertion (always added by signing_executor) must not break placement."""
        signed = _sign_text(
            MARKETING_SITE_TEST_TEXT,
            custom_assertions=[
                {
                    "label": "org.encypher.status",
                    "data": {
                        "statusListCredential": "https://example.com/status",
                        "statusListIndex": "42",
                    },
                }
            ],
        )
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        assert first_invis == len(nfc), (
            f"Status assertion must not affect wrapper placement. "
            f"First invisible at {first_invis}, expected {len(nfc)}"
        )

    def test_with_provenance_assertion(self):
        """User provenance assertion must not break placement."""
        signed = _sign_text(
            MARKETING_SITE_TEST_TEXT,
            custom_assertions=[
                {
                    "label": "org.encypher.user-provenance",
                    "data": {"text": "AI-generated content"},
                }
            ],
        )
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        first_invis = _first_invisible_index(signed)
        assert first_invis == len(nfc)

    def test_with_multiple_assertions(self):
        """Multiple custom assertions must not break placement."""
        signed = _sign_text(
            MARKETING_SITE_TEST_TEXT,
            custom_assertions=[
                {
                    "label": "org.encypher.status",
                    "data": {"statusListCredential": "https://example.com", "statusListIndex": "0"},
                },
                {
                    "label": "org.encypher.user-provenance",
                    "data": {"text": "AI-generated"},
                },
            ],
        )
        nfc = unicodedata.normalize("NFC", MARKETING_SITE_TEST_TEXT)
        visible = _visible_text(signed)
        assert visible == nfc
        first_invis = _first_invisible_index(signed)
        assert first_invis == len(nfc)


class TestC2PASpecPreservesWhitespace:
    """Verify original whitespace structure is preserved."""

    def test_newlines_preserved(self):
        """Newlines and paragraph breaks must be preserved in signed text."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        visible = _visible_text(signed)
        assert "\n\n" in visible, "Double newline (paragraph break) must be preserved"
        assert visible.count("\n") == MARKETING_SITE_TEST_TEXT.count("\n")

    def test_em_dash_preserved(self):
        """Em dash (U+2014) must be preserved."""
        signed = _sign_text(MARKETING_SITE_TEST_TEXT)
        visible = _visible_text(signed)
        assert "\u2014" in visible, "Em dash must be preserved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
