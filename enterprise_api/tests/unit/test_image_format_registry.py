"""Unit tests for image_format_registry -- SSOT for C2PA image format support."""

import pytest


class TestFormatRegistry:
    """Verify the registry contains all 13 C2PA conformance MIME types."""

    def test_all_conformance_mime_types_present(self):
        from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES

        c2pa_required = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/tiff",
            "image/gif",
            "image/jxl",
            "image/svg+xml",
            "image/x-adobe-dng",
            "image/heic",
            "image/heif",
            "image/heic-sequence",
            "image/heif-sequence",
            "image/avif",
        }
        for mime in c2pa_required:
            assert mime in SUPPORTED_IMAGE_MIME_TYPES, f"Missing: {mime}"

    def test_jpg_alias_present(self):
        from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES

        assert "image/jpg" in SUPPORTED_IMAGE_MIME_TYPES

    def test_total_count(self):
        from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES

        # 13 canonical + image/jpg alias = 14
        assert len(SUPPORTED_IMAGE_MIME_TYPES) == 14

    def test_unsupported_type_not_present(self):
        from app.utils.image_format_registry import SUPPORTED_IMAGE_MIME_TYPES

        assert "image/bmp" not in SUPPORTED_IMAGE_MIME_TYPES
        assert "video/mp4" not in SUPPORTED_IMAGE_MIME_TYPES


class TestTierClassification:
    def test_tier_a_formats(self):
        from app.utils.image_format_registry import FormatTier, get_tier

        for mime in ("image/jpeg", "image/png", "image/webp", "image/tiff", "image/gif"):
            assert get_tier(mime) == FormatTier.A, f"{mime} should be Tier A"

    def test_tier_b_formats(self):
        from app.utils.image_format_registry import FormatTier, get_tier

        for mime in ("image/heic", "image/heif", "image/heic-sequence", "image/heif-sequence", "image/avif"):
            assert get_tier(mime) == FormatTier.B, f"{mime} should be Tier B"

    def test_tier_c_formats(self):
        from app.utils.image_format_registry import FormatTier, get_tier

        for mime in ("image/svg+xml", "image/jxl", "image/x-adobe-dng"):
            assert get_tier(mime) == FormatTier.C, f"{mime} should be Tier C"

    def test_unknown_type_returns_none(self):
        from app.utils.image_format_registry import get_tier

        assert get_tier("image/bmp") is None


class TestHelpers:
    def test_is_pillow_format(self):
        from app.utils.image_format_registry import is_pillow_format

        assert is_pillow_format("image/jpeg") is True
        assert is_pillow_format("image/gif") is True
        assert is_pillow_format("image/heic") is True  # Tier B = plugin-backed Pillow
        assert is_pillow_format("image/svg+xml") is False  # Tier C

    def test_is_bypass_format(self):
        from app.utils.image_format_registry import is_bypass_format

        assert is_bypass_format("image/svg+xml") is True
        assert is_bypass_format("image/jxl") is True
        assert is_bypass_format("image/x-adobe-dng") is True
        assert is_bypass_format("image/jpeg") is False

    def test_supports_exif_strip(self):
        from app.utils.image_format_registry import supports_exif_strip

        assert supports_exif_strip("image/jpeg") is True
        assert supports_exif_strip("image/heic") is True
        assert supports_exif_strip("image/svg+xml") is False
        assert supports_exif_strip("image/jxl") is False

    def test_mime_to_pil_format(self):
        from app.utils.image_format_registry import MIME_TO_PIL_FORMAT

        assert MIME_TO_PIL_FORMAT["image/jpeg"] == "JPEG"
        assert MIME_TO_PIL_FORMAT["image/jpg"] == "JPEG"
        assert MIME_TO_PIL_FORMAT["image/gif"] == "GIF"
        assert MIME_TO_PIL_FORMAT["image/avif"] == "AVIF"
        assert "image/svg+xml" not in MIME_TO_PIL_FORMAT
        assert "image/jxl" not in MIME_TO_PIL_FORMAT


class TestMagicByteValidation:
    def test_svg_valid(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', "image/svg+xml")

    def test_svg_with_xml_declaration(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b'<?xml version="1.0"?><svg></svg>', "image/svg+xml")

    def test_svg_with_whitespace(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b'  \n  <?xml version="1.0"?><svg></svg>', "image/svg+xml")

    def test_svg_with_bom(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b"\xef\xbb\xbf<svg></svg>", "image/svg+xml")

    def test_svg_invalid(self):
        from app.utils.image_format_registry import validate_magic_bytes

        with pytest.raises(ValueError, match="SVG"):
            validate_magic_bytes(b"not an svg at all", "image/svg+xml")

    def test_dng_little_endian(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b"II\x2a\x00" + b"\x00" * 100, "image/x-adobe-dng")

    def test_dng_big_endian(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b"MM\x00\x2a" + b"\x00" * 100, "image/x-adobe-dng")

    def test_dng_invalid(self):
        from app.utils.image_format_registry import validate_magic_bytes

        with pytest.raises(ValueError, match="TIFF/DNG"):
            validate_magic_bytes(b"\x89PNG" + b"\x00" * 100, "image/x-adobe-dng")

    def test_jxl_codestream(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b"\xff\x0a" + b"\x00" * 100, "image/jxl")

    def test_jxl_container(self):
        from app.utils.image_format_registry import validate_magic_bytes

        validate_magic_bytes(b"\x00\x00\x00\x0cJXL \r\n\x87\n" + b"\x00" * 100, "image/jxl")

    def test_jxl_invalid(self):
        from app.utils.image_format_registry import validate_magic_bytes

        with pytest.raises(ValueError, match="JPEG XL"):
            validate_magic_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100, "image/jxl")

    def test_dng_too_short(self):
        from app.utils.image_format_registry import validate_magic_bytes

        with pytest.raises(ValueError, match="too short"):
            validate_magic_bytes(b"II", "image/x-adobe-dng")

    def test_unknown_mime_raises(self):
        from app.utils.image_format_registry import validate_magic_bytes

        with pytest.raises(ValueError, match="No magic byte"):
            validate_magic_bytes(b"anything", "image/bmp")


class TestValidateImageNewFormats:
    """Test validate_image with newly supported formats."""

    def test_gif_validates(self):
        from io import BytesIO

        from PIL import Image

        from app.utils.image_utils import validate_image

        img = Image.new("P", (32, 32))
        buf = BytesIO()
        img.save(buf, format="GIF")
        w, h, fmt = validate_image(buf.getvalue(), "image/gif")
        assert w == 32
        assert h == 32

    def test_svg_validates(self):
        from app.utils.image_utils import validate_image

        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" fill="red"/></svg>'
        w, h, fmt = validate_image(svg, "image/svg+xml")
        assert w == 0  # Tier C: no dimensions
        assert h == 0
        assert fmt == "image/svg+xml"

    def test_dng_validates(self):
        from app.utils.image_utils import validate_image

        dng_header = b"II\x2a\x00" + b"\x00" * 200
        w, h, fmt = validate_image(dng_header, "image/x-adobe-dng")
        assert w == 0
        assert h == 0

    def test_jxl_validates(self):
        from app.utils.image_utils import validate_image

        jxl = b"\xff\x0a" + b"\x00" * 200
        w, h, fmt = validate_image(jxl, "image/jxl")
        assert w == 0
        assert h == 0

    def test_svg_with_bad_content_rejected(self):
        from app.utils.image_utils import validate_image

        with pytest.raises(ValueError, match="SVG"):
            validate_image(b"this is not svg", "image/svg+xml")


class TestStripExifNewFormats:
    """Test strip_exif with bypass formats."""

    def test_svg_bypass_returns_original(self):
        from app.utils.image_utils import strip_exif

        svg = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = strip_exif(svg, "image/svg+xml")
        assert result == svg

    def test_dng_bypass_returns_original(self):
        from app.utils.image_utils import strip_exif

        dng = b"II\x2a\x00" + b"\x00" * 200
        result = strip_exif(dng, "image/x-adobe-dng")
        assert result == dng

    def test_jxl_bypass_returns_original(self):
        from app.utils.image_utils import strip_exif

        jxl = b"\xff\x0a" + b"\x00" * 200
        result = strip_exif(jxl, "image/jxl")
        assert result == jxl

    def test_gif_strips_via_pillow(self):
        from io import BytesIO

        from PIL import Image

        from app.utils.image_utils import strip_exif

        img = Image.new("P", (32, 32))
        buf = BytesIO()
        img.save(buf, format="GIF")
        result = strip_exif(buf.getvalue(), "image/gif")
        assert len(result) > 0
        # Verify it's still a valid GIF
        reloaded = Image.open(BytesIO(result))
        assert reloaded.format == "GIF"


class TestComputePhashNewFormats:
    def test_bypass_format_returns_zero(self):
        from app.utils.image_utils import compute_phash

        assert compute_phash(b"<svg></svg>", mime_type="image/svg+xml") == 0
        assert compute_phash(b"\xff\x0a" + b"\x00" * 50, mime_type="image/jxl") == 0
        assert compute_phash(b"II\x2a\x00" + b"\x00" * 50, mime_type="image/x-adobe-dng") == 0

    def test_pillow_format_still_computes(self):
        from io import BytesIO

        from PIL import Image

        from app.utils.image_utils import compute_phash

        img = Image.new("RGB", (64, 64), color=(100, 150, 200))
        buf = BytesIO()
        img.save(buf, format="JPEG")
        h = compute_phash(buf.getvalue(), mime_type="image/jpeg")
        assert isinstance(h, int)


class TestSchemaAcceptsNewFormats:
    """Verify the rich_sign_schemas SUPPORTED_MIME_TYPES includes all formats."""

    def test_schema_has_all_formats(self):
        from app.schemas.rich_sign_schemas import SUPPORTED_MIME_TYPES

        for mime in (
            "image/gif",
            "image/avif",
            "image/svg+xml",
            "image/jxl",
            "image/x-adobe-dng",
            "image/heic",
            "image/heif",
            "image/heic-sequence",
            "image/heif-sequence",
        ):
            assert mime in SUPPORTED_MIME_TYPES, f"Schema missing: {mime}"
