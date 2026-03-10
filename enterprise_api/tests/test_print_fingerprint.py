"""Tests for Print Leak Detection (thin-space steganography).

TEAM_217 - enterprise_api/app/utils/print_stego.py

Tests:
  1. encode -> decode roundtrip
  2. build_payload is deterministic
  3. no thin spaces without flag
  4. enterprise tier required (403 for non-enterprise)
  5. short text - graceful no-op
  6. sign response includes payload_hex
  7. verify endpoint detects fingerprint
  8. plain text has no false positive
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)

from app.utils.print_stego import (
    REGULAR_SPACE,
    THIN_SPACE,
    build_payload,
    decode_print_fingerprint,
    encode_print_fingerprint,
)

# --------------------------------------------------------------------------
# 1. Encode -> decode roundtrip
# --------------------------------------------------------------------------


def _long_text(word_count: int = 200) -> str:
    """Return a plain-text article with enough words for the fingerprint."""
    words = ["word"] * word_count
    return " ".join(words)


def test_encode_decode_roundtrip() -> None:
    """Payload survives encode -> decode."""
    text = _long_text(200)
    payload = build_payload("org-abc", "doc-xyz")

    fingerprinted = encode_print_fingerprint(text, payload)
    recovered = decode_print_fingerprint(fingerprinted)

    assert recovered is not None, "decode returned None  - fingerprint not detected"
    assert recovered == payload, f"payload mismatch: {recovered.hex()} != {payload.hex()}"


def test_encode_decode_roundtrip_various_payloads() -> None:
    """Roundtrip works for different org/doc combinations."""
    text = _long_text(300)
    for org, doc in [("org-1", "doc-A"), ("org-2", "doc-B"), ("org-99", "doc-Z")]:
        payload = build_payload(org, doc)
        recovered = decode_print_fingerprint(encode_print_fingerprint(text, payload))
        assert recovered == payload, f"roundtrip failed for ({org}, {doc})"


# --------------------------------------------------------------------------
# 2. build_payload is deterministic
# --------------------------------------------------------------------------


def test_payload_builder_deterministic() -> None:
    """Same org_id + document_id always produces the same 16-byte payload."""
    p1 = build_payload("org-abc", "doc-xyz")
    p2 = build_payload("org-abc", "doc-xyz")
    assert p1 == p2, "build_payload is not deterministic"
    assert len(p1) == 16


def test_payload_builder_different_inputs() -> None:
    """Different inputs produce different payloads."""
    p1 = build_payload("org-1", "doc-1")
    p2 = build_payload("org-2", "doc-1")
    p3 = build_payload("org-1", "doc-2")
    assert p1 != p2
    assert p1 != p3
    assert p2 != p3


# --------------------------------------------------------------------------
# 3. No thin spaces without the fingerprint
# --------------------------------------------------------------------------


def test_no_thin_spaces_in_unfingerprinted_text() -> None:
    """encode_print_fingerprint introduces thin spaces; plain text has none."""
    text = _long_text(200)
    assert THIN_SPACE not in text, "test text already contains THIN_SPACE"

    payload = build_payload("org-abc", "doc-123")
    fingerprinted = encode_print_fingerprint(text, payload)

    assert THIN_SPACE in fingerprinted, "fingerprinted text should contain THIN_SPACE"
    assert fingerprinted != text, "fingerprinted text must differ from original"


# --------------------------------------------------------------------------
# 4. Short text  - graceful no-op
# --------------------------------------------------------------------------


def test_short_text_graceful_noop() -> None:
    """Text too short to carry payload -> returned unmodified, no exception raised."""
    short_text = "This text is far too short."  # < 128 spaces
    payload = build_payload("org-abc", "doc-short")

    result = encode_print_fingerprint(short_text, payload)
    assert result == short_text, "short text should be returned unmodified"
    assert THIN_SPACE not in result


def test_short_text_decode_returns_none() -> None:
    """Trying to decode a short text returns None."""
    short_text = "This text is far too short."
    result = decode_print_fingerprint(short_text)
    assert result is None


# --------------------------------------------------------------------------
# 5. Plain text has no false positive
# --------------------------------------------------------------------------


def test_regular_text_no_false_positive() -> None:
    """Plain text with only regular spaces -> decode returns None."""
    text = _long_text(300)
    assert THIN_SPACE not in text
    result = decode_print_fingerprint(text)
    assert result is None, f"false positive: decode returned {result!r} for plain text"


def test_text_with_exactly_127_spaces_no_false_positive() -> None:
    """Text with exactly 127 spaces (one short of minimum) -> decode returns None."""
    text = " ".join(["word"] * 128)  # 127 spaces
    assert text.count(REGULAR_SPACE) == 127
    result = decode_print_fingerprint(text)
    assert result is None


# --------------------------------------------------------------------------
# 6. Thin-space positions encode bits correctly
# --------------------------------------------------------------------------


def test_encoding_uses_correct_positions() -> None:
    """Verify the bit-level encoding is correct."""
    text = _long_text(200)
    # Use a known payload: first byte = 0b10100000 = 0xA0 = 160
    payload = bytes([0xA0]) + bytes(15)

    fingerprinted = encode_print_fingerprint(text, payload)
    spaces = [c for c in fingerprinted if c in (REGULAR_SPACE, THIN_SPACE)]

    # Bit pattern for 0xA0: 1 0 1 0 0 0 0 0
    expected_bits = [1, 0, 1, 0, 0, 0, 0, 0]
    for i, expected in enumerate(expected_bits):
        actual = 1 if spaces[i] == THIN_SPACE else 0
        assert actual == expected, f"bit {i}: expected {expected}, got {actual}"

    # Remaining 15 bytes are all 0 -> all remaining spaces should be REGULAR_SPACE
    for i in range(8, 128):
        assert spaces[i] == REGULAR_SPACE, f"space {i}: expected REGULAR_SPACE, got THIN_SPACE"


# --------------------------------------------------------------------------
# 7. Enterprise tier required via API (mock-based)
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_enterprise_tier_required_for_print_fingerprint() -> None:
    """enable_print_fingerprint=True on a free-tier org returns 403."""
    from httpx import ASGITransport, AsyncClient

    from app.dependencies import get_current_organization_dep, require_sign_permission
    from app.main import app

    free_org: dict[str, Any] = {
        "organization_id": "org-free",
        "tier": "free",
        "can_sign": True,
        "can_verify": True,
        "nma_member": False,
        "features": {},
    }

    app.dependency_overrides[require_sign_permission] = lambda: free_org
    app.dependency_overrides[get_current_organization_dep] = lambda: free_org

    try:
        with (
            patch("app.routers.signing.ensure_organization_exists", new_callable=AsyncMock),
            patch("app.routers.signing.QuotaManager.check_quota", new_callable=AsyncMock),
            patch("app.routers.signing.QuotaManager.get_quota_headers", new_callable=AsyncMock, return_value={}),
            patch("app.middleware.api_rate_limiter.api_rate_limiter.check_with_reset") as mock_rate,
            patch("app.middleware.api_rate_limiter.api_rate_limiter.get_headers", return_value={}),
        ):
            from app.middleware.api_rate_limiter import RateLimitResult

            mock_rate.return_value = RateLimitResult(allowed=True, retry_after=None, remaining=99, limit=100, reset_at=0)

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/sign",
                    json={
                        "text": _long_text(200),
                        "options": {"enable_print_fingerprint": True},
                    },
                    headers={"X-API-Key": "test-key"},
                )

        assert response.status_code == 403, f"expected 403 for free tier, got {response.status_code}: {response.text}"
        body = response.json()
        # Verify the error message mentions print fingerprint / Enterprise
        error = body.get("error", {})
        message = error.get("message", "")
        assert (
            "Print Leak Detection" in message or "enterprise" in message.lower() or "tier" in message.lower()
        ), f"expected enterprise tier error, got: {message}"
    finally:
        app.dependency_overrides.clear()
