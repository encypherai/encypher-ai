"""
Tests for state management (incremental signing).
"""
import json
import tempfile
from pathlib import Path

import pytest

from encypher_enterprise.state import StateManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def state_file(temp_dir):
    """Create a temporary state file."""
    return temp_dir / ".encypher-state.json"


@pytest.fixture
def test_file(temp_dir):
    """Create a test file."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("Hello, World!")
    return file_path


def test_state_manager_init(state_file):
    """Test StateManager initialization."""
    manager = StateManager(state_file)
    assert manager.state_file == state_file
    assert manager.state == {}


def test_get_file_hash(state_file, test_file):
    """Test file hash calculation."""
    manager = StateManager(state_file)
    hash1 = manager.get_file_hash(test_file)
    
    # Hash should be consistent
    hash2 = manager.get_file_hash(test_file)
    assert hash1 == hash2
    
    # Hash should change when file changes
    test_file.write_text("Different content")
    hash3 = manager.get_file_hash(test_file)
    assert hash1 != hash3


def test_has_changed_new_file(state_file, test_file):
    """Test detecting new files."""
    manager = StateManager(state_file)
    assert manager.has_changed(test_file) is True


def test_has_changed_unchanged_file(state_file, test_file):
    """Test detecting unchanged files."""
    manager = StateManager(state_file)
    
    # Update state
    manager.update_file_state(test_file, "doc_123")
    
    # File should not have changed
    assert manager.has_changed(test_file) is False


def test_has_changed_modified_file(state_file, test_file):
    """Test detecting modified files."""
    manager = StateManager(state_file)
    
    # Update state
    manager.update_file_state(test_file, "doc_123")
    
    # Modify file
    test_file.write_text("Modified content")
    
    # File should have changed
    assert manager.has_changed(test_file) is True


def test_update_file_state(state_file, test_file):
    """Test updating file state."""
    manager = StateManager(state_file)
    
    manager.update_file_state(test_file, "doc_123")
    
    file_key = str(test_file.resolve())
    assert file_key in manager.state
    
    state = manager.state[file_key]
    assert state.document_id == "doc_123"
    assert state.file_hash == manager.get_file_hash(test_file)
    assert state.file_size == test_file.stat().st_size


def test_save_and_load_state(state_file, test_file):
    """Test saving and loading state."""
    # Create and save state
    manager1 = StateManager(state_file)
    manager1.update_file_state(test_file, "doc_123")
    manager1.save_state()
    
    # Load state in new manager
    manager2 = StateManager(state_file)
    
    file_key = str(test_file.resolve())
    assert file_key in manager2.state
    assert manager2.state[file_key].document_id == "doc_123"


def test_get_changed_files(state_file, temp_dir):
    """Test filtering changed files."""
    manager = StateManager(state_file)
    
    # Create test files
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    file3 = temp_dir / "file3.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    file3.write_text("Content 3")
    
    # Update state for file1 and file2
    manager.update_file_state(file1, "doc_1")
    manager.update_file_state(file2, "doc_2")
    
    # Modify file2
    file2.write_text("Modified content 2")
    
    # Get changed files
    all_files = [file1, file2, file3]
    changed = manager.get_changed_files(all_files)
    
    # file2 (modified) and file3 (new) should be in changed
    assert file1 not in changed
    assert file2 in changed
    assert file3 in changed


def test_get_new_files(state_file, temp_dir):
    """Test filtering new files."""
    manager = StateManager(state_file)
    
    # Create test files
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    
    # Update state for file1
    manager.update_file_state(file1, "doc_1")
    
    # Get new files
    all_files = [file1, file2]
    new_files = manager.get_new_files(all_files)
    
    # Only file2 should be new
    assert file1 not in new_files
    assert file2 in new_files


def test_get_deleted_files(state_file, temp_dir):
    """Test detecting deleted files."""
    manager = StateManager(state_file)
    
    # Create test files
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    
    # Update state for both files
    manager.update_file_state(file1, "doc_1")
    manager.update_file_state(file2, "doc_2")
    
    # Delete file2
    file2.unlink()
    
    # Get deleted files
    current_files = {file1}
    deleted = manager.get_deleted_files(current_files)
    
    # file2 should be in deleted
    assert str(file2.resolve()) in deleted
    assert str(file1.resolve()) not in deleted


def test_remove_file(state_file, test_file):
    """Test removing file from state."""
    manager = StateManager(state_file)
    
    # Add file to state
    manager.update_file_state(test_file, "doc_123")
    
    file_key = str(test_file.resolve())
    assert file_key in manager.state
    
    # Remove file
    manager.remove_file(test_file)
    
    assert file_key not in manager.state


def test_get_file_state(state_file, test_file):
    """Test getting file state."""
    manager = StateManager(state_file)
    
    # No state initially
    assert manager.get_file_state(test_file) is None
    
    # Add state
    manager.update_file_state(test_file, "doc_123")
    
    # Get state
    state = manager.get_file_state(test_file)
    assert state is not None
    assert state.document_id == "doc_123"


def test_get_statistics(state_file, temp_dir):
    """Test getting state statistics."""
    manager = StateManager(state_file)
    
    # Empty state
    stats = manager.get_statistics()
    assert stats['total_files'] == 0
    assert stats['total_size'] == 0
    
    # Add files
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    
    manager.update_file_state(file1, "doc_1")
    manager.update_file_state(file2, "doc_2")
    
    # Get stats
    stats = manager.get_statistics()
    assert stats['total_files'] == 2
    assert stats['total_size'] > 0
    assert stats['oldest_signature'] is not None
    assert stats['newest_signature'] is not None


def test_corrupted_state_file(state_file):
    """Test handling corrupted state file."""
    # Write invalid JSON
    state_file.write_text("invalid json {")
    
    # Should start with empty state
    manager = StateManager(state_file)
    assert manager.state == {}


def test_state_file_version(state_file, test_file):
    """Test state file version handling."""
    manager = StateManager(state_file)
    manager.update_file_state(test_file, "doc_123")
    manager.save_state()
    
    # Check version in saved file
    with open(state_file, 'r') as f:
        data = json.load(f)
    
    assert data['version'] == '1.0'
    assert 'last_updated' in data
    assert 'files' in data


def test_atomic_save(state_file, test_file):
    """Test atomic save operation."""
    manager = StateManager(state_file)
    manager.update_file_state(test_file, "doc_123")
    
    # Save should be atomic (no .tmp file left behind)
    manager.save_state()
    
    assert state_file.exists()
    assert not state_file.with_suffix('.tmp').exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
