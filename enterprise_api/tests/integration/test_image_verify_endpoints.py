"""Integration tests for /api/v1/verify/image and /api/v1/verify/rich endpoints.

Uses the FastAPI TestClient (via httpx ASGITransport) with the real app.
Database is overridden with a fake async session to avoid requiring a live
PostgreSQL instance for these lightweight integration checks.
"""
import base64
import io
import os
import sys
import uuid
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
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.main import app


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


# ---------------------------------------------------------------------------
# POST /api/v1/verify/rich tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_rich_unknown_document_id_returns_404() -> None:
    """Unknown document_id returns HTTP 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={"document_id": "doc_doesnotexist"},
        )
    assert response.status_code == 404


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
async def test_verify_rich_404_error_message_contains_document_id() -> None:
    """The 404 response error message references the document_id."""
    doc_id = "doc_xyz_notfound_9999"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify/rich",
            json={"document_id": doc_id},
        )
    assert response.status_code == 404
    body = response.json()
    # Error detail must reference the missing document_id
    detail_str = str(body)
    assert doc_id in detail_str
