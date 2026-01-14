"""Tests for GET /api/v1/verify/{document_id} endpoint."""
from unittest.mock import MagicMock

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata


def test_verify_by_document_id_returns_html_when_document_exists(client, mock_db, monkeypatch):
    """Test that verify_by_document_id returns HTML page when document exists."""
    private_key, public_key = generate_ed25519_key_pair()
    signer_id = "org_test"
    
    signed_text = UnicodeMetadata.embed_metadata(
        text="Hello world",
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )
    
    # Mock database response
    mock_row = MagicMock()
    mock_row._mapping = {
        "signed_text": signed_text,
        "title": "Test Document",
        "organization_id": "org_test",
    }
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/v1/verify/doc_123")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Test Document" in response.text
    assert "doc_123" in response.text
    assert "Content Verification" in response.text


def test_verify_by_document_id_returns_404_when_document_not_found(client, mock_db):
    """Test that verify_by_document_id returns 404 HTML when document doesn't exist."""
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/v1/verify/nonexistent_doc")
    
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Document Not Found" in response.text
    assert "nonexistent_doc" in response.text
    assert "Demo Organization Note" in response.text


def test_verify_by_document_id_handles_invalid_signature(client, mock_db):
    """Test that verify_by_document_id shows invalid status for tampered content."""
    # Create signed text with one key, but we won't provide the key for verification
    private_key, _ = generate_ed25519_key_pair()
    
    signed_text = UnicodeMetadata.embed_metadata(
        text="Original text",
        private_key=private_key,
        signer_id="org_test",
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )
    
    # Tamper with the text (this will break the signature)
    tampered_text = signed_text.replace("Original", "Tampered")
    
    mock_row = MagicMock()
    mock_row._mapping = {
        "signed_text": tampered_text,
        "title": "Tampered Document",
        "organization_id": "org_test",
    }
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/v1/verify/doc_tampered")
    
    assert response.status_code == 200
    assert "Invalid" in response.text or "SIGNATURE_INVALID" in response.text


def test_verify_by_document_id_handles_tuple_row_access(client, mock_db):
    """Test that verify_by_document_id handles rows without _mapping attribute."""
    private_key, _ = generate_ed25519_key_pair()
    
    signed_text = UnicodeMetadata.embed_metadata(
        text="Test content",
        private_key=private_key,
        signer_id="org_123",
        metadata_format="c2pa",
        target=MetadataTarget.WHITESPACE,
    )
    
    # Mock row as tuple (no _mapping attribute)
    mock_row = (signed_text, "Tuple Row Test", "org_123")
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/v1/verify/doc_tuple")
    
    assert response.status_code == 200
    assert "Tuple Row Test" in response.text
