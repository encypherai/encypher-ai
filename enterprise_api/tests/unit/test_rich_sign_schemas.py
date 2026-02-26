"""Unit tests for rich_sign_schemas.py."""
import base64
from io import BytesIO

import pytest
from PIL import Image
from pydantic import ValidationError


def make_jpeg_b64(width: int = 32, height: int = 32) -> str:
    """Create a minimal in-memory JPEG and return as base64 string."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def make_valid_image(position: int = 0, mime_type: str = "image/jpeg") -> dict:
    """Create a valid RichContentImage payload dict."""
    return {
        "data": make_jpeg_b64(),
        "filename": f"photo{position}.jpg",
        "mime_type": mime_type,
        "position": position,
        "alt_text": None,
        "metadata": {},
    }


class TestRichContentImage:
    def test_valid_jpeg_passes(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        img = RichContentImage(**make_valid_image())
        assert img.filename == "photo0.jpg"
        assert img.mime_type == "image/jpeg"

    def test_invalid_base64_raises(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        with pytest.raises(ValidationError, match="base64"):
            RichContentImage(
                data="not-valid-base64!!!",
                filename="bad.jpg",
                mime_type="image/jpeg",
            )

    def test_image_over_10mb_raises(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        # Create 11MB of fake data and encode as base64
        big_data = b"\xff" * (11 * 1024 * 1024)
        big_b64 = base64.b64encode(big_data).decode()
        with pytest.raises(ValidationError, match="10MB"):
            RichContentImage(
                data=big_b64,
                filename="big.jpg",
                mime_type="image/jpeg",
            )

    def test_unsupported_mime_type_raises(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        with pytest.raises(ValidationError, match="MIME"):
            RichContentImage(
                data=make_jpeg_b64(),
                filename="img.bmp",
                mime_type="image/bmp",
            )

    def test_supported_mime_types(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        for mime in ("image/jpeg", "image/jpg", "image/png", "image/webp", "image/tiff"):
            img = RichContentImage(
                data=make_jpeg_b64(),
                filename="img.jpg",
                mime_type=mime,
            )
            assert img.mime_type == mime

    def test_position_must_be_non_negative(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        with pytest.raises(ValidationError):
            RichContentImage(
                data=make_jpeg_b64(),
                filename="img.jpg",
                mime_type="image/jpeg",
                position=-1,
            )

    def test_alt_text_is_optional(self):
        from app.schemas.rich_sign_schemas import RichContentImage

        img = RichContentImage(
            data=make_jpeg_b64(),
            filename="img.jpg",
            mime_type="image/jpeg",
        )
        assert img.alt_text is None


class TestRichArticleSignRequest:
    def _make_valid_request(self, num_images: int = 1) -> dict:
        return {
            "content": "This is test article content with some text.",
            "content_format": "plain",
            "document_id": "test-doc-001",
            "document_title": "Test Article",
            "images": [make_valid_image(i) for i in range(num_images)],
            "options": {
                "segmentation_level": "sentence",
                "manifest_mode": "micro",
            },
        }

    def test_valid_request_with_one_image(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(1))
        assert len(req.images) == 1
        assert req.content == "This is test article content with some text."

    def test_more_than_20_images_raises(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        with pytest.raises(ValidationError):
            RichArticleSignRequest(**self._make_valid_request(21))

    def test_exactly_20_images_passes(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(20))
        assert len(req.images) == 20

    def test_no_images_raises(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        payload = self._make_valid_request(0)
        with pytest.raises(ValidationError):
            RichArticleSignRequest(**payload)

    def test_enable_trustmark_defaults_false(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request())
        assert req.options.enable_trustmark is False

    def test_enable_trustmark_can_be_set_true(self):
        """Schema itself should allow enable_trustmark=True; tier check is in service."""
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        payload = self._make_valid_request()
        payload["options"]["enable_trustmark"] = True
        req = RichArticleSignRequest(**payload)
        assert req.options.enable_trustmark is True

    def test_content_format_defaults_to_html(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        payload = self._make_valid_request()
        del payload["content_format"]
        req = RichArticleSignRequest(**payload)
        assert req.content_format == "html"

    def test_publisher_org_id_is_optional(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request())
        assert req.publisher_org_id is None


class TestRichSignOptions:
    def test_defaults(self):
        from app.schemas.rich_sign_schemas import RichSignOptions

        opts = RichSignOptions()
        assert opts.segmentation_level == "sentence"
        assert opts.manifest_mode == "micro"
        assert opts.enable_trustmark is False
        assert opts.image_quality == 95
        assert opts.use_rights_profile is True
        assert opts.index_for_attribution is True

    def test_image_quality_bounds(self):
        from app.schemas.rich_sign_schemas import RichSignOptions

        with pytest.raises(ValidationError):
            RichSignOptions(image_quality=0)
        with pytest.raises(ValidationError):
            RichSignOptions(image_quality=101)

    def test_valid_image_quality(self):
        from app.schemas.rich_sign_schemas import RichSignOptions

        opts = RichSignOptions(image_quality=80)
        assert opts.image_quality == 80


class TestSignedImageResult:
    def test_instantiation(self):
        from app.schemas.rich_sign_schemas import SignedImageResult

        result = SignedImageResult(
            image_id="img_aabbccdd",
            filename="photo.jpg",
            position=0,
            signed_image_b64=make_jpeg_b64(),
            signed_image_hash="sha256:" + "a" * 64,
            c2pa_manifest_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            size_bytes=1024,
            mime_type="image/jpeg",
        )
        assert result.image_id == "img_aabbccdd"
        assert result.trustmark_applied is False

    def test_phash_is_optional(self):
        from app.schemas.rich_sign_schemas import SignedImageResult

        result = SignedImageResult(
            image_id="img_aabbccdd",
            filename="photo.jpg",
            position=0,
            signed_image_b64=make_jpeg_b64(),
            signed_image_hash="sha256:" + "a" * 64,
            c2pa_manifest_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            size_bytes=1024,
            mime_type="image/jpeg",
            phash=None,
        )
        assert result.phash is None
