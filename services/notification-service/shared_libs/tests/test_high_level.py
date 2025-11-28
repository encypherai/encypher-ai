"""
Unit tests for the high-level API in the shared commercial library.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from encypher_commercial_shared import EncypherAI, VerificationResult


class TestEncypherAI(unittest.TestCase):
    """Test cases for the EncypherAI high-level API."""

    def setUp(self):
        """Set up test fixtures."""
        self.encypher = EncypherAI()

    def test_initialization(self):
        """Test that the EncypherAI class initializes correctly."""
        self.assertIsNotNone(self.encypher)
        self.assertEqual(self.encypher.verbose, False)
        self.assertEqual(self.encypher.trusted_signers, {})

    def test_initialization_with_options(self):
        """Test initialization with custom options."""
        trusted_signers = {"signer1": "path/to/key1.pem", "signer2": "path/to/key2.pem"}
        encypher = EncypherAI(verbose=True)
        # Manually set trusted signers for testing
        encypher.trusted_signers = trusted_signers

        self.assertTrue(encypher.verbose)
        self.assertEqual(encypher.trusted_signers, trusted_signers)

    @patch('encypher_commercial_shared.high_level.UnicodeMetadata.extract_metadata')
    @patch('encypher_commercial_shared.high_level.UnicodeMetadata.verify_metadata')
    def test_verify_from_text(self, mock_verify, mock_extract):
        """Test verifying metadata from text."""
        # Set up a trusted signer for the test
        self.encypher._trusted_signers = {"test-signer": "mock_key"}

        # Mock the extraction result
        mock_extract.return_value = {"timestamp": "2025-06-03T11:00:00", "model_id": "test-model", "signer_id": "test-signer"}

        # Mock the verification result
        mock_verify.return_value = (True, "test-signer", {"timestamp": "2025-06-03T11:00:00", "model_id": "test-model"})

        # Call the method
        result = self.encypher.verify_from_text("Test text with metadata")

        # Verify the result
        self.assertTrue(result.verified)
        self.assertEqual(result.signer_id, "test-signer")
        self.assertEqual(result.model_id, "test-model")

    @patch('encypher_commercial_shared.high_level.EncypherAI.verify_from_text')
    def test_verify_from_file(self, mock_verify_from_text):
        """Test verifying metadata from a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp:
            temp.write("Test content with metadata")
            temp_path = temp.name

        try:
            # Mock the verification result
            mock_result = VerificationResult(
                verified=True,
                signer_id="test-signer",
                raw_payload={"timestamp": "2025-06-03T11:00:00", "model_id": "test-model"}
            )
            mock_verify_from_text.return_value = mock_result

            # Call the method
            result = self.encypher.verify_from_file(temp_path)

            # Verify the result
            self.assertEqual(result, mock_result)
            mock_verify_from_text.assert_called_once()
        finally:
            # Clean up
            os.unlink(temp_path)

    @patch('encypher_commercial_shared.high_level.UnicodeMetadata.extract_metadata')
    def test_extract_metadata(self, mock_extract):
        """Test extracting metadata from text."""
        # Mock the extraction result
        mock_extract.return_value = {"metadata": "test-metadata"}

        # Call the method
        result = self.encypher.verify_from_text("Test text with metadata")

        # Verify that extract_metadata was called
        mock_extract.assert_called_once_with("Test text with metadata")


if __name__ == '__main__':
    unittest.main()
