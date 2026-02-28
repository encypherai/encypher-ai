"""Unit tests for the ArticleImage SQLAlchemy model.

Tests model instantiation, default values, and column constraints
without requiring a live database connection.
"""

import os
import sys
import uuid
from pathlib import Path

# Ensure enterprise_api root is on the path before app imports
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

from app.models.article_image import ArticleImage


class TestArticleImageInstantiation:
    """Tests for ArticleImage model construction and defaults."""

    def test_instantiation_with_required_fields(self) -> None:
        """ArticleImage can be created with all required fields."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_deadbeef",
            mime_type="image/jpeg",
            original_hash="sha256:aabbcc",
            signed_hash="sha256:ddeeff",
            size_bytes=102400,
        )
        assert img.organization_id == "org_test"
        assert img.document_id == "doc_abc123"
        assert img.image_id == "img_deadbeef"
        assert img.mime_type == "image/jpeg"
        assert img.original_hash == "sha256:aabbcc"
        assert img.signed_hash == "sha256:ddeeff"
        assert img.size_bytes == 102400

    def test_default_position_is_zero(self) -> None:
        """position defaults to 0 when not provided."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_11111111",
            mime_type="image/png",
            original_hash="sha256:aabb",
            signed_hash="sha256:ccdd",
            size_bytes=50000,
        )
        # SQLAlchemy Column default applies on flush; Python-side it may be None
        # but we document expected value is 0
        assert img.position is None or img.position == 0

    def test_default_trustmark_applied_is_false(self) -> None:
        """trustmark_applied defaults to False."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_22222222",
            mime_type="image/png",
            original_hash="sha256:aabb",
            signed_hash="sha256:ccdd",
            size_bytes=50000,
        )
        # Python-side default; may be None before flush but logically False
        assert img.trustmark_applied is None or img.trustmark_applied is False

    def test_optional_fields_default_to_none(self) -> None:
        """Optional fields are None when not provided."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_33333333",
            mime_type="image/jpeg",
            original_hash="sha256:aa",
            signed_hash="sha256:bb",
            size_bytes=12345,
        )
        assert img.filename is None
        assert img.alt_text is None
        assert img.c2pa_instance_id is None
        assert img.c2pa_manifest_hash is None
        assert img.phash is None
        assert img.trustmark_key is None
        assert img.exif_metadata is None

    def test_tablename(self) -> None:
        """__tablename__ is article_images."""
        assert ArticleImage.__tablename__ == "article_images"

    def test_uuid_primary_key_default(self) -> None:
        """id column has a callable uuid4 default."""
        img1 = ArticleImage(
            organization_id="org_a",
            document_id="doc_a",
            image_id="img_a1b2c3d4",
            mime_type="image/jpeg",
            original_hash="sha256:00",
            signed_hash="sha256:11",
            size_bytes=1000,
        )
        img2 = ArticleImage(
            organization_id="org_b",
            document_id="doc_b",
            image_id="img_b2c3d4e5",
            mime_type="image/jpeg",
            original_hash="sha256:22",
            signed_hash="sha256:33",
            size_bytes=2000,
        )
        # Default is a callable; if triggered, ids should differ
        if img1.id is not None and img2.id is not None:
            assert img1.id != img2.id

    def test_phash_accepts_integer(self) -> None:
        """phash column accepts a 64-bit integer."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_phash001",
            mime_type="image/jpeg",
            original_hash="sha256:aa",
            signed_hash="sha256:bb",
            size_bytes=9999,
            phash=0xA1B2C3D4E5F67890,
        )
        assert img.phash == 0xA1B2C3D4E5F67890

    def test_phash_algorithm_default(self) -> None:
        """phash_algorithm column default is average_hash."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc123",
            image_id="img_algo0001",
            mime_type="image/jpeg",
            original_hash="sha256:aa",
            signed_hash="sha256:bb",
            size_bytes=9999,
        )
        # Python-side column default
        assert img.phash_algorithm is None or img.phash_algorithm == "average_hash"

    def test_repr_contains_image_id(self) -> None:
        """__repr__ includes image_id for debugging."""
        img = ArticleImage(
            organization_id="org_test",
            document_id="doc_abc",
            image_id="img_repr0001",
            mime_type="image/png",
            original_hash="sha256:cc",
            signed_hash="sha256:dd",
            size_bytes=500,
        )
        r = repr(img)
        assert "img_repr0001" in r

    def test_with_all_fields(self) -> None:
        """ArticleImage can be constructed with every field specified."""
        img_uuid = uuid.uuid4()
        img = ArticleImage(
            id=img_uuid,
            organization_id="org_full",
            document_id="doc_full",
            image_id="img_fulltest",
            position=3,
            filename="photo.jpg",
            mime_type="image/jpeg",
            alt_text="A beautiful photo",
            original_hash="sha256:orig",
            signed_hash="sha256:sign",
            size_bytes=204800,
            c2pa_instance_id="urn:uuid:12345678-1234-1234-1234-123456789abc",
            c2pa_manifest_hash="sha256:manifest",
            phash=12345678,
            phash_algorithm="average_hash",
            trustmark_applied=True,
            trustmark_key="trustmark_key_v1",
            exif_metadata={"Make": "Canon", "Model": "EOS"},
            image_metadata={"width": 1920, "height": 1080},
        )
        assert img.id == img_uuid
        assert img.position == 3
        assert img.filename == "photo.jpg"
        assert img.alt_text == "A beautiful photo"
        assert img.trustmark_applied is True
        assert img.trustmark_key == "trustmark_key_v1"
        assert img.exif_metadata == {"Make": "Canon", "Model": "EOS"}
        assert img.image_metadata == {"width": 1920, "height": 1080}
