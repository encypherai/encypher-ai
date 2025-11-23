"""
Content diff tracking and version management.

Tracks changes between document versions and generates unified diffs.
"""
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import difflib
import hashlib


@dataclass
class DiffStats:
    """Statistics about changes between versions."""
    lines_added: int
    lines_removed: int
    lines_modified: int
    total_changes: int
    similarity_ratio: float  # 0.0 to 1.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "lines_modified": self.lines_modified,
            "total_changes": self.total_changes,
            "similarity_ratio": self.similarity_ratio
        }


@dataclass
class VersionInfo:
    """Information about a document version."""
    version_number: int
    document_id: str
    content_hash: str
    previous_version_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version_number": self.version_number,
            "document_id": self.document_id,
            "content_hash": self.content_hash,
            "previous_version_id": self.previous_version_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DiffGenerator:
    """
    Generate diffs between document versions.
    
    Example:
        >>> generator = DiffGenerator()
        >>> diff = generator.generate_diff("old content", "new content")
        >>> stats = generator.calculate_stats("old content", "new content")
        >>> print(f"Changes: {stats.total_changes}")
    """
    
    def generate_diff(
        self,
        old_content: str,
        new_content: str,
        context_lines: int = 3
    ) -> str:
        """
        Generate unified diff between two versions.
        
        Args:
            old_content: Original content
            new_content: Modified content
            context_lines: Number of context lines to show
        
        Returns:
            Unified diff string
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='previous',
            tofile='current',
            lineterm='',
            n=context_lines
        )
        
        return ''.join(diff)
    
    def generate_html_diff(
        self,
        old_content: str,
        new_content: str,
        title: str = "Content Diff"
    ) -> str:
        """
        Generate HTML diff with side-by-side comparison.
        
        Args:
            old_content: Original content
            new_content: Modified content
            title: Title for the diff page
        
        Returns:
            HTML string with diff visualization
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        differ = difflib.HtmlDiff()
        html = differ.make_file(
            old_lines,
            new_lines,
            fromdesc='Previous Version',
            todesc='Current Version',
            context=True,
            numlines=3
        )
        
        return html
    
    def calculate_stats(
        self,
        old_content: str,
        new_content: str
    ) -> DiffStats:
        """
        Calculate statistics about changes.
        
        Args:
            old_content: Original content
            new_content: Modified content
        
        Returns:
            DiffStats with change statistics
        """
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Use SequenceMatcher for detailed comparison
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        
        lines_added = 0
        lines_removed = 0
        lines_modified = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                lines_added += (j2 - j1)
            elif tag == 'delete':
                lines_removed += (i2 - i1)
            elif tag == 'replace':
                lines_modified += max(i2 - i1, j2 - j1)
        
        total_changes = lines_added + lines_removed + lines_modified
        similarity_ratio = matcher.ratio()
        
        return DiffStats(
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
            total_changes=total_changes,
            similarity_ratio=similarity_ratio
        )
    
    def identify_changed_sections(
        self,
        old_content: str,
        new_content: str,
        section_delimiter: str = "\n\n"
    ) -> List[Tuple[int, str, str]]:
        """
        Identify which sections (paragraphs) changed.
        
        Args:
            old_content: Original content
            new_content: Modified content
            section_delimiter: Delimiter for sections (default: double newline)
        
        Returns:
            List of (section_index, old_section, new_section) tuples
        """
        old_sections = old_content.split(section_delimiter)
        new_sections = new_content.split(section_delimiter)
        
        matcher = difflib.SequenceMatcher(None, old_sections, new_sections)
        changed_sections = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('replace', 'delete', 'insert'):
                for i in range(i1, i2):
                    old_sec = old_sections[i] if i < len(old_sections) else ""
                    new_sec = new_sections[j1] if j1 < len(new_sections) else ""
                    changed_sections.append((i, old_sec, new_sec))
        
        return changed_sections


class VersionTracker:
    """
    Track document versions and manage version history.
    
    Example:
        >>> tracker = VersionTracker()
        >>> version = tracker.create_version(
        ...     document_id="doc_123",
        ...     content="New content",
        ...     previous_version_id="doc_122"
        ... )
    """
    
    def __init__(self):
        """Initialize version tracker."""
        self.diff_generator = DiffGenerator()
    
    def create_version(
        self,
        document_id: str,
        content: str,
        previous_version_id: Optional[str] = None,
        version_number: Optional[int] = None
    ) -> VersionInfo:
        """
        Create a new version entry.
        
        Args:
            document_id: Current document ID
            content: Current content
            previous_version_id: Previous version's document ID
            version_number: Version number (auto-increments if None)
        
        Returns:
            VersionInfo object
        """
        content_hash = self._calculate_hash(content)
        
        if version_number is None:
            version_number = 1
        
        return VersionInfo(
            version_number=version_number,
            document_id=document_id,
            content_hash=content_hash,
            previous_version_id=previous_version_id,
            created_at=datetime.utcnow()
        )
    
    def generate_version_diff(
        self,
        old_content: str,
        new_content: str,
        old_version_id: str,
        new_version_id: str
    ) -> Dict:
        """
        Generate complete diff information between versions.
        
        Args:
            old_content: Previous version content
            new_content: Current version content
            old_version_id: Previous version document ID
            new_version_id: Current version document ID
        
        Returns:
            Dictionary with diff, stats, and metadata
        """
        diff_text = self.diff_generator.generate_diff(old_content, new_content)
        stats = self.diff_generator.calculate_stats(old_content, new_content)
        changed_sections = self.diff_generator.identify_changed_sections(
            old_content, new_content
        )
        
        return {
            "old_version_id": old_version_id,
            "new_version_id": new_version_id,
            "diff": diff_text,
            "stats": stats.to_dict(),
            "changed_sections_count": len(changed_sections),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class VersionMetadata:
    """
    Manage version metadata for C2PA manifests.
    
    Stores version information in C2PA custom assertions.
    """
    
    @staticmethod
    def create_version_assertion(
        version_info: VersionInfo,
        diff_summary: Optional[Dict] = None
    ) -> Dict:
        """
        Create C2PA custom assertion for version tracking.
        
        Args:
            version_info: Version information
            diff_summary: Optional diff summary
        
        Returns:
            Dictionary formatted for C2PA custom assertion
        """
        assertion = {
            "label": "encypher.version",
            "data": {
                "version_number": version_info.version_number,
                "document_id": version_info.document_id,
                "content_hash": version_info.content_hash,
                "previous_version_id": version_info.previous_version_id,
                "created_at": version_info.created_at.isoformat() if version_info.created_at else None
            }
        }
        
        if diff_summary:
            assertion["data"]["diff_summary"] = diff_summary
        
        return assertion
    
    @staticmethod
    def extract_version_info(metadata: Dict) -> Optional[VersionInfo]:
        """
        Extract version information from C2PA metadata.
        
        Args:
            metadata: C2PA metadata dictionary
        
        Returns:
            VersionInfo if found, None otherwise
        """
        custom = metadata.get("custom", {})
        version_data = custom.get("encypher.version")
        
        if not version_data:
            return None
        
        created_at = None
        if version_data.get("created_at"):
            created_at = datetime.fromisoformat(version_data["created_at"])
        
        return VersionInfo(
            version_number=version_data["version_number"],
            document_id=version_data["document_id"],
            content_hash=version_data["content_hash"],
            previous_version_id=version_data.get("previous_version_id"),
            created_at=created_at
        )


def generate_diff_report(
    old_content: str,
    new_content: str,
    old_version: str = "v1",
    new_version: str = "v2",
    format: str = "text"
) -> str:
    """
    Generate a diff report in various formats.
    
    Args:
        old_content: Previous version content
        new_content: Current version content
        old_version: Previous version label
        new_version: Current version label
        format: Output format ('text', 'html', 'json')
    
    Returns:
        Formatted diff report
    """
    generator = DiffGenerator()
    
    if format == "html":
        return generator.generate_html_diff(
            old_content,
            new_content,
            title=f"Diff: {old_version} → {new_version}"
        )
    elif format == "json":
        import json
        stats = generator.calculate_stats(old_content, new_content)
        diff_text = generator.generate_diff(old_content, new_content)
        
        return json.dumps({
            "old_version": old_version,
            "new_version": new_version,
            "diff": diff_text,
            "stats": stats.to_dict()
        }, indent=2)
    else:  # text
        diff_text = generator.generate_diff(old_content, new_content)
        stats = generator.calculate_stats(old_content, new_content)
        
        report = f"# Diff Report: {old_version} → {new_version}\n\n"
        report += "## Statistics\n"
        report += f"- Lines added: {stats.lines_added}\n"
        report += f"- Lines removed: {stats.lines_removed}\n"
        report += f"- Lines modified: {stats.lines_modified}\n"
        report += f"- Total changes: {stats.total_changes}\n"
        report += f"- Similarity: {stats.similarity_ratio:.1%}\n\n"
        report += f"## Diff\n\n```diff\n{diff_text}\n```\n"
        
        return report
