"""
Tests for C2PA manifest verification utility.
"""

from __future__ import annotations

import socket
import base64
from unittest.mock import AsyncMock, Mock, patch

import pytest
from cryptography.hazmat.primitives import serialization

from app.utils.c2pa_verifier import (
    C2PAAssertion,
    C2PAVerificationResult,
    C2PAVerifier,
    verify_c2pa_manifest,
)
from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.payloads import serialize_c2pa_payload_to_cbor
from encypher.core.signing import sign_c2pa_cose


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
        import httpx
        from contextlib import asynccontextmanager

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
        import httpx
        from contextlib import asynccontextmanager

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
    async def test_convenience_function(self):
        """Test convenience function."""
        with patch("app.utils.c2pa_verifier.c2pa_verifier.verify_manifest_url", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = C2PAVerificationResult(valid=True)

            result = await verify_c2pa_manifest("https://example.com/manifest.json")

            assert result.valid is True
            mock_verify.assert_called_once_with("https://example.com/manifest.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
