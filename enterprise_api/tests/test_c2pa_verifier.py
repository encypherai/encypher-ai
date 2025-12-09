"""
Tests for C2PA manifest verification utility.
"""
from unittest.mock import Mock, patch

import pytest

from app.utils.c2pa_verifier import (
    C2PAAssertion,
    C2PAVerificationResult,
    C2PAVerifier,
    verify_c2pa_manifest,
)


class TestC2PAVerificationResult:
    """Test C2PAVerificationResult dataclass."""
    
    def test_to_dict_basic(self):
        """Test converting result to dictionary."""
        result = C2PAVerificationResult(
            valid=True,
            manifest_url="https://example.com/manifest.json",
            manifest_hash="abc123"
        )
        
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
        assertion = C2PAAssertion(
            label="test.assertion",
            data={"key": "value"},
            verified=True
        )
        
        result = C2PAVerificationResult(
            valid=True,
            assertions=[assertion]
        )
        
        data = result.to_dict()
        
        assert len(data["assertions"]) == 1
        assert data["assertions"][0]["label"] == "test.assertion"
        assert data["assertions"][0]["verified"] is True


class TestC2PAVerifier:
    """Test C2PAVerifier class."""
    
    def test_verify_structure_valid(self):
        """Test structure verification with valid manifest."""
        verifier = C2PAVerifier()
        result = C2PAVerificationResult(valid=True)
        
        manifest = {
            "claim_generator": "Test Generator 1.0",
            "assertions": []
        }
        
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
            "assertions": []
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
                {
                    "label": "c2pa.actions",
                    "data": {"actions": ["created", "edited"]}
                },
                {
                    "label": "c2pa.hash.data",
                    "data": {"hash": "abc123"}
                }
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
        
        manifest = {
            "signature_info": {
                "issuer": "Test CA",
                "time": "2025-10-30T19:00:00Z",
                "alg": "RS256"
            }
        }
        
        verifier._extract_signatures(manifest, result)
        
        assert len(result.signatures) == 1
        assert result.signatures[0].issuer == "Test CA"
        assert result.signatures[0].algorithm == "RS256"
    
    def test_verify_manifest_data(self):
        """Test verifying manifest from data."""
        verifier = C2PAVerifier()
        
        manifest = {
            "claim_generator": "Test Generator 1.0",
            "assertions": [
                {
                    "label": "c2pa.actions",
                    "data": {"actions": ["created"]}
                }
            ],
            "signature_info": {
                "issuer": "Test CA",
                "alg": "RS256"
            }
        }
        
        result = verifier.verify_manifest_data(manifest)
        
        assert result.valid is True
        assert len(result.assertions) == 1
        assert len(result.signatures) == 1
        assert result.manifest_hash is not None
    
    @patch('app.utils.c2pa_verifier.requests.get')
    def test_verify_manifest_url_success(self, mock_get):
        """Test verifying manifest from URL."""
        verifier = C2PAVerifier()
        
        manifest = {
            "claim_generator": "Test Generator 1.0",
            "assertions": []
        }
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.json.return_value = manifest
        mock_response.content = b'{"claim_generator": "Test Generator 1.0", "assertions": []}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = verifier.verify_manifest_url("https://example.com/manifest.json")
        
        assert result.valid is True
        assert result.manifest_url == "https://example.com/manifest.json"
        assert result.manifest_hash is not None
    
    @patch('app.utils.c2pa_verifier.requests.get')
    def test_verify_manifest_url_http_error(self, mock_get):
        """Test verifying manifest with HTTP error."""
        verifier = C2PAVerifier()
        
        # Mock HTTP error
        mock_get.side_effect = Exception("Connection error")
        
        result = verifier.verify_manifest_url("https://example.com/manifest.json")
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert "Connection error" in result.errors[0]
    
    def test_convenience_function(self):
        """Test convenience function."""
        with patch('app.utils.c2pa_verifier.c2pa_verifier.verify_manifest_url') as mock_verify:
            mock_verify.return_value = C2PAVerificationResult(valid=True)
            
            result = verify_c2pa_manifest("https://example.com/manifest.json")
            
            assert result.valid is True
            mock_verify.assert_called_once_with("https://example.com/manifest.json")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
