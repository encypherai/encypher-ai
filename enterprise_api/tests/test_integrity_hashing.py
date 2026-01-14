import unicodedata

from app.utils.merkle import compute_leaf_hash
from app.utils.sentence_parser import compute_sentence_hash, compute_text_hash


def test_leaf_hash_is_case_sensitive() -> None:
    assert compute_leaf_hash("Hello") != compute_leaf_hash("hello")


def test_leaf_hash_is_nfc_normalized() -> None:
    composed = "café"
    decomposed = "cafe\u0301"

    assert unicodedata.normalize("NFC", composed) == unicodedata.normalize("NFC", decomposed)
    assert compute_leaf_hash(composed) == compute_leaf_hash(decomposed)


def test_sign_hashes_are_nfc_normalized_and_case_sensitive() -> None:
    composed = "café"
    decomposed = "cafe\u0301"

    assert compute_text_hash(composed) == compute_text_hash(decomposed)
    assert compute_sentence_hash(composed) == compute_sentence_hash(decomposed)

    assert compute_text_hash("Hello") != compute_text_hash("hello")
    assert compute_sentence_hash("Hello") != compute_sentence_hash("hello")
