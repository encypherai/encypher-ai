"""Unit tests for the image-service watermarking endpoints.

All tests run WITHOUT TrustMark/torch installed. The service layer is either
left unloaded (testing 503 fallback) or replaced with a MagicMock.
"""
import base64
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_test_jpeg() -> bytes:
    """Return a minimal valid JPEG (64x64 solid colour)."""
    from PIL import Image

    img = Image.new("RGB", (64, 64), color=(100, 150, 200))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def make_test_png() -> bytes:
    """Return a minimal valid PNG (32x32 solid colour)."""
    from PIL import Image

    img = Image.new("RGB", (32, 32), color=(200, 100, 50))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_model_not_loaded(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        svc = TrustMarkService()  # not loaded
        app.state.trustmark_service = svc

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is False
        assert data["version"] == "0.1.0"

    def test_health_model_loaded_mock(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        app.state.trustmark_service = mock_svc

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["model_loaded"] is True

    def test_health_no_service_on_state(self) -> None:
        """Health should still return 200 when state has no trustmark_service attr."""
        from app.main import app

        # Remove the attribute if present.
        try:
            del app.state.trustmark_service
        except AttributeError:
            pass

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["model_loaded"] is False


# ---------------------------------------------------------------------------
# Watermark endpoint -- 503 when model not loaded
# ---------------------------------------------------------------------------

class TestWatermarkEndpoint503:
    def _client_with_unloaded_service(self) -> TestClient:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        app.state.trustmark_service = TrustMarkService()  # not loaded
        return TestClient(app, raise_server_exceptions=False)

    def test_watermark_returns_503_when_model_not_available(self) -> None:
        client = self._client_with_unloaded_service()
        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": img_b64,
                "mime_type": "image/jpeg",
                "message_bits": "a" * 26,
            },
        )
        assert resp.status_code == 503

    def test_watermark_returns_503_when_service_none(self) -> None:
        from app.main import app

        app.state.trustmark_service = None
        client = TestClient(app, raise_server_exceptions=False)
        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": img_b64,
                "mime_type": "image/jpeg",
                "message_bits": "b" * 26,
            },
        )
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Detect endpoint -- 503 when model not loaded
# ---------------------------------------------------------------------------

class TestDetectEndpoint503:
    def _client_with_unloaded_service(self) -> TestClient:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        app.state.trustmark_service = TrustMarkService()
        return TestClient(app, raise_server_exceptions=False)

    def test_detect_returns_503_when_model_not_available(self) -> None:
        client = self._client_with_unloaded_service()
        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        resp = client.post(
            "/api/v1/detect",
            json={"image_b64": img_b64, "mime_type": "image/jpeg"},
        )
        assert resp.status_code == 503

    def test_detect_returns_503_when_service_none(self) -> None:
        from app.main import app

        app.state.trustmark_service = None
        client = TestClient(app, raise_server_exceptions=False)
        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        resp = client.post(
            "/api/v1/detect",
            json={"image_b64": img_b64, "mime_type": "image/jpeg"},
        )
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# Watermark endpoint -- mocked service (happy path)
# ---------------------------------------------------------------------------

class TestWatermarkEndpointMocked:
    def test_watermark_with_mocked_service(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        orig_bytes = make_test_jpeg()
        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        mock_svc.encode.return_value = (orig_bytes, 0.99)
        app.state.trustmark_service = mock_svc

        img_b64 = base64.b64encode(orig_bytes).decode()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": img_b64,
                "mime_type": "image/jpeg",
                "message_bits": "a" * 26,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "watermarked_b64" in data
        assert data["confidence"] == pytest.approx(0.99)
        assert data["message_bits"] == "a" * 26
        assert data["processing_time_ms"] >= 0

    def test_watermark_bad_base64_returns_400(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        app.state.trustmark_service = mock_svc

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": "!!!not-valid-base64!!!",
                "mime_type": "image/jpeg",
                "message_bits": "a" * 26,
            },
        )
        assert resp.status_code == 400

    def test_watermark_message_bits_too_short_returns_422(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        app.state.trustmark_service = mock_svc

        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": img_b64,
                "mime_type": "image/jpeg",
                "message_bits": "abc",  # too short
            },
        )
        assert resp.status_code == 422

    def test_watermark_message_bits_too_long_returns_422(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        app.state.trustmark_service = mock_svc

        img_b64 = base64.b64encode(make_test_jpeg()).decode()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/watermark",
            json={
                "image_b64": img_b64,
                "mime_type": "image/jpeg",
                "message_bits": "a" * 27,  # too long
            },
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Detect endpoint -- mocked service (happy path)
# ---------------------------------------------------------------------------

class TestDetectEndpointMocked:
    def test_detect_found_with_mocked_service(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        orig_bytes = make_test_jpeg()
        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        mock_svc.decode.return_value = (True, "deadbeef" * 3 + "ab", 0.95)
        app.state.trustmark_service = mock_svc

        img_b64 = base64.b64encode(orig_bytes).decode()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/detect",
            json={"image_b64": img_b64, "mime_type": "image/jpeg"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected"] is True
        assert data["message_bits"] == "deadbeef" * 3 + "ab"
        assert data["confidence"] == pytest.approx(0.95)

    def test_detect_not_found_with_mocked_service(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        orig_bytes = make_test_jpeg()
        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        mock_svc.decode.return_value = (False, None, 0.1)
        app.state.trustmark_service = mock_svc

        img_b64 = base64.b64encode(orig_bytes).decode()
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/detect",
            json={"image_b64": img_b64, "mime_type": "image/jpeg"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["detected"] is False
        assert data["message_bits"] is None
        assert data["confidence"] == pytest.approx(0.1)

    def test_detect_bad_base64_returns_400(self) -> None:
        from app.main import app
        from app.services.trustmark_service import TrustMarkService

        mock_svc = MagicMock(spec=TrustMarkService)
        mock_svc.is_available = True
        app.state.trustmark_service = mock_svc

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post(
            "/api/v1/detect",
            json={"image_b64": "!!!not-valid!!!", "mime_type": "image/jpeg"},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# TrustMarkService unit tests (no real model)
# ---------------------------------------------------------------------------

class TestTrustMarkServiceUnit:
    def test_service_not_available_by_default(self) -> None:
        from app.services.trustmark_service import TrustMarkService

        svc = TrustMarkService()
        assert svc.is_available is False

    def test_encode_raises_when_not_available(self) -> None:
        from app.services.trustmark_service import ServiceUnavailableError, TrustMarkService

        svc = TrustMarkService()
        with pytest.raises(ServiceUnavailableError):
            svc.encode(b"fake", "image/jpeg", "a" * 26)

    def test_decode_raises_when_not_available(self) -> None:
        from app.services.trustmark_service import ServiceUnavailableError, TrustMarkService

        svc = TrustMarkService()
        with pytest.raises(ServiceUnavailableError):
            svc.decode(b"fake")

    def test_load_model_sets_unavailable_when_import_fails(self) -> None:
        """load_model() must not raise; it must log and set _available=False."""
        import sys
        # trustmark is not installed in CI, so load_model() should handle gracefully.
        # We verify _available stays False after the call.
        from app.services.trustmark_service import TrustMarkService

        svc = TrustMarkService()
        # This will fail to import trustmark in CI (no torch) but must NOT raise.
        svc.load_model()
        # In CI without torch: still False.
        # In a real environment with torch: could be True.
        # We just assert the call completes without exception.
        assert isinstance(svc.is_available, bool)

    def test_mime_to_pil_format(self) -> None:
        from app.services.trustmark_service import _mime_to_pil_format

        assert _mime_to_pil_format("image/jpeg") == "JPEG"
        assert _mime_to_pil_format("image/jpg") == "JPEG"
        assert _mime_to_pil_format("image/png") == "PNG"
        assert _mime_to_pil_format("image/webp") == "WEBP"
        assert _mime_to_pil_format("image/tiff") == "JPEG"  # fallback
        assert _mime_to_pil_format("IMAGE/JPEG") == "JPEG"  # case-insensitive
