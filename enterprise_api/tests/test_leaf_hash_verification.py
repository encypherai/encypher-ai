"""Tests for leaf_hash verification in the micro embedding DB resolution path.

TEAM_272: Verifies that _resolve_uuids_from_db checks the stored leaf_hash
against a recomputed SHA-256 of the submitted sentence text, rejecting content
where the HMAC passes but the full hash does not match.
"""

from __future__ import annotations

import hashlib
import unicodedata
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.verification_logic import _resolve_uuids_from_db
from app.utils.merkle.hashing import compute_leaf_hash
from app.utils.vs256_crypto import (
    create_signed_marker,
    derive_signing_key_from_private_key,
    embed_signature_safely,
    generate_log_id,
)


def _build_signed_text(sentence: str, signing_key: bytes, log_id: bytes) -> str:
    """Create a text payload with a VS256 marker embedded in the given sentence."""
    sig = create_signed_marker(log_id, signing_key, sentence_text=sentence)
    return f"Intro. {embed_signature_safely(sentence, sig)} Outro."


def _make_db_row(
    *,
    organization_id: str = "org_test",
    document_id: str = "doc_123",
    leaf_index: int = 0,
    manifest_mode: str = "micro",
    segment_location: None = None,
    total_segments: int = 1,
    manifest_data: None = None,
    leaf_hash: str | None = None,
) -> SimpleNamespace:
    """Build a fake DB row matching the _RESOLVE_UUID_SQL SELECT columns."""
    return SimpleNamespace(
        organization_id=organization_id,
        document_id=document_id,
        leaf_index=leaf_index,
        manifest_mode=manifest_mode,
        segment_location=segment_location,
        total_segments=total_segments,
        manifest_data=manifest_data,
        leaf_hash=leaf_hash,
    )


@pytest.fixture
def signing_key() -> bytes:
    return b"test_signing_key_32_bytes_long!!"


@pytest.fixture
def private_key():
    """Create a minimal Ed25519 private key for testing."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.generate()


@pytest.fixture
def derived_key(private_key) -> bytes:
    return derive_signing_key_from_private_key(private_key)


@pytest.mark.asyncio
async def test_leaf_hash_match_passes_verification(private_key, derived_key) -> None:
    """When HMAC passes AND leaf_hash matches, is_valid should be True."""
    sentence = "The quick brown fox jumps over the lazy dog."
    log_id = generate_log_id()
    payload_text = _build_signed_text(sentence, derived_key, log_id)
    expected_hash = compute_leaf_hash(sentence)

    row = _make_db_row(leaf_hash=expected_hash)

    mock_content_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = row
    mock_content_session.execute = AsyncMock(return_value=mock_result)

    mock_core_session = AsyncMock()

    with patch(
        "app.utils.crypto_utils.load_organization_private_key",
        new_callable=AsyncMock,
        return_value=private_key,
    ):
        result = await _resolve_uuids_from_db(
            payload_text=payload_text,
            content_db=mock_content_session,
            core_db=mock_core_session,
        )

    assert result is not None
    assert result["is_valid"] is True
    assert result["manifest"]["leaf_hash_verified"] is True


@pytest.mark.asyncio
async def test_leaf_hash_mismatch_fails_verification(private_key, derived_key) -> None:
    """When HMAC passes but leaf_hash does NOT match, is_valid should be False."""
    sentence = "The quick brown fox jumps over the lazy dog."
    log_id = generate_log_id()
    payload_text = _build_signed_text(sentence, derived_key, log_id)

    # Store a leaf_hash for DIFFERENT content than what the text actually contains
    wrong_hash = compute_leaf_hash("Completely different sentence content.")
    row = _make_db_row(leaf_hash=wrong_hash)

    mock_content_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = row
    mock_content_session.execute = AsyncMock(return_value=mock_result)

    mock_core_session = AsyncMock()

    with patch(
        "app.utils.crypto_utils.load_organization_private_key",
        new_callable=AsyncMock,
        return_value=private_key,
    ):
        result = await _resolve_uuids_from_db(
            payload_text=payload_text,
            content_db=mock_content_session,
            core_db=mock_core_session,
        )

    assert result is not None
    assert result["is_valid"] is False
    assert result["manifest"]["leaf_hash_verified"] is False


@pytest.mark.asyncio
async def test_missing_leaf_hash_skips_check(private_key, derived_key) -> None:
    """When DB row has no leaf_hash (old data), skip the check -- backward compat."""
    sentence = "Legacy content without per-sentence hashing."
    log_id = generate_log_id()
    payload_text = _build_signed_text(sentence, derived_key, log_id)

    row = _make_db_row(leaf_hash=None)

    mock_content_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = row
    mock_content_session.execute = AsyncMock(return_value=mock_result)

    mock_core_session = AsyncMock()

    with patch(
        "app.utils.crypto_utils.load_organization_private_key",
        new_callable=AsyncMock,
        return_value=private_key,
    ):
        result = await _resolve_uuids_from_db(
            payload_text=payload_text,
            content_db=mock_content_session,
            core_db=mock_core_session,
        )

    assert result is not None
    # HMAC passed, no leaf_hash to check -> still valid
    assert result["is_valid"] is True
    assert result["manifest"].get("leaf_hash_verified") is None


@pytest.mark.asyncio
async def test_leaf_hash_verified_flag_in_manifest(private_key, derived_key) -> None:
    """The manifest dict should contain leaf_hash_verified when the check runs."""
    sentence = "Provenance matters for trust."
    log_id = generate_log_id()
    payload_text = _build_signed_text(sentence, derived_key, log_id)
    expected_hash = compute_leaf_hash(sentence)

    row = _make_db_row(leaf_hash=expected_hash)

    mock_content_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = row
    mock_content_session.execute = AsyncMock(return_value=mock_result)

    mock_core_session = AsyncMock()

    with patch(
        "app.utils.crypto_utils.load_organization_private_key",
        new_callable=AsyncMock,
        return_value=private_key,
    ):
        result = await _resolve_uuids_from_db(
            payload_text=payload_text,
            content_db=mock_content_session,
            core_db=mock_core_session,
        )

    assert result is not None
    assert "leaf_hash_verified" in result["manifest"]
    assert result["manifest"]["leaf_hash_verified"] is True
