"""
Tests for diff tracking and version management.
"""
import pytest
from datetime import datetime
from encypher_enterprise.diff import (
    DiffGenerator,
    VersionTracker,
    VersionInfo,
    DiffStats,
    VersionMetadata,
    generate_diff_report
)


class TestDiffGenerator:
    """Test diff generation functionality."""
    
    def test_generate_diff_basic(self):
        """Test basic diff generation."""
        generator = DiffGenerator()
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 modified\nLine 3"
        
        diff = generator.generate_diff(old_content, new_content)
        
        assert diff is not None
        assert "Line 2" in diff
        assert "modified" in diff
    
    def test_generate_diff_empty(self):
        """Test diff with empty content."""
        generator = DiffGenerator()
        diff = generator.generate_diff("", "New content")
        
        assert diff is not None
        assert "New content" in diff
    
    def test_generate_diff_identical(self):
        """Test diff with identical content."""
        generator = DiffGenerator()
        content = "Same content"
        diff = generator.generate_diff(content, content)
        
        # Identical content should produce minimal diff
        assert diff == ""
    
    def test_calculate_stats_additions(self):
        """Test stats calculation for additions."""
        generator = DiffGenerator()
        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nLine 2\nLine 3\nLine 4"
        
        stats = generator.calculate_stats(old_content, new_content)
        
        assert stats.lines_added == 2
        assert stats.lines_removed == 0
        assert stats.total_changes == 2
        assert stats.similarity_ratio > 0.5
    
    def test_calculate_stats_deletions(self):
        """Test stats calculation for deletions."""
        generator = DiffGenerator()
        old_content = "Line 1\nLine 2\nLine 3\nLine 4"
        new_content = "Line 1\nLine 2"
        
        stats = generator.calculate_stats(old_content, new_content)
        
        assert stats.lines_added == 0
        assert stats.lines_removed == 2
        assert stats.total_changes == 2
    
    def test_calculate_stats_modifications(self):
        """Test stats calculation for modifications."""
        generator = DiffGenerator()
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 modified\nLine 3 modified"
        
        stats = generator.calculate_stats(old_content, new_content)
        
        assert stats.lines_modified > 0
        assert stats.total_changes > 0
    
    def test_calculate_stats_identical(self):
        """Test stats for identical content."""
        generator = DiffGenerator()
        content = "Same content"
        stats = generator.calculate_stats(content, content)
        
        assert stats.lines_added == 0
        assert stats.lines_removed == 0
        assert stats.lines_modified == 0
        assert stats.total_changes == 0
        assert stats.similarity_ratio == 1.0
    
    def test_identify_changed_sections(self):
        """Test identification of changed sections."""
        generator = DiffGenerator()
        old_content = "Para 1\n\nPara 2\n\nPara 3"
        new_content = "Para 1\n\nPara 2 modified\n\nPara 3"
        
        changed = generator.identify_changed_sections(old_content, new_content)
        
        assert len(changed) > 0
        # Should identify that Para 2 changed
        assert any("Para 2" in str(section) for _, section, _ in changed)
    
    def test_generate_html_diff(self):
        """Test HTML diff generation."""
        generator = DiffGenerator()
        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nLine 2 modified"
        
        html = generator.generate_html_diff(old_content, new_content, title="Test Diff")
        
        assert html is not None
        assert "Test Diff" in html or "html" in html.lower()
        assert len(html) > 100  # Should be substantial HTML


class TestVersionTracker:
    """Test version tracking functionality."""
    
    def test_create_version_initial(self):
        """Test creating initial version."""
        tracker = VersionTracker()
        version = tracker.create_version(
            document_id="doc_123",
            content="Test content"
        )
        
        assert version.version_number == 1
        assert version.document_id == "doc_123"
        assert version.content_hash is not None
        assert version.previous_version_id is None
    
    def test_create_version_with_previous(self):
        """Test creating version with previous version."""
        tracker = VersionTracker()
        version = tracker.create_version(
            document_id="doc_124",
            content="New content",
            previous_version_id="doc_123",
            version_number=2
        )
        
        assert version.version_number == 2
        assert version.document_id == "doc_124"
        assert version.previous_version_id == "doc_123"
    
    def test_generate_version_diff(self):
        """Test generating diff between versions."""
        tracker = VersionTracker()
        old_content = "Old content\nLine 2"
        new_content = "New content\nLine 2"
        
        diff_info = tracker.generate_version_diff(
            old_content,
            new_content,
            "doc_old",
            "doc_new"
        )
        
        assert diff_info["old_version_id"] == "doc_old"
        assert diff_info["new_version_id"] == "doc_new"
        assert "diff" in diff_info
        assert "stats" in diff_info
        assert diff_info["stats"]["total_changes"] > 0
    
    def test_version_info_to_dict(self):
        """Test VersionInfo serialization."""
        version = VersionInfo(
            version_number=1,
            document_id="doc_123",
            content_hash="abc123",
            previous_version_id=None,
            created_at=datetime(2025, 10, 29, 12, 0, 0)
        )
        
        data = version.to_dict()
        
        assert data["version_number"] == 1
        assert data["document_id"] == "doc_123"
        assert data["content_hash"] == "abc123"
        assert data["previous_version_id"] is None
        assert "2025-10-29" in data["created_at"]


class TestVersionMetadata:
    """Test version metadata for C2PA."""
    
    def test_create_version_assertion(self):
        """Test creating C2PA version assertion."""
        version = VersionInfo(
            version_number=2,
            document_id="doc_124",
            content_hash="def456",
            previous_version_id="doc_123",
            created_at=datetime.utcnow()
        )
        
        assertion = VersionMetadata.create_version_assertion(version)
        
        assert assertion["label"] == "encypher.version"
        assert assertion["data"]["version_number"] == 2
        assert assertion["data"]["document_id"] == "doc_124"
        assert assertion["data"]["previous_version_id"] == "doc_123"
    
    def test_create_version_assertion_with_diff(self):
        """Test creating assertion with diff summary."""
        version = VersionInfo(
            version_number=2,
            document_id="doc_124",
            content_hash="def456"
        )
        
        diff_summary = {
            "lines_added": 5,
            "lines_removed": 2,
            "total_changes": 7
        }
        
        assertion = VersionMetadata.create_version_assertion(version, diff_summary)
        
        assert "diff_summary" in assertion["data"]
        assert assertion["data"]["diff_summary"]["lines_added"] == 5
    
    def test_extract_version_info(self):
        """Test extracting version info from metadata."""
        metadata = {
            "custom": {
                "encypher.version": {
                    "version_number": 3,
                    "document_id": "doc_125",
                    "content_hash": "ghi789",
                    "previous_version_id": "doc_124",
                    "created_at": "2025-10-29T12:00:00"
                }
            }
        }
        
        version = VersionMetadata.extract_version_info(metadata)
        
        assert version is not None
        assert version.version_number == 3
        assert version.document_id == "doc_125"
        assert version.previous_version_id == "doc_124"
    
    def test_extract_version_info_missing(self):
        """Test extracting when version info is missing."""
        metadata = {"custom": {}}
        
        version = VersionMetadata.extract_version_info(metadata)
        
        assert version is None


class TestDiffStats:
    """Test DiffStats dataclass."""
    
    def test_diff_stats_to_dict(self):
        """Test DiffStats serialization."""
        stats = DiffStats(
            lines_added=10,
            lines_removed=5,
            lines_modified=3,
            total_changes=18,
            similarity_ratio=0.75
        )
        
        data = stats.to_dict()
        
        assert data["lines_added"] == 10
        assert data["lines_removed"] == 5
        assert data["lines_modified"] == 3
        assert data["total_changes"] == 18
        assert data["similarity_ratio"] == 0.75


class TestGenerateDiffReport:
    """Test diff report generation function."""
    
    def test_generate_text_report(self):
        """Test generating text diff report."""
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 modified\nLine 3\nLine 4"
        
        report = generate_diff_report(
            old_content,
            new_content,
            old_version="v1",
            new_version="v2",
            format="text"
        )
        
        assert "v1" in report
        assert "v2" in report
        assert "Statistics" in report
        assert "Lines added" in report
    
    def test_generate_json_report(self):
        """Test generating JSON diff report."""
        import json
        
        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nLine 2 modified"
        
        report = generate_diff_report(
            old_content,
            new_content,
            old_version="v1",
            new_version="v2",
            format="json"
        )
        
        data = json.loads(report)
        assert data["old_version"] == "v1"
        assert data["new_version"] == "v2"
        assert "diff" in data
        assert "stats" in data
    
    def test_generate_html_report(self):
        """Test generating HTML diff report."""
        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nLine 2 modified"
        
        report = generate_diff_report(
            old_content,
            new_content,
            old_version="v1",
            new_version="v2",
            format="html"
        )
        
        assert "html" in report.lower()
        assert len(report) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
