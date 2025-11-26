"""
Integration tests for signing workflow using demo keys.

These tests use the demo API keys configured in dependencies.py,
which work without the key-service running (fallback mode).

NOTE: These tests have async event loop issues when run in sequence.
Run them individually or with a running server for reliable results.
"""
import os
import pytest
import unicodedata
from httpx import AsyncClient, ASGITransport

from app.main import app
from encypher.interop.c2pa import text_wrapper

# Skip all tests in this module unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("DEMO_KEY_TESTS", "").lower() != "true",
    reason="Demo key tests have async event loop issues. Set DEMO_KEY_TESTS=true to run."
)


@pytest.fixture
async def test_client():
    """Create async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestSigningWithDemoKeys:
    """Test signing flow using demo API keys (no key-service required)."""

    @pytest.mark.asyncio
    async def test_sign_verify_flow_demo_key(self, test_client: AsyncClient):
        """Test basic sign and verify flow with demo API key."""
        document_text = (
            "This is a test document for signing. "
            "It contains multiple sentences. "
            "Each sentence will be tracked."
        )
        
        # Sign the document
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer demo-api-key-for-testing"},
            json={
                "text": document_text,
                "document_title": "Demo Test Document",
                "document_url": "https://example.com/demo-test",
                "document_type": "article",
            },
        )
        
        assert sign_response.status_code == 200
        sign_data = sign_response.json()
        assert sign_data["success"] is True
        assert sign_data["total_sentences"] == 3
        signed_text = sign_data["signed_text"]
        document_id = sign_data["document_id"]
        assert document_id.startswith("doc_")
        
        # Verify the signed text
        verify_response = await test_client.post(
            "/api/v1/verify",
            json={"text": signed_text},
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["success"] is True
        verdict = verify_data["data"]
        assert verdict["valid"] is True
        assert verdict["tampered"] is False
        # Signer info comes from the manifest, not the database
        assert "signer_id" in verdict or "signer_name" in verdict

    @pytest.mark.asyncio
    async def test_sign_verify_with_business_key(self, test_client: AsyncClient):
        """Test sign and verify with business tier API key."""
        document_text = "Business tier signing test. Multiple features enabled."
        
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer business-api-key-for-testing"},
            json={
                "text": document_text,
                "document_title": "Business Test",
                "document_type": "article",
            },
        )
        
        assert sign_response.status_code == 200
        sign_data = sign_response.json()
        assert sign_data["success"] is True
        signed_text = sign_data["signed_text"]
        
        # Verify
        verify_response = await test_client.post(
            "/api/v1/verify",
            json={"text": signed_text},
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["data"]["valid"] is True
        # Signer ID should be present (may be org_business or from manifest)
        assert "signer_id" in verify_data["data"]

    @pytest.mark.asyncio
    async def test_signed_text_contains_manifest(self, test_client: AsyncClient):
        """Test that signed text contains C2PA manifest."""
        document_text = "Test document for manifest verification."
        
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer demo-api-key-for-testing"},
            json={"text": document_text},
        )
        
        assert sign_response.status_code == 200
        signed_text = sign_response.json()["signed_text"]
        
        # Extract manifest from signed text
        manifest_bytes, normalized_text, span = text_wrapper.find_and_decode(signed_text)
        
        assert manifest_bytes is not None
        assert span is not None
        assert signed_text.count("\ufeff") == 1  # BOM marker
        assert normalized_text == unicodedata.normalize("NFC", document_text)

    @pytest.mark.asyncio
    async def test_tamper_detection(self, test_client: AsyncClient):
        """Test that tampering is detected."""
        document_text = "Original text that should not be modified."
        
        # Sign
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer demo-api-key-for-testing"},
            json={"text": document_text},
        )
        
        signed_text = sign_response.json()["signed_text"]
        
        # Tamper with the text
        tampered_text = signed_text.replace("Original", "Modified")
        
        # Verify tampered text
        verify_response = await test_client.post(
            "/api/v1/verify",
            json={"text": tampered_text},
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        # Should detect tampering
        verdict = verify_data["data"]
        assert verdict["tampered"] is True or verdict["valid"] is False

    @pytest.mark.asyncio
    async def test_starter_tier_can_sign(self, test_client: AsyncClient):
        """Test that starter tier can sign documents."""
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer starter-api-key-for-testing"},
            json={"text": "Starter tier test document."},
        )
        
        assert sign_response.status_code == 200
        assert sign_response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_api_key_rejected(self, test_client: AsyncClient):
        """Test that invalid API keys are rejected."""
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer invalid-key-12345"},
            json={"text": "This should fail."},
        )
        
        assert sign_response.status_code == 401


class TestLookupWithDemoKeys:
    """Test lookup functionality with demo keys."""

    @pytest.mark.asyncio
    async def test_lookup_signed_sentence(self, test_client: AsyncClient):
        """Test looking up a signed sentence."""
        document_text = "This unique sentence will be looked up later."
        
        # Sign first
        sign_response = await test_client.post(
            "/api/v1/sign",
            headers={"Authorization": "Bearer demo-api-key-for-testing"},
            json={
                "text": document_text,
                "document_title": "Lookup Test",
            },
        )
        
        assert sign_response.status_code == 200
        
        # Lookup the sentence
        lookup_response = await test_client.post(
            "/api/v1/lookup",
            json={"sentence_text": "This unique sentence will be looked up later."},
        )
        
        assert lookup_response.status_code == 200
        lookup_data = lookup_response.json()
        assert lookup_data["success"] is True
        assert lookup_data["found"] is True
        assert lookup_data["organization_name"] == "Demo Organization"
