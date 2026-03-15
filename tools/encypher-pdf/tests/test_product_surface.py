from __future__ import annotations

import json
from pathlib import Path

from encypher_pdf.cli import main as cli_main
from encypher_pdf.extractor import extract_signed_text, extract_text
from encypher_pdf.font_registry import list_supported_font_families, resolve_font_path
from encypher_pdf.inspector import inspect_pdf
from encypher_pdf.writer import Document, TextStyle


def test_supported_font_families_include_expected_aliases() -> None:
    families = list_supported_font_families()
    assert "roboto" in families
    assert "arial" in families
    assert "times" in families


def test_resolve_font_path_for_supported_family() -> None:
    resolved = resolve_font_path("roboto")
    assert resolved.path
    assert resolved.family == "roboto"


def test_extract_signed_text_and_inspect_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "signed.pdf"
    doc = Document(footer_text="footer")
    doc.add_text("Hello\ufe01World", TextStyle(font_family="times", bold=True))
    doc.set_signed_text("Hello\ufe01World")
    doc.save(str(pdf_path))

    assert extract_signed_text(pdf_path) == "Hello\ufe01World"
    assert extract_text(pdf_path) == "Hello\ufe01World"

    info = inspect_pdf(pdf_path)
    assert info["has_signed_text_stream"] is True
    assert info["page_count"] == 1
    assert 0xFE01 in info["invisible_codepoints"]
    assert info["font_count"] >= 1


def test_cli_generate_extract_inspect_verify(tmp_path: Path, capsys) -> None:
    text_path = tmp_path / "input.txt"
    expected_text = "Title line\n\nBody with invisible \u200b marker"
    text_path.write_text(expected_text, encoding="utf-8")
    pdf_path = tmp_path / "output.pdf"

    assert (
        cli_main(
            [
                "generate",
                str(text_path),
                str(pdf_path),
                "--title",
                "Sample",
                "--font-family",
                "arial",
            ]
        )
        == 0
    )

    assert pdf_path.exists()

    assert cli_main(["verify", str(pdf_path), str(text_path)]) == 0
    out = capsys.readouterr().out
    assert "verified" in out

    assert cli_main(["verify", str(pdf_path), str(text_path), "--prefer-text-layer"]) == 1
    verify_err = capsys.readouterr().err
    assert "Verification failed" in verify_err

    assert cli_main(["inspect", str(pdf_path), "--pretty"]) == 0
    inspect_out = capsys.readouterr().out
    inspect_json = json.loads(inspect_out)
    assert inspect_json["has_signed_text_stream"] is True

    assert cli_main(["extract", str(pdf_path), "--signed-only"]) == 0
    extract_out = capsys.readouterr().out
    assert expected_text in extract_out
