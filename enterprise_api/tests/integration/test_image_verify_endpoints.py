"""Integration tests for /api/v1/verify/image and /api/v1/verify/rich endpoints.

Uses the FastAPI TestClient (via httpx ASGITransport) with the real app.
Database is overridden with a fake async session to avoid requiring a live
PostgreSQL instance for these lightweight integration checks.
"""

import base64
import copy
import hashlib
import io
import json
import os
import sys
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

# Ensure enterprise_api root is on the path before any app imports
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
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_content_db, get_db
from app.main import app
from app.middleware.public_rate_limiter import public_rate_limiter


def _make_jpeg_b64(width: int = 10, height: int = 10) -> str:
    """Return a base64-encoded minimal JPEG."""
    img = Image.new("RGB", (width, height), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def _make_empty_content_db_override():
    """Return an async generator that yields a mock content DB returning no rows."""

    async def _override() -> AsyncGenerator:
        session = MagicMock(spec=AsyncSession)
        # execute() returns a result whose scalar_one_or_none() is None
        # and scalars().all() is an empty list
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        mock_result.scalars.return_value = scalars_mock
        session.execute = AsyncMock(return_value=mock_result)
        yield session

    return _override


@pytest.fixture(autouse=True)
def _override_db():
    """Override both database dependencies for all tests in this module."""

    async def _empty_core_db():
        session = MagicMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        yield session

    app.dependency_overrides[get_db] = _empty_core_db
    app.dependency_overrides[get_content_db] = _make_empty_content_db_override()
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/v1/verify/image tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_image_invalid_base64_returns_400() -> None:
    """Submitting invalid base64 data returns HTTP 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": "!!NOT_VALID_BASE64!!", "mime_type": "image/jpeg"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_verify_image_unsigned_jpeg_returns_200_valid_false() -> None:
    """Posting an unsigned JPEG returns 200 with valid=False (no C2PA manifest)."""
    jpeg_b64 = _make_jpeg_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["valid"] is False
    assert data["cryptographically_verified"] is False
    assert data["db_matched"] is False
    assert data["historically_signed_by_us"] is False
    assert data["overall_status"] == "invalid"
    assert data["c2pa_manifest"] is None
    assert data["correlation_id"] is not None
    assert data["verified_at"] is not None


@pytest.mark.asyncio
async def test_verify_image_response_contains_hash() -> None:
    """Response includes a sha256 hash of the submitted image."""
    jpeg_b64 = _make_jpeg_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
        )
    data = response.json()
    assert data["hash"] is not None
    assert data["hash"].startswith("sha256:")


@pytest.mark.asyncio
async def test_verify_image_missing_image_data_returns_422() -> None:
    """Omitting image_data returns HTTP 422 (Unprocessable Entity)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"mime_type": "image/jpeg"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_image_no_db_record_image_id_is_null() -> None:
    """When image is not in DB, image_id and document_id are None."""
    jpeg_b64 = _make_jpeg_b64()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
        )
    data = response.json()
    assert data["image_id"] is None
    assert data["document_id"] is None
    assert data["phash"] is None


@pytest.mark.asyncio
async def test_verify_image_payload_over_limit_returns_413(monkeypatch) -> None:
    """Image payloads above the configured size ceiling are rejected."""
    jpeg_b64 = _make_jpeg_b64()
    monkeypatch.setattr(settings, "image_max_size_bytes", 1)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
        )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_verify_image_anonymous_rate_limited() -> None:
    """Anonymous verify/image requests are throttled by the public rate limiter."""
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["verify_image"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("127.0.0.1")
        jpeg_b64 = _make_jpeg_b64()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.post(
                "/api/v1/verify/image",
                json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
            )
            second = await client.post(
                "/api/v1/verify/image",
                json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
            )

        assert first.status_code == 200
        assert second.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("127.0.0.1")


@pytest.mark.asyncio
async def test_verify_image_minimal_response_hides_metadata(monkeypatch) -> None:
    """Minimal-response mode hides public image metadata while preserving the verdict."""
    jpeg_b64 = _make_jpeg_b64()
    monkeypatch.setattr(settings, "public_verify_minimal_response", True)

    fake_result = MagicMock()
    fake_result.valid = True
    fake_result.manifest_data = {"manifest": "data"}
    fake_result.error = None
    monkeypatch.setattr("app.api.v1.image_verify.verify_image_c2pa", lambda *_args, **_kwargs: fake_result)

    async def _image_db_override():
        session = MagicMock(spec=AsyncSession)
        row = MagicMock()
        row.image_id = "img_123"
        row.document_id = "doc_123"
        row.phash = int("deadbeefdeadbeef", 16)
        first_result = MagicMock()
        first_result.scalar_one_or_none.return_value = row
        session.execute = AsyncMock(return_value=first_result)
        yield session

    app.dependency_overrides[get_content_db] = _image_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/image",
            json={"image_data": jpeg_b64, "mime_type": "image/jpeg"},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["valid"] is True
    assert data["c2pa_manifest"] is None
    assert data["image_id"] is None
    assert data["document_id"] is None
    assert data["phash"] is None
    assert data["hash"] is not None


# ---------------------------------------------------------------------------
# POST /api/v1/verify/rich tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_rich_unknown_document_id_returns_generic_invalid_response() -> None:
    """Unknown document_id returns a generic invalid verification response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={"document_id": "doc_doesnotexist"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["overall_status"] == "invalid"
    assert body["error"] == "Unable to verify requested article"


@pytest.mark.asyncio
async def test_verify_rich_missing_document_id_returns_422() -> None:
    """Omitting document_id returns HTTP 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_rich_unknown_document_id_error_does_not_echo_identifier() -> None:
    """Unknown rich verification responses do not echo the identifier in the error message."""
    doc_id = "doc_xyz_notfound_9999"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={"document_id": doc_id},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] == "Unable to verify requested article"
    assert doc_id not in body["error"]


@pytest.mark.asyncio
async def test_verify_rich_minimal_response_hides_metadata(monkeypatch) -> None:
    """Minimal-response mode hides signer and image metadata on public rich verification."""
    monkeypatch.setattr(settings, "public_verify_minimal_response", True)

    manifest_data = {"title": "signed article"}
    manifest_json = json.dumps(manifest_data, sort_keys=True, separators=(",", ":"))

    composite_row = MagicMock()
    composite_row.document_id = "doc_rich_123"
    composite_row.manifest_data = manifest_data
    composite_row.manifest_hash = "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest()
    composite_row.organization_id = "org_demo"

    image_row = MagicMock()
    image_row.image_id = "img_123"
    image_row.filename = "photo.jpg"
    image_row.signed_hash = "sha256:abc"
    image_row.c2pa_instance_id = "urn:uuid:test"

    async def _rich_db_override():
        session = MagicMock(spec=AsyncSession)
        composite_result = MagicMock()
        composite_result.scalar_one_or_none.return_value = composite_row
        images_result = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [image_row]
        images_result.scalars.return_value = scalars_mock
        session.execute = AsyncMock(side_effect=[composite_result, images_result])
        yield session

    app.dependency_overrides[get_content_db] = _rich_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={"document_id": "doc_rich_123"},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["valid"] is True
    assert data["signer_identity"] is None
    assert len(data["image_verifications"]) == 1
    assert data["image_verifications"][0]["image_id"] is None
    assert data["image_verifications"][0]["filename"] is None
    assert data["image_verifications"][0]["c2pa_instance_id"] is None


@pytest.mark.asyncio
async def test_verify_rich_anonymous_rate_limited() -> None:
    """Anonymous verify/rich requests are throttled by the public rate limiter."""
    original_limits = copy.deepcopy(public_rate_limiter.ENDPOINT_LIMITS)
    try:
        public_rate_limiter.ENDPOINT_LIMITS["verify_rich"] = {
            "requests_per_hour": 1,
            "window_seconds": 60,
        }
        public_rate_limiter.reset_ip("127.0.0.1")
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.post(
                "/api/v1/verify/rich",
                json={"document_id": "doc_doesnotexist"},
            )
            second = await client.post(
                "/api/v1/verify/rich",
                json={"document_id": "doc_doesnotexist"},
            )

        assert first.status_code == 200
        assert second.status_code == 429
    finally:
        public_rate_limiter.ENDPOINT_LIMITS = original_limits
        public_rate_limiter.reset_ip("127.0.0.1")
