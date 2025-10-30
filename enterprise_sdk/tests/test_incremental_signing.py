"""
Integration tests for incremental signing.
"""
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

import pytest

from encypher_enterprise import RepositorySigner, FileMetadata
from encypher_enterprise.models import SignResponse


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = Mock()
    
    # Mock sign method
    def mock_sign(text, title=None, metadata=None):
        response = Mock(spec=SignResponse)
        response.document_id = f"doc_{hash(text) % 10000}"
        response.signed_text = f"SIGNED:{text}"
        response.verification_url = f"https://encypherai.com/verify/{response.document_id}"
        response.total_sentences = len(text.split('.'))
        return response
    
    client.sign = mock_sign
    return client


def test_incremental_signing_first_run(temp_dir, mock_client):
    """Test first run signs all files."""
    # Create test files
    (temp_dir / "file1.md").write_text("Content 1")
    (temp_dir / "file2.md").write_text("Content 2")
    (temp_dir / "file3.md").write_text("Content 3")
    
    signer = RepositorySigner(mock_client)
    
    result = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    # All files should be signed
    assert result.total_files == 3
    assert result.successful == 3
    assert result.skipped == 0
    
    # State file should exist
    state_file = temp_dir / ".encypher-state.json"
    assert state_file.exists()


def test_incremental_signing_no_changes(temp_dir, mock_client):
    """Test second run skips unchanged files."""
    # Create test files
    (temp_dir / "file1.md").write_text("Content 1")
    (temp_dir / "file2.md").write_text("Content 2")
    
    signer = RepositorySigner(mock_client)
    
    # First run
    result1 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    assert result1.total_files == 2
    assert result1.skipped == 0
    
    # Second run (no changes)
    result2 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    # All files should be skipped
    assert result2.total_files == 0
    assert result2.skipped == 2


def test_incremental_signing_with_changes(temp_dir, mock_client):
    """Test second run signs only changed files."""
    # Create test files
    file1 = temp_dir / "file1.md"
    file2 = temp_dir / "file2.md"
    file3 = temp_dir / "file3.md"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    file3.write_text("Content 3")
    
    signer = RepositorySigner(mock_client)
    
    # First run
    result1 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    assert result1.total_files == 3
    assert result1.skipped == 0
    
    # Modify file2
    file2.write_text("Modified content 2")
    
    # Second run
    result2 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    # Only file2 should be signed
    assert result2.total_files == 1
    assert result2.successful == 1
    assert result2.skipped == 2
    
    # Verify file2 was signed
    assert any(r.file_path == file2 for r in result2.results)


def test_incremental_signing_with_new_file(temp_dir, mock_client):
    """Test second run signs new files."""
    # Create initial files
    (temp_dir / "file1.md").write_text("Content 1")
    (temp_dir / "file2.md").write_text("Content 2")
    
    signer = RepositorySigner(mock_client)
    
    # First run
    result1 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    assert result1.total_files == 2
    
    # Add new file
    (temp_dir / "file3.md").write_text("Content 3")
    
    # Second run
    result2 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    # Only new file should be signed
    assert result2.total_files == 1
    assert result2.successful == 1
    assert result2.skipped == 2


def test_force_resign(temp_dir, mock_client):
    """Test force resign option."""
    # Create test files
    (temp_dir / "file1.md").write_text("Content 1")
    (temp_dir / "file2.md").write_text("Content 2")
    
    signer = RepositorySigner(mock_client)
    
    # First run
    result1 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True
    )
    
    assert result1.total_files == 2
    
    # Second run with force_resign
    result2 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True,
        force_resign=True
    )
    
    # All files should be re-signed
    assert result2.total_files == 2
    assert result2.successful == 2
    assert result2.skipped == 0


def test_custom_state_file(temp_dir, mock_client):
    """Test using custom state file."""
    # Create test files
    (temp_dir / "file1.md").write_text("Content 1")
    
    custom_state = temp_dir / "custom-state.json"
    
    signer = RepositorySigner(mock_client)
    
    result = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=True,
        state_file=custom_state
    )
    
    assert result.total_files == 1
    assert custom_state.exists()
    
    # Default state file should not exist
    default_state = temp_dir / ".encypher-state.json"
    assert not default_state.exists()


def test_incremental_without_flag(temp_dir, mock_client):
    """Test that incremental=False signs all files every time."""
    # Create test files
    (temp_dir / "file1.md").write_text("Content 1")
    (temp_dir / "file2.md").write_text("Content 2")
    
    signer = RepositorySigner(mock_client)
    
    # First run
    result1 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=False
    )
    
    assert result1.total_files == 2
    
    # Second run (should sign all files again)
    result2 = signer.sign_directory(
        directory=temp_dir,
        patterns=["*.md"],
        incremental=False
    )
    
    # All files should be signed again
    assert result2.total_files == 2
    assert result2.skipped == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
