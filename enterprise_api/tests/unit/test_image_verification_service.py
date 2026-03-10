"""Unit tests for image_verification_service.py.

Tests C2PA verification logic and SHA-256 hash utility.
Uses an in-memory JPEG (Pillow) to avoid file I/O.
No database calls.
"""

import io
import os
import sys
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

from PIL import Image

from app.services.image_verification_service import compute_sha256, verify_image_c2pa


def _make_jpeg_bytes(width: int = 10, height: int = 10) -> bytes:
    """Create a minimal in-memory JPEG image."""
    img = Image.new("RGB", (width, height), color=(128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_png_bytes(width: int = 8, height: int = 8) -> bytes:
    """Create a minimal in-memory PNG image."""
    img = Image.new("RGB", (width, height), color=(0, 128, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestComputeSha256:
    """Tests for compute_sha256 helper."""

    def test_returns_sha256_prefix(self) -> None:
        """Result starts with 'sha256:'."""
        result = compute_sha256(b"hello world")
        assert result.startswith("sha256:")

    def test_hex_length(self) -> None:
        """The hex digest portion is 64 characters."""
        result = compute_sha256(b"test data")
        prefix = "sha256:"
        assert result.startswith(prefix)
        hex_part = result[len(prefix) :]
        assert len(hex_part) == 64

    def test_hex_chars_only(self) -> None:
        """The hex portion contains only lowercase hex characters."""
        result = compute_sha256(b"example")
        hex_part = result[len("sha256:") :]
        assert all(c in "0123456789abcdef" for c in hex_part)

    def test_deterministic(self) -> None:
        """Same input produces same hash every time."""
        data = b"reproducible"
        assert compute_sha256(data) == compute_sha256(data)

    def test_different_inputs_differ(self) -> None:
        """Different inputs produce different hashes."""
        assert compute_sha256(b"aaa") != compute_sha256(b"bbb")

    def test_empty_bytes(self) -> None:
        """Empty byte string produces valid hash."""
        result = compute_sha256(b"")
        assert result.startswith("sha256:")
        assert len(result) == len("sha256:") + 64

    def test_known_value(self) -> None:
        """Known SHA-256 value for 'abc' matches Python hashlib output."""
        import hashlib

        expected_hex = hashlib.sha256(b"abc").hexdigest()
        result = compute_sha256(b"abc")
        assert result == "sha256:" + expected_hex


class TestVerifyImageC2pa:
    """Tests for verify_image_c2pa service function."""

    def test_plain_jpeg_returns_invalid(self) -> None:
        """A plain (unsigned) JPEG returns valid=False with c2pa_manifest_valid=False."""
        jpeg_bytes = _make_jpeg_bytes()
        result = verify_image_c2pa(jpeg_bytes, "image/jpeg")
        assert result.valid is False
        assert result.c2pa_manifest_valid is False

    def test_plain_jpeg_no_error_is_set(self) -> None:
        """A plain JPEG without a manifest returns an informative error string."""
        jpeg_bytes = _make_jpeg_bytes()
        result = verify_image_c2pa(jpeg_bytes, "image/jpeg")
        # error must be a non-empty string
        assert result.error is not None
        assert len(result.error) > 0

    def test_plain_png_returns_invalid(self) -> None:
        """A plain (unsigned) PNG returns valid=False."""
        png_bytes = _make_png_bytes()
        result = verify_image_c2pa(png_bytes, "image/png")
        assert result.valid is False
        assert result.c2pa_manifest_valid is False

    def test_invalid_bytes_returns_error(self) -> None:
        """Completely invalid bytes return valid=False with an error message."""
        garbage = b"\x00\x01\x02\x03 this is not an image"
        result = verify_image_c2pa(garbage, "image/jpeg")
        assert result.valid is False
        assert result.c2pa_manifest_valid is False
        assert result.hash_matches is False
        assert result.error is not None

    def test_empty_bytes_returns_error(self) -> None:
        """Empty bytes return valid=False."""
        result = verify_image_c2pa(b"", "image/jpeg")
        assert result.valid is False
        assert result.error is not None

    def test_result_has_no_instance_id_for_unsigned(self) -> None:
        """Unsigned image produces no c2pa_instance_id."""
        jpeg_bytes = _make_jpeg_bytes()
        result = verify_image_c2pa(jpeg_bytes, "image/jpeg")
        assert result.c2pa_instance_id is None

    def test_result_has_no_manifest_data_for_unsigned(self) -> None:
        """Unsigned image produces no manifest_data."""
        jpeg_bytes = _make_jpeg_bytes()
        result = verify_image_c2pa(jpeg_bytes, "image/jpeg")
        assert result.manifest_data is None

    def test_result_dataclass_fields_present(self) -> None:
        """Result object always has all expected fields."""
        jpeg_bytes = _make_jpeg_bytes()
        result = verify_image_c2pa(jpeg_bytes, "image/jpeg")
        assert hasattr(result, "valid")
        assert hasattr(result, "c2pa_manifest_valid")
        assert hasattr(result, "hash_matches")
        assert hasattr(result, "c2pa_instance_id")
        assert hasattr(result, "signer")
        assert hasattr(result, "signed_at")
        assert hasattr(result, "manifest_data")
        assert hasattr(result, "error")
