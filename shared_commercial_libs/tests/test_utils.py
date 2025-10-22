"""
Unit tests for the utility functions in the shared commercial library.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import csv
from pathlib import Path

from encypher_commercial_shared import EncypherAI, VerificationResult
from encypher_commercial_shared.utils import scan_directory, generate_report, load_trusted_signers_from_directory as load_trusted_signers


class TestUtils(unittest.TestCase):
    """Test cases for the utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.encypher = MagicMock(spec=EncypherAI)
        
        # Create mock verification results
        self.mock_result1 = VerificationResult(
            verified=True,
            signer_id="test-signer",
            raw_payload={"timestamp": "2025-06-03T11:00:00", "model_id": "test-model"}
        )
        self.mock_result2 = VerificationResult(
            verified=False,
            signer_id=None,
            raw_payload={}
        )
        
        # Set up return values for the mock
        self.encypher.verify_from_file.side_effect = [self.mock_result1, self.mock_result2]

    @patch('encypher_commercial_shared.utils.Path')
    def test_scan_directory(self, mock_path):
        """Test scanning a directory for files with metadata."""
        # Set up mock directory structure
        mock_dir = MagicMock()
        mock_path.return_value = mock_dir
        
        # Mock the directory exists check
        mock_dir.exists.return_value = True
        
        # Mock the glob method to return some files
        mock_file1 = MagicMock()
        mock_file1.is_dir.return_value = False
        mock_file1.suffix = ".txt"
        mock_file1.__str__.return_value = "file1.txt"
        mock_file1.name = "file1.txt"
        
        mock_file2 = MagicMock()
        mock_file2.is_dir.return_value = False
        mock_file2.suffix = ".md"
        mock_file2.__str__.return_value = "file2.md"
        mock_file2.name = "file2.md"
        
        # Return a list that's already sorted
        mock_dir.glob.side_effect = [[mock_file1], [mock_file2]]
        
        # Call the function
        results = scan_directory(
            directory_path="/test/dir",
            encypher_ai=self.encypher,
            file_extensions=[".txt", ".md"],
            show_progress=False
        )
        
        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results["file1.txt"], self.mock_result1)
        self.assertEqual(results["file2.md"], self.mock_result2)
        
        # Verify the mock calls
        self.encypher.verify_from_file.assert_any_call("file1.txt")
        self.encypher.verify_from_file.assert_any_call("file2.md")

    def test_generate_report(self):
        """Test generating a CSV report from verification results."""
        # Create a temporary directory for the report
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, "test_report.csv")
            
            # Create some test results
            results = {
                "file1.txt": self.mock_result1,
                "file2.md": self.mock_result2
            }
            
            # Generate the report
            generate_report(results, report_path)
            
            # Verify the report was created
            self.assertTrue(os.path.exists(report_path))
            
            # Read the report and verify its contents
            with open(report_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                
                self.assertEqual(len(rows), 2)
                
                # Verify the first row
                self.assertEqual(rows[0]["File"], "file1.txt")
                self.assertEqual(rows[0]["Verified"], "True")
                self.assertEqual(rows[0]["Signer ID"], "test-signer")
                
                # Verify the second row
                self.assertEqual(rows[1]["File"], "file2.md")
                self.assertEqual(rows[1]["Verified"], "False")
                self.assertEqual(rows[1]["Signer ID"], "")

    @patch('encypher_commercial_shared.utils.Path')
    def test_load_trusted_signers(self, mock_path):
        """Test loading trusted signers from a directory."""
        # Set up mock directory structure
        mock_dir = MagicMock()
        mock_path.return_value = mock_dir
        
        # Mock the glob method to return some key files
        mock_key1 = MagicMock()
        mock_key1.stem = "signer1"
        mock_key1.__str__.return_value = "/test/keys/signer1.pem"
        
        mock_key2 = MagicMock()
        mock_key2.stem = "signer2"
        mock_key2.__str__.return_value = "/test/keys/signer2.pem"
        
        mock_dir.glob.return_value = [mock_key1, mock_key2]
        mock_dir.is_dir.return_value = True
        
        # Call the function
        trusted_signers = load_trusted_signers("/test/keys")
        
        # Verify the results
        self.assertEqual(len(trusted_signers), 2)
        self.assertEqual(trusted_signers["signer1"], "/test/keys/signer1.pem")
        self.assertEqual(trusted_signers["signer2"], "/test/keys/signer2.pem")


if __name__ == '__main__':
    unittest.main()
