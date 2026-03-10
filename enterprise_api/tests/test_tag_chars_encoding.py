"""
Automated tests for Unicode Tag Character encoding properties.

Tests encoding/decoding roundtrips, Unicode properties, and size characteristics
of tag characters (U+E0000-U+E007F) as potential candidates for invisible
text embedding alongside or replacing the current base-4 charset.

Run:
    cd enterprise_api
    uv run pytest tests/test_tag_chars_encoding.py -v
"""

import math
import unicodedata

# ── Tag character definitions ──────────────────────────────────────────

TAG_PRINTABLE_START = 0xE0020  # TAG SPACE
TAG_PRINTABLE_END = 0xE007E  # TAG TILDE
TAG_PRINTABLE = [chr(cp) for cp in range(TAG_PRINTABLE_START, TAG_PRINTABLE_END + 1)]

TAG_BLOCK_START = 0xE0000
TAG_BLOCK_END = 0xE007F

# Current production base-4 set for comparison
CURRENT_BASE4 = ["\u200c", "\u200d", "\u034f", "\u180e"]  # ZWNJ, ZWJ, CGJ, MVS


# ── Unicode property tests ─────────────────────────────────────────────


class TestTagCharUnicodeProperties:
    """Verify Unicode properties that matter for invisible embedding."""

    def test_tag_printable_range_has_95_chars(self):
        assert len(TAG_PRINTABLE) == 95

    def test_all_tag_printable_are_format_category(self):
        """Tag chars should be General_Category: Cf (Format), same as ZWNJ/ZWJ."""
        for cp in range(TAG_PRINTABLE_START, TAG_PRINTABLE_END + 1):
            char = chr(cp)
            category = unicodedata.category(char)
            assert category == "Cf", f"U+{cp:05X} has category {category}, expected Cf"

    def test_current_base4_are_also_format_or_mark(self):
        """Our current chars are Cf or Mn — tag chars match this profile."""
        for char in CURRENT_BASE4:
            cat = unicodedata.category(char)
            assert cat in ("Cf", "Mn"), f"U+{ord(char):04X} has unexpected category {cat}"

    def test_tag_chars_are_supplementary_plane(self):
        """Tag chars are in Plane 14 (above BMP), requiring surrogate pairs in UTF-16."""
        for cp in range(TAG_BLOCK_START, TAG_BLOCK_END + 1):
            assert cp > 0xFFFF, f"U+{cp:05X} is unexpectedly in the BMP"

    def test_tag_chars_utf8_size(self):
        """Each tag char should be 4 bytes in UTF-8."""
        for char in TAG_PRINTABLE:
            assert len(char.encode("utf-8")) == 4

    def test_tag_chars_utf16_surrogate_pairs(self):
        """Each tag char should be a surrogate pair (4 bytes) in UTF-16."""
        for char in TAG_PRINTABLE:
            utf16_bytes = len(char.encode("utf-16-le"))
            assert utf16_bytes == 4, f"U+{ord(char):05X}: expected 4 UTF-16 bytes (surrogate pair), got {utf16_bytes}"

    def test_current_base4_utf8_size(self):
        """Current chars are 2-3 bytes in UTF-8 (smaller than tag chars)."""
        for char in CURRENT_BASE4:
            size = len(char.encode("utf-8"))
            assert size in (2, 3), f"U+{ord(char):04X}: unexpected UTF-8 size {size}"

    def test_tag_chars_have_names(self):
        """Verify we can look up tag character names (well-defined in Unicode)."""
        # Spot-check a few
        assert "TAG" in unicodedata.name(chr(0xE0041))  # TAG LATIN CAPITAL LETTER A
        assert "TAG" in unicodedata.name(chr(0xE0061))  # TAG LATIN SMALL LETTER a
        assert "CANCEL TAG" == unicodedata.name(chr(0xE007F))

    def test_language_tag_and_cancel_tag_exist(self):
        """U+E0001 (LANGUAGE TAG) and U+E007F (CANCEL TAG) are defined."""
        assert unicodedata.category(chr(0xE0001)) == "Cf"
        assert unicodedata.category(chr(0xE007F)) == "Cf"


# ── Encoding roundtrip tests ──────────────────────────────────────────


class TestTagCharEncoding:
    """Test encoding/decoding roundtrips using tag characters."""

    def _encode_byte_base_n(self, byte_val: int, base: int, charset: list) -> list:
        """Encode a byte value in the given base using the charset."""
        digits_needed = math.ceil(math.log(256, base)) if base > 1 else 8
        result = []
        value = byte_val
        for _ in range(digits_needed):
            result.append(charset[value % base])
            value //= base
        return result

    def _decode_byte_base_n(self, chars: list, base: int, charset: list) -> int:
        """Decode chars back to a byte value."""
        value = 0
        for i, char in enumerate(chars):
            idx = charset.index(char)
            value += idx * (base**i)
        return value

    def test_base4_roundtrip_all_bytes(self):
        """All 256 byte values roundtrip with 4 tag chars (base-4)."""
        charset = TAG_PRINTABLE[:4]
        for byte_val in range(256):
            encoded = self._encode_byte_base_n(byte_val, 4, charset)
            decoded = self._decode_byte_base_n(encoded, 4, charset)
            assert decoded == byte_val, f"Base-4 roundtrip failed for {byte_val}"

    def test_base16_roundtrip_all_bytes(self):
        """All 256 byte values roundtrip with 16 tag chars (base-16 / hex)."""
        charset = TAG_PRINTABLE[:16]
        for byte_val in range(256):
            encoded = self._encode_byte_base_n(byte_val, 16, charset)
            assert len(encoded) == 2  # 16^2 = 256 exactly
            decoded = self._decode_byte_base_n(encoded, 16, charset)
            assert decoded == byte_val, f"Base-16 roundtrip failed for {byte_val}"

    def test_base95_roundtrip_all_bytes(self):
        """All 256 byte values roundtrip with 95 tag chars (base-95)."""
        charset = TAG_PRINTABLE  # all 95
        for byte_val in range(256):
            d0 = byte_val % 95
            d1 = byte_val // 95
            encoded = [charset[d0], charset[d1]]
            decoded = charset.index(encoded[0]) + charset.index(encoded[1]) * 95
            assert decoded == byte_val, f"Base-95 roundtrip failed for {byte_val}"

    def test_base4_tag_chars_per_byte(self):
        """Base-4 with tag chars: 4 chars per byte (same as current)."""
        charset = TAG_PRINTABLE[:4]
        encoded = self._encode_byte_base_n(255, 4, charset)
        assert len(encoded) == 4

    def test_base16_tag_chars_per_byte(self):
        """Base-16 with tag chars: 2 chars per byte (50% reduction)."""
        charset = TAG_PRINTABLE[:16]
        encoded = self._encode_byte_base_n(255, 16, charset)
        assert len(encoded) == 2

    def test_base95_tag_chars_per_byte(self):
        """Base-95 with tag chars: 2 chars per byte (50% reduction)."""
        # 95^2 = 9025 >> 256, so 2 chars is enough
        d0 = 255 % 95
        d1 = 255 // 95
        assert d1 < 95  # fits in 2 digits


# ── Size comparison tests ─────────────────────────────────────────────


class TestPayloadSizeComparison:
    """Compare payload sizes between current base-4 and potential tag encodings."""

    PAYLOAD_BYTES = 32  # UUID (16) + HMAC (16) = 32 bytes

    def test_current_base4_signature_size(self):
        """Current: 32 bytes * 4 chars/byte = 128 chars."""
        chars = self.PAYLOAD_BYTES * 4
        assert chars == 128

    def test_tag_base4_signature_size(self):
        """Tag base-4: same char count but more UTF-8 bytes."""
        chars = self.PAYLOAD_BYTES * 4
        utf8_bytes = chars * 4  # each tag char = 4 UTF-8 bytes
        assert chars == 128
        assert utf8_bytes == 512

    def test_tag_base16_signature_size(self):
        """Tag base-16: 32 bytes * 2 chars/byte = 64 chars, 256 UTF-8 bytes."""
        chars = self.PAYLOAD_BYTES * 2
        utf8_bytes = chars * 4
        assert chars == 64
        assert utf8_bytes == 256

    def test_tag_base95_signature_size(self):
        """Tag base-95: 32 bytes * 2 chars/byte = 64 chars, 256 UTF-8 bytes."""
        chars = self.PAYLOAD_BYTES * 2
        utf8_bytes = chars * 4
        assert chars == 64
        assert utf8_bytes == 256

    def test_current_base4_utf8_bytes(self):
        """Current base-4 UTF-8 size: 128 chars * ~2.5 avg bytes."""
        # ZWNJ (U+200C) = 3 bytes, ZWJ (U+200D) = 3 bytes,
        # CGJ (U+034F) = 2 bytes, MVS (U+180E) = 3 bytes
        # Average assuming uniform distribution: (3+3+2+3)/4 = 2.75
        sizes = [len(c.encode("utf-8")) for c in CURRENT_BASE4]
        avg = sum(sizes) / len(sizes)
        total = int(128 * avg)
        # Between 256 (all 2-byte) and 384 (all 3-byte)
        assert 256 <= total <= 384

    def test_tag_base95_is_fewer_chars_than_current(self):
        """Tag base-95 uses 50% fewer characters than current base-4."""
        current_chars = self.PAYLOAD_BYTES * 4  # 128
        tag95_chars = self.PAYLOAD_BYTES * 2  # 64
        assert tag95_chars == current_chars // 2

    def test_tag_base95_utf8_smaller_than_current(self):
        """Tag base-95 may actually use fewer UTF-8 bytes than current base-4.

        Current: 128 chars * 2.75 avg = 352 bytes
        Tag-95:   64 chars * 4.0       = 256 bytes
        => Tag-95 saves ~96 bytes (27% reduction in UTF-8 bytes)
        """
        current_utf8 = sum(len(c.encode("utf-8")) for c in CURRENT_BASE4) / len(CURRENT_BASE4) * 128
        tag95_utf8 = 64 * 4
        assert tag95_utf8 < current_utf8


# ── Character distinctness tests ──────────────────────────────────────


class TestTagCharDistinctness:
    """Ensure tag characters are distinct and won't collide with existing chars."""

    def test_no_overlap_with_current_base4(self):
        """Tag chars must not overlap with current ZWNJ/ZWJ/CGJ/MVS."""
        current_set = set(CURRENT_BASE4)
        tag_set = set(TAG_PRINTABLE)
        assert current_set.isdisjoint(tag_set)

    def test_no_overlap_with_common_invisible_chars(self):
        """Tag chars must not overlap with other known invisible characters."""
        known_invisible = {
            "\u200b",  # ZWSP
            "\u200c",  # ZWNJ
            "\u200d",  # ZWJ
            "\u034f",  # CGJ
            "\u180e",  # MVS
            "\u2060",  # WJ
            "\ufeff",  # BOM/ZWNBSP
            "\u2061",  # Function Application
            "\u2062",  # Invisible Times
            "\u2063",  # Invisible Separator
            "\u2064",  # Invisible Plus
        }
        tag_set = set(TAG_PRINTABLE)
        assert known_invisible.isdisjoint(tag_set)

    def test_all_95_tag_printable_are_unique(self):
        """All 95 tag printable chars are distinct code points."""
        assert len(set(TAG_PRINTABLE)) == 95

    def test_tag_chars_distinguishable_in_python(self):
        """Python string operations can distinguish all tag chars."""
        text = "".join(TAG_PRINTABLE)
        for i, char in enumerate(TAG_PRINTABLE):
            assert text.index(char) == i
            assert text.count(char) == 1


# ── Contiguous detection feasibility ─────────────────────────────────


class TestContiguousDetection:
    """Test that tag char signatures can be detected via contiguous sequence."""

    def test_detect_contiguous_tag_sequence(self):
        """Detect a contiguous run of tag characters in mixed text."""
        visible = "Hello world"
        tag_sig = "".join(TAG_PRINTABLE[:32])  # 32-char tag sequence
        text = visible[:5] + tag_sig + visible[5:]

        # Detection: find longest contiguous run of tag-block chars
        tag_set = set(chr(cp) for cp in range(TAG_BLOCK_START, TAG_BLOCK_END + 1))
        runs = []
        current_run_start = None
        current_run_len = 0

        for i, ch in enumerate(text):
            if ch in tag_set:
                if current_run_start is None:
                    current_run_start = i
                current_run_len += 1
            else:
                if current_run_len > 0:
                    runs.append((current_run_start, current_run_len))
                current_run_start = None
                current_run_len = 0
        if current_run_len > 0:
            runs.append((current_run_start, current_run_len))

        assert len(runs) == 1
        start, length = runs[0]
        assert length == 32
        extracted = text[start : start + length]
        assert extracted == tag_sig

    def test_mixed_tag_and_current_chars_distinguishable(self):
        """Tag chars and current base-4 chars form separate contiguous runs."""
        current_sig = "".join(CURRENT_BASE4 * 8)  # 32 current chars
        tag_sig = "".join(TAG_PRINTABLE[:32])  # 32 tag chars
        visible = "Test sentence"

        text = visible + current_sig + "." + tag_sig + " More text."

        # Count runs of each type
        tag_set = set(chr(cp) for cp in range(TAG_BLOCK_START, TAG_BLOCK_END + 1))
        base4_set = set(CURRENT_BASE4)

        tag_run_count = 0
        base4_run_count = 0
        in_tag = False
        in_base4 = False

        for ch in text:
            if ch in tag_set:
                if not in_tag:
                    tag_run_count += 1
                    in_tag = True
                in_base4 = False
            elif ch in base4_set:
                if not in_base4:
                    base4_run_count += 1
                    in_base4 = True
                in_tag = False
            else:
                in_tag = False
                in_base4 = False

        assert tag_run_count == 1
        assert base4_run_count == 1
