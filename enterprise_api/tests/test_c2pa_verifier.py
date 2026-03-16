"""
Tests for C2PA manifest verification utility.
"""

from __future__ import annotations

import asyncio
import base64
import socket
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.payloads import serialize_c2pa_payload_to_cbor
from encypher.core.signing import sign_c2pa_cose

from app.config import settings
from app.services.session_service import session_service
from app.utils.c2pa_verifier import C2PAAssertion, C2PAVerificationResult, C2PAVerifier, verify_c2pa_manifest


class _FakeRedis:
    def __init__(self) -> None:
        self.sorted_sets: dict[str, dict[str, int]] = {}

    async def eval(self, script: str, *args):
        if len(args) == 6:
            _, key, now_ms, lease_ms, limit, token = args
            bucket = self.sorted_sets.setdefault(str(key), {})
            now_ms = int(now_ms)
            lease_ms = int(lease_ms)
            limit = int(limit)
            bucket = {entry: expiry for entry, expiry in bucket.items() if expiry > now_ms}
            self.sorted_sets[str(key)] = bucket
            if len(bucket) >= limit:
                return 0
            bucket[str(token)] = now_ms + lease_ms
            return 1

        if len(args) == 3:
            _, key, token = args
            bucket = self.sorted_sets.setdefault(str(key), {})
            bucket.pop(str(token), None)
            return 1

        raise AssertionError(f"Unexpected eval args: {args}")


class TestC2PAVerificationResult:
    """Test C2PAVerificationResult dataclass."""

    def test_to_dict_basic(self):
        """Test converting result to dictionary."""
        result = C2PAVerificationResult(valid=True, manifest_url="https://example.com/manifest.json", manifest_hash="abc123")

        data = result.to_dict()

        assert data["valid"] is True
        assert data["manifest_url"] == "https://example.com/manifest.json"
        assert data["manifest_hash"] == "abc123"
        assert data["assertions"] == []
        assert data["signatures"] == []
        assert data["errors"] == []
        assert data["warnings"] == []

    def test_to_dict_with_assertions(self):
        """Test converting result with assertions to dictionary."""
        assertion = C2PAAssertion(label="test.assertion", data={"key": "value"}, verified=True)

        result = C2PAVerificationResult(valid=True, assertions=[assertion])

        data = result.to_dict()

        assert len(data["assertions"]) == 1
        assert data["assertions"][0]["label"] == "test.assertion"
        assert data["assertions"][0]["verified"] is True


class TestC2PAVerifier:
    """Test C2PAVerifier class."""

    @pytest.mark.asyncio
    async def test_verify_manifest_url_rejects_http_scheme(self):
        # No mocks needed - early return before any network call
        verifier = C2PAVerifier()
        result = await verifier.verify_manifest_url("http://example.com/manifest.json")
        assert result.valid is False
        assert any("untrusted" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    async def test_verify_manifest_url_rejects_localhost(self):
        # No mocks needed - early return before any network call
        verifier = C2PAVerifier()
        result = await verifier.verify_manifest_url("https://localhost/manifest.json")
        assert result.valid is False
        assert any("untrusted" in err.lower() for err in result.errors)

    @pytest.mark.asyncio
    async def test_verify_manifest_url_rejects_private_ip(self):
        # No mocks needed - early return before any network call
        verifier = C2PAVerifier()
        result = await verifier.verify_manifest_url("https://127.0.0.1/manifest.json")
        assert result.valid is False
        assert any("untrusted" in err.lower() for err in result.errors)

    def test_verify_structure_valid(self):
        """Test structure verification with valid manifest."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)

        manifest = {"claim_generator": "Test Generator 1.0", "assertions": []}

        is_valid = verifier._verify_structure(manifest, result)

        assert is_valid is True
        assert len(result.errors) == 0

    def test_verify_structure_missing_field(self):
        """Test structure verification with missing required field."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)

        manifest = {
            "claim_generator": "Test Generator 1.0"
            # Missing 'assertions' field
        }

        is_valid = verifier._verify_structure(manifest, result)

        assert is_valid is False
        assert len(result.errors) > 0
        assert "assertions" in result.errors[0].lower()

    def test_verify_structure_invalid_claim_generator(self):
        """Test structure verification with invalid claim_generator."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)

        manifest = {
            "claim_generator": 123,  # Should be string
            "assertions": [],
        }

        is_valid = verifier._verify_structure(manifest, result)

        assert is_valid is False
        assert len(result.errors) > 0

    def test_extract_assertions(self):
        """Test extracting assertions from manifest."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)

        manifest = {
            "assertions": [
                {"label": "c2pa.actions", "data": {"actions": ["created", "edited"]}},
                {"label": "c2pa.hash.data", "data": {"hash": "abc123"}},
            ]
        }

        verifier._extract_assertions(manifest, result)

        assert len(result.assertions) == 2
        assert result.assertions[0].label == "c2pa.actions"
        assert result.assertions[1].label == "c2pa.hash.data"

    def test_extract_signatures(self):
        """Test extracting signatures from manifest."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)

        manifest = {"signature_info": {"issuer": "Test CA", "time": "2025-10-30T19:00:00Z", "alg": "RS256"}}

        verifier._extract_signatures(manifest, result)

        assert len(result.signatures) == 1
        assert result.signatures[0].issuer == "Test CA"
        assert result.signatures[0].algorithm == "RS256"

    def test_verify_manifest_data(self):
        """Test verifying manifest from data."""
        verifier = C2PAVerifier()

        manifest = {
            "claim_generator": "Test Generator 1.0",
            "assertions": [{"label": "c2pa.actions", "data": {"actions": ["created"]}}],
            "signature_info": {"issuer": "Test CA", "alg": "RS256"},
        }

        result = verifier.verify_manifest_data(manifest)

        assert result.valid is True
        assert len(result.assertions) == 1
        assert len(result.signatures) == 1
        assert result.manifest_hash is not None

    def test_verify_manifest_data_with_cose_signature(self):
        """Test cryptographic COSE signature verification."""
        private_key, public_key = generate_ed25519_key_pair()

        manifest_payload = {
            "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
            "instance_id": "urn:uuid:test",
            "claim_generator": "Test Generator",
            "assertions": [{"label": "c2pa.actions", "data": {"actions": ["created"]}}],
        }
        payload_bytes = serialize_c2pa_payload_to_cbor(manifest_payload)
        cose_bytes = sign_c2pa_cose(private_key, payload_bytes)
        cose_b64 = base64.b64encode(cose_bytes).decode("utf-8")

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        manifest_data = {
            "claim_generator": manifest_payload["claim_generator"],
            "assertions": manifest_payload["assertions"],
            "signature_info": {
                "issuer": "Test Issuer",
                "alg": "EdDSA",
                "cose_sign1": cose_b64,
                "public_key_pem": public_key_pem,
            },
        }

        verifier = C2PAVerifier()
        result = verifier.verify_manifest_data(manifest_data)

        assert result.valid is True
        assert result.signatures
        assert result.signatures[0].verified is True

    @pytest.mark.asyncio
    async def test_verify_manifest_url_success(self):
        """Test verifying manifest from URL."""
        from contextlib import asynccontextmanager

        import httpx

        verifier = C2PAVerifier()
        payload = b'{"claim_generator": "Test Generator 1.0", "assertions": []}'

        async def _aiter_bytes(chunk_size=8192):
            yield payload

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aiter_bytes = _aiter_bytes

        @asynccontextmanager
        async def mock_stream(*args, **kwargs):
            yield mock_response

        @asynccontextmanager
        async def mock_client_cm(*args, **kwargs):
            client = Mock()
            client.stream = mock_stream
            yield client

        with patch.object(httpx, "AsyncClient", mock_client_cm):
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is True
        assert result.manifest_url == "https://example.com/manifest.json"
        assert result.manifest_hash is not None

    @pytest.mark.asyncio
    async def test_verify_manifest_url_http_error(self):
        """Test verifying manifest with HTTP error."""
        from contextlib import asynccontextmanager

        import httpx

        verifier = C2PAVerifier()

        @asynccontextmanager
        async def mock_client_cm(*args, **kwargs):
            client = Mock()
            client.stream.side_effect = httpx.RequestError("Connection error")
            yield client

        with patch.object(httpx, "AsyncClient", mock_client_cm):
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is False
        assert len(result.errors) > 0
        assert "connection error" in result.errors[0].lower()

    @pytest.mark.asyncio
    async def test_verify_manifest_url_returns_busy_when_concurrency_slot_unavailable(self, monkeypatch):
        verifier = C2PAVerifier()
        monkeypatch.setattr("app.utils.c2pa_verifier.settings.remote_manifest_verify_acquire_timeout_seconds", 0.01)
        verifier._verification_semaphore = asyncio.Semaphore(1)

        await verifier._verification_semaphore.acquire()
        try:
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")
        finally:
            verifier._verification_semaphore.release()

        assert result.valid is False
        assert result.errors == ["Manifest verification busy; retry later"]

    @pytest.mark.asyncio
    async def test_verify_manifest_url_releases_concurrency_slot_after_fetch(self):
        from contextlib import asynccontextmanager

        import httpx

        verifier = C2PAVerifier()
        payload = b'{"claim_generator": "Test Generator 1.0", "assertions": []}'

        async def _aiter_bytes(chunk_size=8192):
            yield payload

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aiter_bytes = _aiter_bytes

        @asynccontextmanager
        async def mock_stream(*args, **kwargs):
            yield mock_response

        @asynccontextmanager
        async def mock_client_cm(*args, **kwargs):
            client = Mock()
            client.stream = mock_stream
            yield client

        initial_value = verifier._verification_semaphore._value
        with patch.object(httpx, "AsyncClient", mock_client_cm):
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is True
        assert verifier._verification_semaphore._value == initial_value

    @pytest.mark.asyncio
    async def test_verify_manifest_url_uses_cached_result(self):
        verifier = C2PAVerifier()
        cached_result = C2PAVerificationResult(valid=True, manifest_url="https://example.com/manifest.json", manifest_hash="cached")
        verifier._cache_result("https://example.com/manifest.json", cached_result)

        with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
            result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is True
        assert result.manifest_hash == "cached"

    @pytest.mark.asyncio
    async def test_verify_manifest_url_returns_busy_when_host_slot_unavailable(self, monkeypatch):
        verifier = C2PAVerifier()
        monkeypatch.setattr("app.utils.c2pa_verifier.settings.remote_manifest_verify_acquire_timeout_seconds", 0.01)
        verifier._host_semaphores["example.com"] = asyncio.Semaphore(1)

        await verifier._host_semaphores["example.com"].acquire()
        try:
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")
        finally:
            verifier._host_semaphores["example.com"].release()

        assert result.valid is False
        assert result.errors == ["Manifest verification busy; retry later"]

    @pytest.mark.asyncio
    async def test_verify_manifest_url_opens_host_circuit_after_failures(self, monkeypatch):
        from contextlib import asynccontextmanager

        import httpx

        verifier = C2PAVerifier()
        monkeypatch.setattr("app.utils.c2pa_verifier.settings.remote_manifest_verify_host_failure_threshold", 1)
        monkeypatch.setattr("app.utils.c2pa_verifier.settings.remote_manifest_verify_negative_cache_ttl_seconds", 0)

        @asynccontextmanager
        async def mock_client_cm(*args, **kwargs):
            client = Mock()
            client.stream.side_effect = httpx.RequestError("Connection error")
            yield client

        with patch.object(httpx, "AsyncClient", mock_client_cm):
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                first = await verifier.verify_manifest_url("https://example.com/manifest.json")
                second = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert first.valid is False
        assert any("connection error" in err.lower() for err in first.errors)
        assert second.valid is False
        assert second.errors == ["Manifest host temporarily unavailable"]

    @pytest.mark.asyncio
    async def test_verify_manifest_url_returns_busy_when_distributed_slot_unavailable(self, monkeypatch):
        verifier = C2PAVerifier()
        fake_redis = _FakeRedis()
        monkeypatch.setattr(settings, "remote_manifest_verify_distributed_limit_use_redis", True)
        monkeypatch.setattr(settings, "remote_manifest_verify_concurrency_limit", 1)
        monkeypatch.setattr(session_service, "redis_client", fake_redis)

        fake_redis.sorted_sets[verifier._distributed_limit_key("global")] = {"lease-1": int(time.time() * 1000) + 60_000}

        with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
            result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is False
        assert result.errors == ["Manifest verification busy; retry later"]

    @pytest.mark.asyncio
    async def test_verify_manifest_url_releases_distributed_leases_after_fetch(self, monkeypatch):
        from contextlib import asynccontextmanager

        import httpx

        verifier = C2PAVerifier()
        fake_redis = _FakeRedis()
        monkeypatch.setattr(settings, "remote_manifest_verify_distributed_limit_use_redis", True)
        monkeypatch.setattr(session_service, "redis_client", fake_redis)

        payload = b'{"claim_generator": "Test Generator 1.0", "assertions": []}'

        async def _aiter_bytes(chunk_size=8192):
            yield payload

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aiter_bytes = _aiter_bytes

        @asynccontextmanager
        async def mock_stream(*args, **kwargs):
            yield mock_response

        @asynccontextmanager
        async def mock_client_cm(*args, **kwargs):
            client = Mock()
            client.stream = mock_stream
            yield client

        with patch.object(httpx, "AsyncClient", mock_client_cm):
            with patch("app.utils.c2pa_verifier.socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
                result = await verifier.verify_manifest_url("https://example.com/manifest.json")

        assert result.valid is True
        assert fake_redis.sorted_sets[verifier._distributed_limit_key("global")] == {}
        assert fake_redis.sorted_sets[verifier._distributed_limit_key("host:example.com")] == {}

    def test_assertions_unverified_without_cose(self):
        """Assertions stay verified=False when no COSE signature is present."""
        verifier = C2PAVerifier()
        manifest = {
            "claim_generator": "Test Generator 1.0",
            "assertions": [
                {"label": "c2pa.actions", "data": {"actions": ["created"]}},
                {"label": "c2pa.hash.data", "data": {"hash": "abc123"}},
            ],
            "signature_info": {"issuer": "Test CA", "alg": "RS256"},
        }
        result = verifier.verify_manifest_data(manifest)
        assert len(result.assertions) == 2
        for a in result.assertions:
            assert a.verified is False

    def test_assertions_verified_with_valid_cose(self):
        """Assertions are upgraded to verified=True when a valid COSE signature covers them."""
        private_key, public_key = generate_ed25519_key_pair()
        manifest_payload = {
            "claim_generator": "Test Generator",
            "assertions": [{"label": "c2pa.actions", "data": {"actions": ["created"]}}],
        }
        payload_bytes = serialize_c2pa_payload_to_cbor(manifest_payload)
        cose_bytes = sign_c2pa_cose(private_key, payload_bytes)
        cose_b64 = base64.b64encode(cose_bytes).decode("utf-8")
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        manifest_data = {
            "claim_generator": manifest_payload["claim_generator"],
            "assertions": manifest_payload["assertions"],
            "signature_info": {
                "issuer": "Test Issuer",
                "alg": "EdDSA",
                "cose_sign1": cose_b64,
                "public_key_pem": public_key_pem,
            },
        }
        verifier = C2PAVerifier()
        result = verifier.verify_manifest_data(manifest_data)

        assert result.valid is True
        assert result.signatures[0].verified is True
        assert len(result.assertions) == 1
        assert result.assertions[0].verified is True

    def test_assertions_unverified_on_tampered_manifest(self):
        """Assertions stay verified=False when manifest assertions are tampered after signing."""
        private_key, public_key = generate_ed25519_key_pair()
        original_assertions = [{"label": "c2pa.actions", "data": {"actions": ["created"]}}]
        manifest_payload = {
            "claim_generator": "Test Generator",
            "assertions": original_assertions,
        }
        payload_bytes = serialize_c2pa_payload_to_cbor(manifest_payload)
        cose_bytes = sign_c2pa_cose(private_key, payload_bytes)
        cose_b64 = base64.b64encode(cose_bytes).decode("utf-8")
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Tamper: change the assertion label in the manifest but not in the signed payload
        tampered_assertions = [{"label": "c2pa.TAMPERED", "data": {"actions": ["created"]}}]
        manifest_data = {
            "claim_generator": manifest_payload["claim_generator"],
            "assertions": tampered_assertions,
            "signature_info": {
                "issuer": "Test Issuer",
                "alg": "EdDSA",
                "cose_sign1": cose_b64,
                "public_key_pem": public_key_pem,
            },
        }
        verifier = C2PAVerifier()
        result = verifier.verify_manifest_data(manifest_data)

        # The COSE verification itself should catch the mismatch
        assert result.valid is False
        # Assertions should not be verified
        for a in result.assertions:
            assert a.verified is False

    def test_verified_payload_not_in_to_dict(self):
        """The _verified_payload field must not appear in to_dict() output."""
        result = C2PAVerificationResult(valid=True)
        result._verified_payload = {"claim_generator": "test", "assertions": []}
        data = result.to_dict()
        assert "_verified_payload" not in data
        assert "verified_payload" not in data

    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test convenience function."""
        with patch("app.utils.c2pa_verifier.c2pa_verifier.verify_manifest_url", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = C2PAVerificationResult(valid=True)

            result = await verify_c2pa_manifest("https://example.com/manifest.json")

            assert result.valid is True
            mock_verify.assert_called_once_with("https://example.com/manifest.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
