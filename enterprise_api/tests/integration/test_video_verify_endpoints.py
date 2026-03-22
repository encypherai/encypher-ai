"""Integration tests for public POST /api/v1/verify/video endpoint.

Uses the FastAPI TestClient (via httpx ASGITransport) with the real app.
No live PostgreSQL required -- the endpoint does not touch a database.
"""

import copy
import io
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


def _make_mp4_bytes() -> bytes:
    """Return minimal MP4 bytes (ftyp + mdat boxes)."""
    ftyp_data = b"isom" + b"\x00\x00\x00\x00" + b"isom" + b"mp41"
    ftyp = struct.pack(">I", 8 + len(ftyp_data)) + b"ftyp" + ftyp_data
    mdat_data = b"\x00" * 100
    mdat = struct.pack(">I", 8 + len(mdat_data)) + b"mdat" + mdat_data
    return ftyp + mdat


def _upload_video(client, video_bytes: bytes | None = None, mime_type: str = "video/mp4"):
    """Build the multipart payload for video verify."""
    if video_bytes is None:
        video_bytes = _make_mp4_bytes()
    return client.post(
        "/api/v1/verify/video",
        files={"file": ("test.mp4", io.BytesIO(video_bytes), mime_type)},
        data={"mime_type": mime_type},
    )


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
# POST /api/v1/verify/video tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_video_empty_file_returns_400() -> None:
    """Submitting an empty file returns HTTP 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/video",
            files={"file": ("empty.mp4", io.BytesIO(b""), "video/mp4")},
            data={"mime_type": "video/mp4"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_video_unsigned_mp4_returns_200_valid_false() -> None:
    """Posting an unsigned MP4 returns 200 with valid=False (no C2PA manifest)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await _upload_video(client)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["valid"] is False
    assert data["correlation_id"] is not None
    assert data["verified_at"] is not None


@pytest.mark.asyncio
async def test_verify_video_response_shape() -> None:
    """Response includes all expected fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await _upload_video(client)
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
async def test_verify_video_missing_file_returns_422() -> None:
    """Omitting the file returns HTTP 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/video",
            data={"mime_type": "video/mp4"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_video_no_auth_required() -> None:
    """Public video verify does not require authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await _upload_video(client)
    assert response.status_code not in (401, 403)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_video_payload_over_limit_returns_413(monkeypatch) -> None:
    """Video payloads above the configured public size ceiling are rejected."""
    monkeypatch.setattr(settings, "public_video_max_size_bytes", 1)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await _upload_video(client)
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_verify_video_anonymous_rate_limited() -> None:
    """Anonymous verify/video requests are throttled by the public rate limiter."""
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["verify_video"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("127.0.0.1")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r1 = await _upload_video(client)
            assert r1.status_code == 200

            r2 = await _upload_video(client)
            assert r2.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("127.0.0.1")
