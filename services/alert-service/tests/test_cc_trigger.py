"""Tests for Claude Code investigation trigger."""

import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.cc_trigger import _sign_payload, trigger_if_critical, trigger_investigation


class TestSignPayload:
    def test_produces_hex_digest(self):
        sig = _sign_payload(b'{"test": true}', "secret123")
        assert len(sig) == 64
        assert all(c in "0123456789abcdef" for c in sig)

    def test_deterministic(self):
        payload = b'{"incident_id": "abc"}'
        assert _sign_payload(payload, "key") == _sign_payload(payload, "key")

    def test_different_keys_different_sigs(self):
        payload = b"same payload"
        assert _sign_payload(payload, "key1") != _sign_payload(payload, "key2")


class TestTriggerInvestigation:
    @pytest.fixture
    def mock_incident(self):
        incident = MagicMock()
        incident.id = "test-incident-123"
        incident.fingerprint = "abc123"
        incident.title = "[CRITICAL] auth-service: E_INTERNAL on /api/v1/auth/login"
        incident.severity = "critical"
        incident.service_name = "auth-service"
        incident.endpoint = "/api/v1/auth/login"
        incident.error_code = "E_INTERNAL"
        incident.occurrence_count = 5
        incident.sample_error = "Internal server error"
        incident.sample_stack = "Traceback..."
        incident.sample_request_id = "req-456"
        return incident

    @pytest.mark.asyncio
    async def test_returns_no_webhook_when_url_empty(self, mock_incident):
        with patch("app.services.cc_trigger.settings") as mock_settings:
            mock_settings.CC_WEBHOOK_URL = ""
            result = await trigger_investigation(mock_incident)
            assert result == "no_webhook"

    @pytest.mark.asyncio
    async def test_returns_triggered_on_success(self, mock_incident):
        with patch("app.services.cc_trigger.settings") as mock_settings:
            mock_settings.CC_WEBHOOK_URL = "http://localhost:9090"
            mock_settings.CC_WEBHOOK_SECRET = "test-secret"  # pragma: allowlist secret
            mock_settings.ALERT_SERVICE_URL = "http://localhost:8011"

            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_response.text = '{"status": "accepted"}'

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                result = await trigger_investigation(mock_incident)
                assert result == "triggered"

    @pytest.mark.asyncio
    async def test_includes_signature_header(self, mock_incident):
        with patch("app.services.cc_trigger.settings") as mock_settings:
            mock_settings.CC_WEBHOOK_URL = "http://localhost:9090"
            mock_settings.CC_WEBHOOK_SECRET = "my-secret"  # pragma: allowlist secret
            mock_settings.ALERT_SERVICE_URL = "http://localhost:8011"

            mock_response = MagicMock()
            mock_response.status_code = 202

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client_cls.return_value = mock_client

                await trigger_investigation(mock_incident)

                call_kwargs = mock_client.post.call_args
                headers = call_kwargs.kwargs.get("headers", {})
                assert "X-Signature-256" in headers
                assert headers["X-Signature-256"].startswith("sha256=")


class TestTriggerIfCritical:
    @pytest.fixture
    def mock_incident(self):
        incident = MagicMock()
        incident.id = "test-123"
        incident.severity = "critical"
        incident.fingerprint = "fp"
        incident.title = "test"
        incident.service_name = "svc"
        incident.endpoint = "/api"
        incident.error_code = "E_INTERNAL"
        incident.occurrence_count = 1
        incident.sample_error = "err"
        incident.sample_stack = None
        incident.sample_request_id = None
        return incident

    @pytest.mark.asyncio
    async def test_skips_non_critical(self, mock_incident):
        mock_incident.severity = "warning"
        result = await trigger_if_critical(mock_incident)
        assert result is None

    @pytest.mark.asyncio
    async def test_skips_when_auto_investigate_disabled(self, mock_incident):
        with patch("app.services.cc_trigger.settings") as mock_settings:
            mock_settings.CC_AUTO_INVESTIGATE = False
            result = await trigger_if_critical(mock_incident)
            assert result is None

    @pytest.mark.asyncio
    async def test_triggers_for_critical(self, mock_incident):
        with patch("app.services.cc_trigger.trigger_investigation", new_callable=AsyncMock) as mock_trigger:
            with patch("app.services.cc_trigger.settings") as mock_settings:
                mock_settings.CC_AUTO_INVESTIGATE = True
                mock_trigger.return_value = "triggered"
                result = await trigger_if_critical(mock_incident)
                assert result == "triggered"
                mock_trigger.assert_called_once_with(mock_incident, source="auto")
