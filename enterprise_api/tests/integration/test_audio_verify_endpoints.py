"""Integration tests for public POST /api/v1/verify/audio endpoint.

Uses the FastAPI TestClient (via httpx ASGITransport) with the real app.
No live PostgreSQL required -- the endpoint does not touch a database.
"""

import base64
import copy
import os
import struct
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg:///encypher_test_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg:///encypher_test_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_content_db, get_db
from app.main import app
from app.middleware.public_rate_limiter import public_rate_limiter


def _make_wav_b64() -> str:
    """Return a base64-encoded minimal WAV file."""
    fmt_data = struct.pack("<HHIIHH", 1, 1, 44100, 44100, 1, 8)
    fmt_chunk = b"fmt " + struct.pack("<I", len(fmt_data)) + fmt_data
    audio_data = b"\x80" * 100
    data_chunk = b"data" + struct.pack("<I", len(audio_data)) + audio_data
    riff_body = b"WAVE" + fmt_chunk + data_chunk
    wav_bytes = b"RIFF" + struct.pack("<I", len(riff_body)) + riff_body
    return base64.b64encode(wav_bytes).decode()


@pytest.fixture(autouse=True)
def _override_db():
    """Override database dependencies for all tests in this module."""

    async def _empty_core_db():
        session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        yield session

    async def _empty_content_db():
        session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        session.execute = AsyncMock(return_value=mock_result)
        yield session

    app.dependency_overrides[get_db] = _empty_core_db
    app.dependency_overrides[get_content_db] = _empty_content_db
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/v1/verify/audio tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_audio_invalid_base64_returns_400() -> None:
    """Submitting invalid base64 data returns HTTP 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": "!!NOT_VALID_BASE64!!", "mime_type": "audio/wav"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_audio_empty_data_returns_400() -> None:
    """Submitting empty audio_data returns HTTP 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": "", "mime_type": "audio/wav"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_audio_unsigned_wav_returns_200_valid_false() -> None:
    """Posting an unsigned WAV returns 200 with valid=False (no C2PA manifest)."""
    wav_b64 = _make_wav_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": wav_b64, "mime_type": "audio/wav"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["valid"] is False
    assert data["correlation_id"] is not None
    assert data["verified_at"] is not None


@pytest.mark.asyncio
async def test_verify_audio_response_shape() -> None:
    """Response includes all expected fields."""
    wav_b64 = _make_wav_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": wav_b64, "mime_type": "audio/wav"},
        )
    data = response.json()
    expected_keys = {
        "success",
        "valid",
        "c2pa_manifest_valid",
        "hash_matches",
        "c2pa_instance_id",
        "signer",
        "signed_at",
        "manifest_data",
        "error",
        "correlation_id",
        "verified_at",
    }
    assert expected_keys.issubset(set(data.keys()))


@pytest.mark.asyncio
async def test_verify_audio_missing_audio_data_returns_422() -> None:
    """Omitting audio_data returns HTTP 422 (Unprocessable Entity)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"mime_type": "audio/wav"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_audio_no_auth_required() -> None:
    """Public audio verify does not require authentication."""
    wav_b64 = _make_wav_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": wav_b64, "mime_type": "audio/wav"},
        )
    # Should NOT be 401 or 403
    assert response.status_code not in (401, 403)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_audio_payload_over_limit_returns_413(monkeypatch) -> None:
    """Audio payloads above the configured public size ceiling are rejected."""
    wav_b64 = _make_wav_b64()
    monkeypatch.setattr(settings, "public_audio_max_size_bytes", 1)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/audio",
            json={"audio_data": wav_b64, "mime_type": "audio/wav"},
        )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_verify_audio_anonymous_rate_limited() -> None:
    """Anonymous verify/audio requests are throttled by the public rate limiter."""
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["verify_audio"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("127.0.0.1")
        wav_b64 = _make_wav_b64()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # First request should succeed
            r1 = await client.post(
                "/api/v1/verify/audio",
                json={"audio_data": wav_b64, "mime_type": "audio/wav"},
            )
            assert r1.status_code == 200

            # Second request should be rate limited
            r2 = await client.post(
                "/api/v1/verify/audio",
                json={"audio_data": wav_b64, "mime_type": "audio/wav"},
            )
            assert r2.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("127.0.0.1")
