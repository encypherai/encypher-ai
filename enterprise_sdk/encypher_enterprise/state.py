"""
State management for incremental signing.

Tracks file hashes to detect changes and avoid re-signing unchanged files.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FileState:
    """State information for a single file."""
    file_path: str
    file_hash: str
    document_id: str
    signed_at: str
    file_size: int
    version_number: int = 1
    previous_document_id: Optional[str] = None
    previous_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileState':
        """Create from dictionary."""
        # Handle old state files without version fields
        if 'version_number' not in data:
            data['version_number'] = 1
        if 'previous_document_id' not in data:
            data['previous_document_id'] = None
        if 'previous_hash' not in data:
            data['previous_hash'] = None
        return cls(**data)


class StateManager:
    """
    Manages signing state for incremental operations.
    
    Tracks which files have been signed and their hashes to detect changes.
    """
    
    def __init__(self, state_file: Path = Path(".encypher-state.json")):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to state file (default: .encypher-state.json)
        """
        self.state_file = state_file
        self.state: Dict[str, FileState] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        """Load state from file."""
        if not self.state_file.exists():
            self.state = {}
            return
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate version
            if data.get('version') != '1.0':
                # Migration logic could go here
                self.state = {}
                return
            
            # Load file states
            self.state = {
                path: FileState.from_dict(state_data)
                for path, state_data in data.get('files', {}).items()
            }
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Corrupted state file - start fresh
            print(f"Warning: Corrupted state file, starting fresh: {e}")
            self.state = {}
    
    def save_state(self) -> None:
        """Save state to file."""
        data = {
            'version': '1.0',
            'last_updated': datetime.utcnow().isoformat(),
            'files': {
                path: state.to_dict()
                for path, state in self.state.items()
            }
        }
        
        # Write atomically (write to temp, then rename)
        temp_file = self.state_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.state_file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise e
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def has_changed(self, file_path: Path) -> bool:
        """
        Check if file has changed since last signing.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if file is new or has changed, False if unchanged
        """
        file_key = str(file_path.resolve())
        
        # New file
        if file_key not in self.state:
            return True
        
        # Check if file still exists
        if not file_path.exists():
            return True
        
        # Compare hash
        current_hash = self.get_file_hash(file_path)
        stored_state = self.state[file_key]
        
        return current_hash != stored_state.file_hash
    
    def update_file_state(
        self,
        file_path: Path,
        document_id: str,
        track_versions: bool = False
    ) -> None:
        """
        Update state for a signed file.
        
        Args:
            file_path: Path to file
            document_id: Document ID from signing response
            track_versions: If True, track version history
        """
        file_key = str(file_path.resolve())
        current_hash = self.get_file_hash(file_path)
        
        # Get previous state if it exists
        previous_state = self.state.get(file_key)
        version_number = 1
        previous_document_id = None
        previous_hash = None
        
        if track_versions and previous_state:
            version_number = previous_state.version_number + 1
            previous_document_id = previous_state.document_id
            previous_hash = previous_state.file_hash
        
        self.state[file_key] = FileState(
            file_path=file_key,
            file_hash=current_hash,
            document_id=document_id,
            signed_at=datetime.utcnow().isoformat(),
            file_size=file_path.stat().st_size,
            version_number=version_number,
            previous_document_id=previous_document_id,
            previous_hash=previous_hash
        )
    
    def get_changed_files(self, files: list[Path]) -> list[Path]:
        """
        Filter list of files to only those that have changed.
        
        Args:
            files: List of file paths to check
        
        Returns:
            List of files that are new or have changed
        """
        return [f for f in files if self.has_changed(f)]
    
    def get_new_files(self, files: list[Path]) -> list[Path]:
        """
        Filter list of files to only new files (not in state).
        
        Args:
            files: List of file paths to check
        
        Returns:
            List of files not in state
        """
        return [
            f for f in files
            if str(f.resolve()) not in self.state
        ]
    
    def get_deleted_files(self, current_files: Set[Path]) -> list[str]:
        """
        Find files in state that no longer exist on disk.
        
        Args:
            current_files: Set of currently existing file paths
        
        Returns:
            List of file paths that are in state but not on disk
        """
        current_keys = {str(f.resolve()) for f in current_files}
        return [
            path for path in self.state.keys()
            if path not in current_keys
        ]
    
    def remove_file(self, file_path: Path) -> None:
        """
        Remove file from state.
        
        Args:
            file_path: Path to file to remove
        """
        file_key = str(file_path.resolve())
        if file_key in self.state:
            del self.state[file_key]
    
    def get_file_state(self, file_path: Path) -> Optional[FileState]:
        """
        Get state for a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            FileState if file is in state, None otherwise
        """
        file_key = str(file_path.resolve())
        return self.state.get(file_key)
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about current state.
        
        Returns:
            Dictionary with state statistics
        """
        return {
            'total_files': len(self.state),
            'total_size': sum(s.file_size for s in self.state.values()),
            'oldest_signature': min(
                (s.signed_at for s in self.state.values()),
                default=None
            ),
            'newest_signature': max(
                (s.signed_at for s in self.state.values()),
                default=None
            )
        }
