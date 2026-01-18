"""Unit tests for fuzzy fingerprint utilities."""

from app.services.fuzzy_fingerprint_service import FuzzyFingerprintService


def test_simhash_similarity_exact_match() -> None:
    service = FuzzyFingerprintService()
    fingerprint = service._simhash(["alpha", "beta"], bits=64)
    similarity = service._similarity(fingerprint, fingerprint, bits=64)
    assert similarity == 1.0


def test_simhash_similarity_differs_for_different_tokens() -> None:
    service = FuzzyFingerprintService()
    left = service._simhash(["alpha", "beta"], bits=64)
    right = service._simhash(["gamma", "delta"], bits=64)
    similarity = service._similarity(left, right, bits=64)
    assert 0.0 <= similarity < 1.0


def test_bucket_uses_high_bits() -> None:
    service = FuzzyFingerprintService()
    fingerprint = int("11110000", 2)
    bucket = service._bucket(fingerprint, bits=8, bucket_bits=4)
    assert bucket == 0b1111
