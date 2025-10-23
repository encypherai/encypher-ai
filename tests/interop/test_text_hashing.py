import hashlib
import unicodedata

import pytest

from encypher.interop.c2pa.text_hashing import compute_normalized_hash, normalize_text


def test_compute_normalized_hash_normalizes_text():
    text = "e\u0301clair"  # contains combining accent
    result = compute_normalized_hash(text)

    expected_normalized = unicodedata.normalize("NFC", text)
    expected_hash = hashlib.sha256(expected_normalized.encode("utf-8")).hexdigest()

    assert result.normalized_text == expected_normalized
    assert result.filtered_text == expected_normalized
    assert result.hexdigest == expected_hash


def test_compute_normalized_hash_with_exclusion_removes_wrapper():
    visible = "C2PA document"
    wrapper = "\ufeff" + "".join(chr(0xFE00 + i) for i in range(4))
    full_text = visible + wrapper

    normalized_full = normalize_text(full_text)
    wrapper_index = normalized_full.rfind(wrapper)
    assert wrapper_index >= 0

    exclusion_start = len(normalized_full[:wrapper_index].encode("utf-8"))
    exclusion_length = len(wrapper.encode("utf-8"))

    result = compute_normalized_hash(full_text, [(exclusion_start, exclusion_length)])

    expected_clean = normalize_text(visible)
    expected_hash = hashlib.sha256(expected_clean.encode("utf-8")).hexdigest()

    assert result.filtered_text == expected_clean
    assert result.hexdigest == expected_hash


def test_compute_normalized_hash_rejects_invalid_exclusions():
    text = "sample"
    with pytest.raises(ValueError):
        compute_normalized_hash(text, [(-1, 2)])
    with pytest.raises(ValueError):
        compute_normalized_hash(text, [(0, -2)])
    with pytest.raises(ValueError):
        compute_normalized_hash(text, [(0, 10)])
    with pytest.raises(ValueError):
        compute_normalized_hash(text, [(0, 3), (2, 1)])
