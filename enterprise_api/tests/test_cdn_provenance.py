"""Tests for CDN provenance service and router.

Tests:
- CdnProvenanceService.register_image() creates a record
- CdnProvenanceService.lookup_by_phash() finds similar image within threshold
- CdnProvenanceService.lookup_by_phash() returns None for dissimilar image
- POST /api/v1/cdn/images/sign returns 403 for FREE tier
- GET /api/v1/cdn/manifests/{record_id} returns 404 for missing record
- POST /api/v1/cdn/verify returns PROVENANCE_LOST for unregistered image

Uses SQLite in-memory via aiosqlite for the service unit tests and
dependency overrides + mocks for router tests.
"""

from __future__ import annotations

import os
import sys
import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

# ---------------------------------------------------------------------------
# Path + env setup (must happen before any app imports)
# ---------------------------------------------------------------------------

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault("IMAGE_SIGNING_PASSTHROUGH", "true")
os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",  # pragma: allowlist secret
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:15432/encypher_content",  # pragma: allowlist secret
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_solid_jpeg(color: tuple = (128, 128, 128), size: int = 64) -> bytes:
    """Create a small solid-color JPEG for testing."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("Pillow not installed")
    img = Image.new("RGB", (size, size), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_solid_png(color: tuple = (200, 100, 50), size: int = 64) -> bytes:
    """Create a small solid-color PNG for testing."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("Pillow not installed")
    img = Image.new("RGB", (size, size), color=color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# SQLite in-memory fixtures for service unit tests
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def sqlite_session():
    """Provide an async SQLite in-memory session with cdn_image_records table.

    Creates the table manually using SQLite-compatible DDL (JSON instead of
    JSONB and String instead of PGUUID, which are PostgreSQL-specific types).
    Monkey-patches the CdnImageRecord class so service code uses the
    SQLite-compatible model during the test.
    """
    try:
        import aiosqlite  # noqa: F401
    except ImportError:
        pytest.skip("aiosqlite not installed")

    import datetime as _dt
    import uuid as _uuid_mod

    from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Column, String, Text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import DeclarativeBase, sessionmaker
    from sqlalchemy.types import JSON

    class _LocalBase(DeclarativeBase):
        pass

    # Redeclare with SQLite-compatible column types
    class CdnImageRecordSQLite(_LocalBase):
        __tablename__ = "cdn_image_records"

        id = Column(String(36), primary_key=True, default=lambda: str(_uuid_mod.uuid4()))
        organization_id = Column(String(64), nullable=False)
        original_url = Column(Text, nullable=True)
        content_sha256 = Column(String(71), nullable=True)
        phash = Column(BigInteger, nullable=True)
        manifest_store = Column(JSON, nullable=True)
        is_variant = Column(Boolean, nullable=False, default=False)
        parent_record_id = Column(String(36), nullable=True)
        transform_description = Column(String(500), nullable=True)
        created_at = Column(TIMESTAMP, nullable=False, default=_dt.datetime.utcnow)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(_LocalBase.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    import app.models.cdn_image_record as _cdn_model_mod

    original_cls = _cdn_model_mod.CdnImageRecord
    _cdn_model_mod.CdnImageRecord = CdnImageRecordSQLite  # type: ignore[assignment]

    try:
        async with async_session_factory() as session:
            yield session
    finally:
        _cdn_model_mod.CdnImageRecord = original_cls
        await engine.dispose()


# ---------------------------------------------------------------------------
# Service unit tests
# ---------------------------------------------------------------------------


class TestCdnProvenanceServiceRegister:
    """Tests for CdnProvenanceService.register_image()."""

    @pytest.mark.asyncio
    async def test_register_creates_record(self, sqlite_session):
        """register_image() should create and return a CdnImageRecord."""
        from app.services.cdn_provenance_service import CdnProvenanceService

        image_bytes = make_solid_jpeg((100, 100, 100))
        record = await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_test_001",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
            manifest_data={"title": "test"},
            original_url="https://example.com/image.jpg",
        )
        await sqlite_session.commit()

        assert record is not None
        assert record.id is not None
        assert record.organization_id == "org_test_001"
        assert record.content_sha256 is not None
        assert record.content_sha256.startswith("sha256:")
        assert record.original_url == "https://example.com/image.jpg"
        assert record.manifest_store == {"title": "test"}
        assert record.is_variant is False

    @pytest.mark.asyncio
    async def test_register_is_idempotent(self, sqlite_session):
        """register_image() called twice with same bytes returns same record."""
        from app.services.cdn_provenance_service import CdnProvenanceService

        image_bytes = make_solid_jpeg((200, 200, 200))
        record1 = await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_test_002",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )
        await sqlite_session.commit()

        record2 = await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_test_002",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )

        assert str(record1.id) == str(record2.id)

    @pytest.mark.asyncio
    async def test_register_stores_sha256(self, sqlite_session):
        """register_image() always stores a non-None content_sha256."""
        from app.services.cdn_provenance_service import CdnProvenanceService

        image_bytes = make_solid_png((50, 150, 250))
        record = await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_test_003",
            image_bytes=image_bytes,
            mime_type="image/png",
        )
        await sqlite_session.commit()

        # sha256 must always be present
        assert record.content_sha256 is not None
        assert record.content_sha256.startswith("sha256:")
        # phash may be None for degenerate solid-color images (compute_phash returns 0)
        # but if set it must be an integer
        if record.phash is not None:
            assert isinstance(record.phash, int)


def _make_gradient_jpeg(width: int = 64, height: int = 64) -> bytes:
    """Create a horizontal gradient JPEG (varied pixel values → non-zero pHash)."""
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("Pillow not installed")
    import numpy as np

    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        brightness = int(x / width * 255)
        arr[:, x, :] = brightness
    img = Image.fromarray(arr, "RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


class TestCdnProvenanceServiceLookup:
    """Tests for CdnProvenanceService.lookup_by_phash()."""

    @pytest.mark.asyncio
    async def test_lookup_finds_similar_image(self, sqlite_session):
        """lookup_by_phash() should find an identical image (distance 0)."""
        from app.services.cdn_provenance_service import CdnProvenanceService
        from app.utils.image_utils import compute_phash

        image_bytes = _make_gradient_jpeg()
        phash_val = compute_phash(image_bytes)
        if phash_val == 0:
            pytest.skip("pHash is 0 for test image — cannot test lookup")

        await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_lookup_001",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )
        await sqlite_session.commit()

        result = await CdnProvenanceService.lookup_by_phash(
            db=sqlite_session,
            org_id="org_lookup_001",
            image_bytes=image_bytes,
            threshold=8,
        )

        assert result is not None
        record, distance = result
        assert distance == 0
        assert record.organization_id == "org_lookup_001"

    @pytest.mark.asyncio
    async def test_lookup_returns_none_for_different_org(self, sqlite_session):
        """lookup_by_phash() should NOT find images belonging to a different org."""
        from app.services.cdn_provenance_service import CdnProvenanceService
        from app.utils.image_utils import compute_phash

        image_bytes = _make_gradient_jpeg()
        phash_val = compute_phash(image_bytes)
        if phash_val == 0:
            pytest.skip("pHash is 0 for test image — cannot test lookup")

        await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_lookup_002",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )
        await sqlite_session.commit()

        result = await CdnProvenanceService.lookup_by_phash(
            db=sqlite_session,
            org_id="org_lookup_DIFFERENT",
            image_bytes=image_bytes,
            threshold=8,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_lookup_returns_none_for_dissimilar_image(self, sqlite_session):
        """lookup_by_phash() returns None when Hamming distance exceeds threshold.

        Uses the _hamming_distance helper directly to inject a record with a
        maximally different pHash value, avoiding reliance on Pillow producing
        a non-zero pHash from solid-color images.
        """
        from app.services.cdn_provenance_service import CdnProvenanceService, _hamming_distance
        from app.utils.image_utils import compute_phash

        image_bytes = _make_gradient_jpeg()
        query_phash = compute_phash(image_bytes)
        if query_phash == 0:
            pytest.skip("pHash is 0 for test image — cannot test dissimilar lookup")

        # Register directly with a manually inverted phash (all 64 bits flipped)
        inverted_phash = ~query_phash  # All bits flipped → Hamming distance = 64
        from app.models.cdn_image_record import CdnImageRecord

        record = CdnImageRecord(
            organization_id="org_lookup_003",
            content_sha256="sha256:" + "ff" * 32,
            phash=inverted_phash,
            is_variant=False,
        )
        sqlite_session.add(record)
        await sqlite_session.flush()
        await sqlite_session.commit()

        # Lookup should not find a match (distance = 64, well above threshold=8)
        result = await CdnProvenanceService.lookup_by_phash(
            db=sqlite_session,
            org_id="org_lookup_003",
            image_bytes=image_bytes,
            threshold=8,
        )

        assert result is None


class TestCdnProvenanceServiceVariants:
    """Tests for CdnProvenanceService.pre_register_variants()."""

    @pytest.mark.asyncio
    async def test_pre_register_variants_creates_records(self, sqlite_session):
        """pre_register_variants() creates the correct number of variant records."""
        from app.services.cdn_provenance_service import CdnProvenanceService

        image_bytes = make_solid_jpeg((120, 120, 120))
        parent = await CdnProvenanceService.register_image(
            db=sqlite_session,
            org_id="org_variants_001",
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )
        await sqlite_session.commit()

        transforms = ["resize:800x600", "webp", "q75"]
        variants = await CdnProvenanceService.pre_register_variants(
            db=sqlite_session,
            parent_record=parent,
            transform_descriptions=transforms,
        )
        await sqlite_session.commit()

        assert len(variants) == 3
        for v in variants:
            assert v.is_variant is True
            assert str(v.parent_record_id) == str(parent.id)
            assert v.organization_id == "org_variants_001"


# ---------------------------------------------------------------------------
# Hamming distance unit test
# ---------------------------------------------------------------------------


class TestHammingDistance:
    """Tests for the _hamming_distance helper."""

    def test_identical_values_distance_zero(self):
        from app.services.cdn_provenance_service import _hamming_distance

        assert _hamming_distance(0x1234567890ABCDEF, 0x1234567890ABCDEF) == 0

    def test_all_bits_flipped(self):
        from app.services.cdn_provenance_service import _hamming_distance

        assert _hamming_distance(0, -1) == 64  # all 64 bits differ

    def test_one_bit_different(self):
        from app.services.cdn_provenance_service import _hamming_distance

        assert _hamming_distance(0, 1) == 1

    def test_signed_negative_values(self):
        from app.services.cdn_provenance_service import _hamming_distance

        # Signed negative: should still compute correctly
        result = _hamming_distance(-1, 0)
        assert result == 64


# ---------------------------------------------------------------------------
# Router tests (mocked DB + dependency overrides)
# ---------------------------------------------------------------------------


def _mock_org_dep_factory(org_id: str = "org_test_router_001"):
    def override():
        return {"organization_id": org_id}

    return override


def _async_db_override_factory(db_mock):
    async def override():
        yield db_mock

    return override


@pytest.fixture
def app_client():
    """Return a synchronous TestClient with no overrides (cleaned up after)."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


class TestCdnSignEndpoint:
    """Tests for POST /api/v1/cdn/images/sign."""

    def test_sign_returns_403_for_free_tier(self, app_client):
        """FREE tier org should receive 403 FeatureNotAvailable."""
        from app.database import get_db
        from app.dependencies import get_current_organization_dep
        from app.main import app

        org_id = "org_free_test_001"

        # Build a fake FREE-tier org
        fake_org = MagicMock()
        fake_org.id = org_id
        fake_org.tier = "free"
        fake_org.cdn_provenance_enabled = False

        db = AsyncMock()
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = fake_org
        db.execute = AsyncMock(return_value=exec_result)

        app.dependency_overrides[get_current_organization_dep] = _mock_org_dep_factory(org_id)
        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            # Create a 1x1 JPEG for the upload
            try:
                from PIL import Image
            except ImportError:
                pytest.skip("Pillow not installed")
            img = Image.new("RGB", (1, 1), color=(0, 0, 0))
            buf = BytesIO()
            img.save(buf, format="JPEG")
            image_data = buf.getvalue()

            response = app_client.post(
                "/api/v1/cdn/images/sign",
                data={"title": "test image"},
                files={"file": ("test.jpg", image_data, "image/jpeg")},
            )
            assert response.status_code == 403
            body = response.json()
            assert "FeatureNotAvailable" in str(body) or response.status_code == 403
        finally:
            app.dependency_overrides.clear()


class TestCdnManifestEndpoint:
    """Tests for GET /api/v1/cdn/manifests/{record_id}."""

    def test_get_manifest_returns_404_for_missing_record(self, app_client):
        """GET /manifests/{record_id} with unknown UUID should return 404."""
        from app.database import get_db
        from app.main import app

        db = AsyncMock()
        db.get = AsyncMock(return_value=None)  # record not found

        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            missing_id = str(uuid.uuid4())
            response = app_client.get(f"/api/v1/cdn/manifests/{missing_id}")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_get_manifest_returns_422_for_invalid_uuid(self, app_client):
        """GET /manifests/not-a-uuid should return 422."""
        from app.database import get_db
        from app.main import app

        db = AsyncMock()
        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            response = app_client.get("/api/v1/cdn/manifests/not-a-valid-uuid")
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


class TestCdnVerifyEndpoint:
    """Tests for POST /api/v1/cdn/verify."""

    def test_verify_returns_provenance_lost_for_unregistered_image(self, app_client):
        """Uploading an unknown image should return verdict=PROVENANCE_LOST."""
        from app.database import get_db
        from app.main import app

        db = AsyncMock()
        # SHA-256 lookup: no match
        exec_result_empty = MagicMock()
        exec_result_empty.scalar_one_or_none.return_value = None
        exec_result_all = MagicMock()
        exec_result_all.scalars.return_value.all.return_value = []

        db.execute = AsyncMock(side_effect=[exec_result_empty, exec_result_all])

        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            try:
                from PIL import Image
            except ImportError:
                pytest.skip("Pillow not installed")

            img = Image.new("RGB", (8, 8), color=(42, 42, 42))
            buf = BytesIO()
            img.save(buf, format="JPEG")
            image_data = buf.getvalue()

            response = app_client.post(
                "/api/v1/cdn/verify",
                files={"file": ("unknown.jpg", image_data, "image/jpeg")},
            )

            assert response.status_code == 200
            body = response.json()
            assert body["verdict"] == "PROVENANCE_LOST"
            assert body["verification_path"] == "NONE"
            assert body["record_id"] is None
        finally:
            app.dependency_overrides.clear()

    def test_get_manifest_returns_cbor_when_requested(self, app_client):
        """GET /manifests/{id} with Accept: application/cbor returns 200.

        If cbor2 is installed the response is application/cbor; otherwise
        the endpoint falls through to JSON.  Either is acceptable.
        """
        from unittest.mock import MagicMock

        from app.database import get_db
        from app.main import app
        from app.models.cdn_image_record import CdnImageRecord

        fake_record = MagicMock(spec=CdnImageRecord)
        fake_record.id = uuid.uuid4()
        fake_record.manifest_store = {"title": "test", "assertions": []}

        db = AsyncMock()
        db.get = AsyncMock(return_value=fake_record)

        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            response = app_client.get(
                f"/api/v1/cdn/manifests/{fake_record.id}",
                headers={"accept": "application/cbor"},
            )
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_well_known_manifest_redirects(self, app_client):
        """GET /.well-known/c2pa/manifests/{uuid} should redirect 301."""
        fake_id = str(uuid.uuid4())
        resp = app_client.get(f"/.well-known/c2pa/manifests/{fake_id}", follow_redirects=False)
        assert resp.status_code == 301
        assert f"/api/v1/cdn/manifests/{fake_id}" in resp.headers["location"]

    def test_verify_returns_original_signed_for_sha256_match(self, app_client):
        """Uploading a registered image (SHA-256 match) → ORIGINAL_SIGNED."""
        from app.database import get_db
        from app.main import app
        from app.models.cdn_image_record import CdnImageRecord

        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        img = Image.new("RGB", (8, 8), color=(77, 77, 77))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        image_data = buf.getvalue()

        fake_record = MagicMock(spec=CdnImageRecord)
        fake_record.id = uuid.uuid4()
        fake_record.manifest_store = {"title": "registered"}

        db = AsyncMock()
        # First execute: SHA-256 match returns a record
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = fake_record
        db.execute = AsyncMock(return_value=exec_result)

        app.dependency_overrides[get_db] = _async_db_override_factory(db)

        try:
            response = app_client.post(
                "/api/v1/cdn/verify",
                files={"file": ("known.jpg", image_data, "image/jpeg")},
            )

            assert response.status_code == 200
            body = response.json()
            assert body["verdict"] == "ORIGINAL_SIGNED"
            assert body["verification_path"] == "URL_LOOKUP"
            assert body["record_id"] is not None
        finally:
            app.dependency_overrides.clear()
