"""Unit tests for rich_sign_schemas.py."""

import base64
import struct
import wave
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


def make_wav_b64(duration: float = 0.01, sample_rate: int = 8000) -> str:
    """Create a minimal WAV file and return as base64 string."""
    buf = BytesIO()
    n_samples = int(sample_rate * duration)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_samples)
    return base64.b64encode(buf.getvalue()).decode()


def make_mp4_b64() -> str:
    """Create minimal bytes that look like an MP4 (ftyp box) and return as base64."""
    ftyp_data = b"mp42\x00\x00\x00\x00mp42isom"
    box_size = 8 + len(ftyp_data)
    ftyp_box = struct.pack(">I", box_size) + b"ftyp" + ftyp_data
    return base64.b64encode(ftyp_box + b"\x00" * 64).decode()


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


def make_valid_audio(position: int = 0, mime_type: str = "audio/wav") -> dict:
    """Create a valid RichContentAudio payload dict."""
    return {
        "data": make_wav_b64(),
        "filename": f"clip{position}.wav",
        "mime_type": mime_type,
        "position": position,
        "metadata": {},
    }


def make_valid_video(position: int = 0, mime_type: str = "video/mp4") -> dict:
    """Create a valid RichContentVideo payload dict."""
    return {
        "data": make_mp4_b64(),
        "filename": f"video{position}.mp4",
        "mime_type": mime_type,
        "position": position,
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


class TestRichContentAudio:
    def test_valid_wav_passes(self):
        from app.schemas.rich_sign_schemas import RichContentAudio

        aud = RichContentAudio(**make_valid_audio())
        assert aud.filename == "clip0.wav"
        assert aud.mime_type == "audio/wav"

    def test_invalid_base64_raises(self):
        from app.schemas.rich_sign_schemas import RichContentAudio

        with pytest.raises(ValidationError, match="base64"):
            RichContentAudio(data="not-valid!!!", filename="bad.wav", mime_type="audio/wav")

    def test_audio_over_50mb_raises(self):
        from app.schemas.rich_sign_schemas import RichContentAudio

        big_data = b"\x00" * (51 * 1024 * 1024)
        big_b64 = base64.b64encode(big_data).decode()
        with pytest.raises(ValidationError, match="50MB"):
            RichContentAudio(data=big_b64, filename="big.wav", mime_type="audio/wav")

    def test_unsupported_audio_mime_raises(self):
        from app.schemas.rich_sign_schemas import RichContentAudio

        with pytest.raises(ValidationError, match="audio MIME"):
            RichContentAudio(data=make_wav_b64(), filename="bad.ogg", mime_type="audio/ogg")

    def test_position_must_be_non_negative(self):
        from app.schemas.rich_sign_schemas import RichContentAudio

        with pytest.raises(ValidationError):
            RichContentAudio(data=make_wav_b64(), filename="clip.wav", mime_type="audio/wav", position=-1)


class TestRichContentVideo:
    def test_valid_mp4_passes(self):
        from app.schemas.rich_sign_schemas import RichContentVideo

        vid = RichContentVideo(**make_valid_video())
        assert vid.filename == "video0.mp4"
        assert vid.mime_type == "video/mp4"

    def test_invalid_base64_raises(self):
        from app.schemas.rich_sign_schemas import RichContentVideo

        with pytest.raises(ValidationError, match="base64"):
            RichContentVideo(data="not-valid!!!", filename="bad.mp4", mime_type="video/mp4")

    def test_video_over_100mb_raises(self):
        from app.schemas.rich_sign_schemas import RichContentVideo

        big_data = b"\x00" * (101 * 1024 * 1024)
        big_b64 = base64.b64encode(big_data).decode()
        with pytest.raises(ValidationError, match="100MB"):
            RichContentVideo(data=big_b64, filename="big.mp4", mime_type="video/mp4")

    def test_unsupported_video_mime_raises(self):
        from app.schemas.rich_sign_schemas import RichContentVideo

        with pytest.raises(ValidationError, match="video MIME"):
            RichContentVideo(data=make_mp4_b64(), filename="bad.webm", mime_type="video/webm")

    def test_position_must_be_non_negative(self):
        from app.schemas.rich_sign_schemas import RichContentVideo

        with pytest.raises(ValidationError):
            RichContentVideo(data=make_mp4_b64(), filename="clip.mp4", mime_type="video/mp4", position=-1)


class TestRichArticleSignRequest:
    def _make_valid_request(self, num_images: int = 1, num_audios: int = 0, num_videos: int = 0) -> dict:
        return {
            "content": "This is test article content with some text.",
            "content_format": "plain",
            "document_id": "test-doc-001",
            "document_title": "Test Article",
            "images": [make_valid_image(i) for i in range(num_images)],
            "audios": [make_valid_audio(i) for i in range(num_audios)],
            "videos": [make_valid_video(i) for i in range(num_videos)],
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

    def test_valid_request_with_audio_only(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(num_images=0, num_audios=2))
        assert len(req.images) == 0
        assert len(req.audios) == 2

    def test_valid_request_with_video_only(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(num_images=0, num_videos=1))
        assert len(req.videos) == 1

    def test_valid_request_with_all_media_types(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(num_images=2, num_audios=1, num_videos=1))
        assert len(req.images) == 2
        assert len(req.audios) == 1
        assert len(req.videos) == 1

    def test_no_media_raises(self):
        """At least one media item is required."""
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        payload = self._make_valid_request(num_images=0, num_audios=0, num_videos=0)
        with pytest.raises(ValidationError, match="At least one media item"):
            RichArticleSignRequest(**payload)

    def test_more_than_20_images_raises(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        with pytest.raises(ValidationError):
            RichArticleSignRequest(**self._make_valid_request(21))

    def test_more_than_10_audios_raises(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        with pytest.raises(ValidationError):
            RichArticleSignRequest(**self._make_valid_request(num_images=0, num_audios=11))

    def test_more_than_5_videos_raises(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        with pytest.raises(ValidationError):
            RichArticleSignRequest(**self._make_valid_request(num_images=0, num_videos=6))

    def test_exactly_20_images_passes(self):
        from app.schemas.rich_sign_schemas import RichArticleSignRequest

        req = RichArticleSignRequest(**self._make_valid_request(20))
        assert len(req.images) == 20

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
        assert opts.enable_audio_watermark is False
        assert opts.enable_video_watermark is False
        assert opts.image_quality == 95
        assert opts.use_rights_profile is True
        assert opts.index_for_attribution is True

    def test_watermark_flags_can_be_set(self):
        from app.schemas.rich_sign_schemas import RichSignOptions

        opts = RichSignOptions(enable_audio_watermark=True, enable_video_watermark=True)
        assert opts.enable_audio_watermark is True
        assert opts.enable_video_watermark is True

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


class TestSignedAudioResult:
    def test_instantiation(self):
        from app.schemas.rich_sign_schemas import SignedAudioResult

        result = SignedAudioResult(
            audio_id="aud_aabbccdd11223344",
            filename="interview.wav",
            position=0,
            signed_audio_b64=make_wav_b64(),
            signed_audio_hash="sha256:" + "b" * 64,
            c2pa_manifest_instance_id="urn:uuid:11111111-2222-3333-4444-555555555555",
            size_bytes=2048,
            mime_type="audio/wav",
        )
        assert result.audio_id == "aud_aabbccdd11223344"
        assert result.watermark_applied is False
        assert result.c2pa_signed is True

    def test_watermark_applied(self):
        from app.schemas.rich_sign_schemas import SignedAudioResult

        result = SignedAudioResult(
            audio_id="aud_test",
            filename="clip.wav",
            position=0,
            signed_audio_b64=make_wav_b64(),
            signed_audio_hash="sha256:" + "c" * 64,
            c2pa_manifest_instance_id="urn:uuid:test",
            size_bytes=1024,
            mime_type="audio/wav",
            watermark_applied=True,
        )
        assert result.watermark_applied is True


class TestSignedVideoResult:
    def test_instantiation(self):
        from app.schemas.rich_sign_schemas import SignedVideoResult

        result = SignedVideoResult(
            video_id="vid_aabbccdd11223344",
            filename="intro.mp4",
            position=0,
            signed_video_b64=make_mp4_b64(),
            signed_video_hash="sha256:" + "d" * 64,
            c2pa_manifest_instance_id="urn:uuid:66666666-7777-8888-9999-aaaaaaaaaaaa",
            size_bytes=4096,
            mime_type="video/mp4",
        )
        assert result.video_id == "vid_aabbccdd11223344"
        assert result.watermark_applied is False
        assert result.c2pa_signed is True
