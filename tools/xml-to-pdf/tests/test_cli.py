# TEAM_153: Tests for CLI entry point
"""Tests for the CLI interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from xml_to_pdf.cli import main

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
SAMPLE_XML = str(EXAMPLES_DIR / "content_provenance_paper.xml")


class TestCLIDryRun:
    """Test CLI dry-run mode (no API/PDF needed)."""

    def test_dry_run_parses_xml(self, capsys):
        ret = main([SAMPLE_XML, "--dry-run"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Content Provenance" in captured.out
        assert "Dr. Elena Vasquez" in captured.out

    def test_dry_run_shows_structure(self, capsys):
        ret = main([SAMPLE_XML, "--dry-run"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Sections: 5" in captured.out
        assert "References: 5" in captured.out

    def test_nonexistent_file(self, capsys):
        ret = main(["/nonexistent/file.xml"])
        assert ret == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestCLIUnsigned:
    """Test unsigned PDF generation."""

    def test_unsigned_pdf(self, tmp_path, capsys):
        out = str(tmp_path / "test.pdf")
        ret = main([SAMPLE_XML, "--unsigned", "-o", out])
        assert ret == 0
        assert Path(out).exists()
        assert Path(out).stat().st_size > 1000

    def test_unsigned_default_output(self, capsys, monkeypatch):
        monkeypatch.chdir(Path(__file__).parent.parent)
        ret = main([SAMPLE_XML, "--unsigned"])
        assert ret == 0
        # Default output goes to ./output/
        expected = Path("output/content_provenance_paper_unsigned.pdf")
        assert expected.exists()
        expected.unlink()  # cleanup


class TestCLIWithSigning:
    """Test CLI with mocked signing."""

    @patch("xml_to_pdf.cli.sign_text")
    def test_single_mode(self, mock_sign, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test")

        mock_sign.return_value = MagicMock(
            signed_text="signed\u200ccontent",
            document_id="doc-1",
            verification_url="https://v.test/1",
            total_segments=3,
            merkle_root="root123",
            instance_id="inst-1",
        )

        out = str(tmp_path / "c2pa.pdf")
        ret = main([SAMPLE_XML, "-m", "c2pa_full", "-o", out])
        assert ret == 0
        assert Path(out).exists()
        mock_sign.assert_called_once()

    @patch("xml_to_pdf.cli.sign_text")
    def test_all_modes(self, mock_sign, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("ENCYPHER_API_KEY", "test")
        monkeypatch.chdir(tmp_path)

        mock_sign.return_value = MagicMock(
            signed_text="signed\u200ccontent",
            document_id="doc-1",
            verification_url="https://v.test/1",
            total_segments=5,
            merkle_root="root123",
            instance_id="inst-1",
        )

        ret = main([SAMPLE_XML, "-m", "all"])
        assert ret == 0
        # Should call sign_text 5 times (one per mode)
        assert mock_sign.call_count == 5
        captured = capsys.readouterr()
        assert "5/5 PDFs generated" in captured.out
