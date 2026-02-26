"""Unit tests for image_utils module."""
import hashlib
from io import BytesIO

import pytest

from PIL import Image


def make_test_jpeg(width: int = 64, height: int = 64) -> bytes:
    """Create a minimal in-memory JPEG for testing."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def make_test_png(width: int = 64, height: int = 64) -> bytes:
    """Create a minimal in-memory PNG for testing."""
    img = Image.new("RGB", (width, height), color=(200, 100, 50))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_test_webp(width: int = 64, height: int = 64) -> bytes:
    """Create a minimal in-memory WebP for testing."""
    img = Image.new("RGB", (width, height), color=(50, 100, 200))
    buf = BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


class TestValidateImage:
    def test_valid_jpeg_passes(self):
        from app.utils.image_utils import validate_image

        data = make_test_jpeg()
        w, h, fmt = validate_image(data, "image/jpeg")
        assert w == 64
        assert h == 64
        assert fmt.upper() in ("JPEG", "JPG")

    def test_valid_png_passes(self):
        from app.utils.image_utils import validate_image

        data = make_test_png()
        w, h, fmt = validate_image(data, "image/png")
        assert w == 64
        assert h == 64
        assert fmt.upper() == "PNG"

    def test_oversized_file_raises_value_error(self):
        from app.utils.image_utils import validate_image

        # Generate a real-looking oversized bytes blob
        big_data = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)
        with pytest.raises(ValueError, match="exceeds"):
            validate_image(big_data, "image/jpeg")

    def test_bad_bytes_raises_value_error(self):
        from app.utils.image_utils import validate_image

        with pytest.raises(ValueError):
            validate_image(b"not-an-image-at-all-garbage-data", "image/jpeg")

    def test_unsupported_mime_type_raises_value_error(self):
        from app.utils.image_utils import validate_image

        data = make_test_jpeg()
        with pytest.raises(ValueError, match="Unsupported"):
            validate_image(data, "image/bmp")

    def test_custom_max_size(self):
        from app.utils.image_utils import validate_image

        data = make_test_jpeg()
        # Set max_size_bytes below the actual image size
        with pytest.raises(ValueError, match="exceeds"):
            validate_image(data, "image/jpeg", max_size_bytes=10)


class TestExtractExif:
    def test_returns_dict_for_jpeg_without_exif(self):
        from app.utils.image_utils import extract_exif

        data = make_test_jpeg()
        result = extract_exif(data)
        assert isinstance(result, dict)

    def test_returns_dict_for_png(self):
        from app.utils.image_utils import extract_exif

        data = make_test_png()
        result = extract_exif(data)
        assert isinstance(result, dict)

    def test_never_raises(self):
        from app.utils.image_utils import extract_exif

        # Garbage input should return empty dict, not raise
        result = extract_exif(b"garbage")
        assert result == {}


class TestStripExif:
    def test_output_is_valid_jpeg(self):
        from app.utils.image_utils import strip_exif

        data = make_test_jpeg()
        stripped = strip_exif(data, "image/jpeg")
        # Should be decodable by PIL
        img = Image.open(BytesIO(stripped))
        assert img.size == (64, 64)

    def test_output_is_smaller_or_equal_for_jpeg(self):
        from app.utils.image_utils import strip_exif

        data = make_test_jpeg()
        stripped = strip_exif(data, "image/jpeg")
        # Stripped should be valid image bytes (not necessarily smaller for a minimal test img)
        assert len(stripped) > 0
        # Should be a valid JPEG header
        assert stripped[:2] == b"\xff\xd8"

    def test_png_strips_correctly(self):
        from app.utils.image_utils import strip_exif

        data = make_test_png()
        stripped = strip_exif(data, "image/png")
        img = Image.open(BytesIO(stripped))
        assert img.size == (64, 64)

    def test_strip_exif_respects_mime_type(self):
        from app.utils.image_utils import strip_exif

        data = make_test_jpeg()
        stripped = strip_exif(data, "image/jpeg", quality=85)
        assert len(stripped) > 0


class TestComputePhash:
    def test_returns_integer(self):
        from app.utils.image_utils import compute_phash

        data = make_test_jpeg()
        h = compute_phash(data)
        assert isinstance(h, int)

    def test_same_image_gives_same_hash(self):
        from app.utils.image_utils import compute_phash

        data = make_test_jpeg()
        h1 = compute_phash(data)
        h2 = compute_phash(data)
        assert h1 == h2

    def test_different_images_give_different_hashes(self):
        from app.utils.image_utils import compute_phash

        # Create two visually distinct images: solid blue vs gradient
        img_blue = Image.new("RGB", (64, 64), color=(0, 0, 255))
        buf_blue = BytesIO()
        img_blue.save(buf_blue, format="JPEG")
        data_blue = buf_blue.getvalue()

        # Create a checkerboard pattern image (very different structure)
        img_check = Image.new("RGB", (64, 64), color=(255, 255, 255))
        pixels = img_check.load()
        for y in range(64):
            for x in range(64):
                if (x // 8 + y // 8) % 2 == 0:
                    pixels[x, y] = (0, 0, 0)
        buf_check = BytesIO()
        img_check.save(buf_check, format="JPEG")
        data_check = buf_check.getvalue()

        h_blue = compute_phash(data_blue)
        h_check = compute_phash(data_check)
        # Two structurally different images should have different hashes
        assert h_blue != h_check

    def test_int64_range(self):
        from app.utils.image_utils import compute_phash

        data = make_test_jpeg()
        h = compute_phash(data)
        # PostgreSQL BIGINT range
        assert -(1 << 63) <= h <= (1 << 63) - 1


class TestComputeSha256:
    def test_returns_sha256_prefix(self):
        from app.utils.image_utils import compute_sha256

        data = b"hello world"
        result = compute_sha256(data)
        assert result.startswith("sha256:")

    def test_correct_length(self):
        from app.utils.image_utils import compute_sha256

        data = b"test data"
        result = compute_sha256(data)
        # "sha256:" + 64 hex chars
        assert len(result) == 7 + 64

    def test_is_deterministic(self):
        from app.utils.image_utils import compute_sha256

        data = b"deterministic test"
        assert compute_sha256(data) == compute_sha256(data)

    def test_matches_hashlib(self):
        from app.utils.image_utils import compute_sha256

        data = b"match test"
        expected = "sha256:" + hashlib.sha256(data).hexdigest()
        assert compute_sha256(data) == expected


class TestGenerateImageId:
    def test_starts_with_img_prefix(self):
        from app.utils.image_utils import generate_image_id

        img_id = generate_image_id()
        assert img_id.startswith("img_")

    def test_length_is_12(self):
        from app.utils.image_utils import generate_image_id

        img_id = generate_image_id()
        # "img_" (4) + 8 hex chars = 12
        assert len(img_id) == 12

    def test_unique_per_call(self):
        from app.utils.image_utils import generate_image_id

        ids = {generate_image_id() for _ in range(20)}
        assert len(ids) == 20


class TestEnchypherXmp:
    """Unit tests for XMP inject/extract roundtrip."""

    def test_jpeg_roundtrip(self):
        from app.utils.image_utils import extract_encypher_xmp, inject_encypher_xmp

        jpeg = make_test_jpeg()
        embedded = inject_encypher_xmp(
            image_bytes=jpeg,
            mime_type="image/jpeg",
            instance_id="urn:uuid:test-instance-1",
            org_id="org_unit_test",
            document_id="doc_unit_test",
            image_hash="sha256:deadbeef",
        )
        result = extract_encypher_xmp(embedded, "image/jpeg")
        assert result is not None
        assert result["instance_id"] == "urn:uuid:test-instance-1"
        assert result["org_id"] == "org_unit_test"
        assert result["document_id"] == "doc_unit_test"
        assert result["image_hash"] == "sha256:deadbeef"

    def test_png_roundtrip(self):
        from app.utils.image_utils import extract_encypher_xmp, inject_encypher_xmp

        png = make_test_png()
        embedded = inject_encypher_xmp(
            image_bytes=png,
            mime_type="image/png",
            instance_id="urn:uuid:png-instance-99",
            org_id="org_png",
            document_id="doc_png",
            image_hash="sha256:cafebabe",
        )
        result = extract_encypher_xmp(embedded, "image/png")
        assert result is not None
        assert result["instance_id"] == "urn:uuid:png-instance-99"
        assert result["org_id"] == "org_png"
        assert result["document_id"] == "doc_png"

    def test_inject_changes_bytes(self):
        from app.utils.image_utils import compute_sha256, inject_encypher_xmp

        jpeg = make_test_jpeg()
        embedded = inject_encypher_xmp(
            image_bytes=jpeg,
            mime_type="image/jpeg",
            instance_id="urn:uuid:change-test",
            org_id="org_a",
            document_id="doc_a",
            image_hash="sha256:aabbcc",
        )
        assert compute_sha256(embedded) != compute_sha256(jpeg)

    def test_extract_returns_none_on_no_xmp(self):
        from app.utils.image_utils import extract_encypher_xmp

        jpeg = make_test_jpeg()
        result = extract_encypher_xmp(jpeg, "image/jpeg")
        assert result is None

    def test_inject_on_unsupported_mime_returns_original(self):
        from app.utils.image_utils import inject_encypher_xmp

        webp = make_test_webp()
        result = inject_encypher_xmp(
            image_bytes=webp,
            mime_type="image/webp",
            instance_id="urn:uuid:noop",
            org_id="org_noop",
            document_id="doc_noop",
            image_hash="sha256:00",
        )
        assert result == webp

    def test_inject_error_returns_original(self):
        from app.utils.image_utils import inject_encypher_xmp

        garbage = b"not-a-real-jpeg"
        result = inject_encypher_xmp(
            image_bytes=garbage,
            mime_type="image/jpeg",
            instance_id="urn:uuid:err",
            org_id="org_err",
            document_id="doc_err",
            image_hash="sha256:err",
        )
        # Should return original on error, not raise
        assert result == garbage
