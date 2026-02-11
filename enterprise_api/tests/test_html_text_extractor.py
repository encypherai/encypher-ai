"""
Unit tests for HTML text extractor (TEAM_169).

Tests that extract_text_from_html and extract_segments_from_html correctly
strip HTML tags while preserving only rendered text content.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.utils.html_text_extractor import (
    embed_signed_text_in_html,
    extract_segments_from_html,
    extract_text_from_html,
)

EXAMPLE_HTML_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "chesschampion"
    / "example_article.html"
)


@pytest.fixture
def simple_html() -> str:
    return (
        "<h1>Title</h1>"
        "<p>First paragraph sentence one. First paragraph sentence two.</p>"
        "<p>Second paragraph with <b>bold text</b> and <i>italic text</i>.</p>"
    )


@pytest.fixture
def html_with_lists() -> str:
    return (
        "<h2>Top Items</h2>"
        "<ol><li>First item</li><li>Second item</li><li>Third item</li></ol>"
        "<ul><li>Bullet one</li><li>Bullet two</li></ul>"
    )


@pytest.fixture
def html_with_links() -> str:
    return (
        '<p>Visit <a href="https://example.com">Example Site</a> for more info.</p>'
        '<p>Also see <a href="https://other.com" target="_blank">Other Site</a>.</p>'
    )


@pytest.fixture
def html_with_images() -> str:
    return (
        "<p>Here is some text before the image.</p>"
        '<img src="photo.jpg" alt="A photo" title="Photo Title" width="600" height="400">'
        "<p>Here is some text after the image.</p>"
    )


@pytest.fixture
def example_html() -> str:
    assert EXAMPLE_HTML_PATH.exists(), f"Example HTML not found: {EXAMPLE_HTML_PATH}"
    return EXAMPLE_HTML_PATH.read_text(encoding="utf-8")


class TestExtractTextFromHtml:
    def test_strips_tags_returns_rendered_text(self, simple_html):
        result = extract_text_from_html(simple_html)
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "<b>" not in result
        assert "<i>" not in result
        assert "Title" in result
        assert "First paragraph sentence one" in result
        assert "bold text" in result
        assert "italic text" in result

    def test_preserves_paragraph_boundaries(self, simple_html):
        result = extract_text_from_html(simple_html)
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        assert len(lines) >= 3, f"Expected at least 3 text blocks, got {len(lines)}: {lines}"
        assert lines[0] == "Title"
        assert "First paragraph" in lines[1]
        assert "Second paragraph" in lines[2]

    def test_handles_ordered_lists(self, html_with_lists):
        result = extract_text_from_html(html_with_lists)
        assert "First item" in result
        assert "Second item" in result
        assert "Third item" in result
        assert "Bullet one" in result
        assert "Bullet two" in result
        assert "<li>" not in result
        assert "<ol>" not in result

    def test_ignores_img_elements(self, html_with_images):
        result = extract_text_from_html(html_with_images)
        assert "photo.jpg" not in result
        assert "A photo" not in result
        assert "Photo Title" not in result
        assert "text before the image" in result
        assert "text after the image" in result

    def test_preserves_link_text_strips_href(self, html_with_links):
        result = extract_text_from_html(html_with_links)
        assert "Example Site" in result
        assert "Other Site" in result
        assert "https://example.com" not in result
        assert "https://other.com" not in result

    def test_preserves_inline_formatting_text(self, simple_html):
        result = extract_text_from_html(simple_html)
        assert "bold text" in result
        assert "italic text" in result

    def test_chesschampion_article_extraction(self, example_html):
        result = extract_text_from_html(example_html)
        assert "Best Chess Games of All Time" in result
        assert "Garry Kasparov" in result
        assert "Bobby Fischer" in result
        assert "Deep Blue" in result
        assert "Magnus Carlsen" in result
        assert "<h1" not in result
        assert "<h2" not in result
        assert "<p>" not in result
        assert "<img" not in result
        assert 'src="' not in result
        assert 'alt="' not in result
        assert len(result) > 5000, f"Expected substantial text, got {len(result)} chars"

    def test_empty_html(self):
        assert extract_text_from_html("") == ""
        assert extract_text_from_html("   ") == ""

    def test_plain_text_passthrough(self):
        plain = "Just a plain text sentence."
        result = extract_text_from_html(plain)
        assert result.strip() == plain


class TestEmbedSignedTextInHtml:
    """Tests for embed_signed_text_in_html (inject signed text back into HTML)."""

    def test_preserves_html_tags(self):
        """Output should still contain all original HTML tags."""
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            derive_signing_key_from_private_key,
            embed_signature_safely,
        )
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import uuid as uuid_mod

        html = "<h1>Title</h1><p>First sentence. Second sentence.</p>"
        text = extract_text_from_html(html)

        # Simulate signing: embed markers into the extracted text
        keypair = Ed25519PrivateKey.generate()
        signing_key = derive_signing_key_from_private_key(keypair)
        segments = text.split("\n")
        signed_segments = []
        for seg in segments:
            if not seg.strip():
                signed_segments.append(seg)
                continue
            sig = create_minimal_signed_uuid(uuid_mod.uuid4(), signing_key)
            signed_segments.append(embed_signature_safely(seg, sig))
        signed_text = "\n".join(signed_segments)

        result = embed_signed_text_in_html(html, signed_text)

        assert "<h1>" in result
        assert "</h1>" in result
        assert "<p>" in result
        assert "</p>" in result
        assert "Title" in result
        assert "First sentence" in result

    def test_preserves_img_tags(self):
        """img tags should remain untouched."""
        html = (
            "<p>Before image.</p>"
            '<img src="photo.jpg" alt="A photo" width="600">'
            "<p>After image.</p>"
        )
        text = extract_text_from_html(html)
        # Use text as-is (no actual signing, just test structure preservation)
        result = embed_signed_text_in_html(html, text)
        assert "src=\"photo.jpg\"" in result
        assert 'alt="A photo"' in result
        assert "Before image" in result
        assert "After image" in result

    def test_preserves_link_attributes(self):
        """Link href and attributes should remain untouched."""
        html = '<p>Visit <a href="https://example.com" target="_blank">Example</a> now.</p>'
        text = extract_text_from_html(html)
        result = embed_signed_text_in_html(html, text)
        assert 'href="https://example.com"' in result
        assert 'target="_blank"' in result
        assert "<a " in result
        assert "Example" in result

    def test_signed_html_longer_than_original(self):
        """When markers are present, the HTML output should be longer."""
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            derive_signing_key_from_private_key,
            embed_signature_safely,
        )
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import uuid as uuid_mod

        html = "<p>Hello world.</p>"
        text = extract_text_from_html(html)

        keypair = Ed25519PrivateKey.generate()
        signing_key = derive_signing_key_from_private_key(keypair)
        sig = create_minimal_signed_uuid(uuid_mod.uuid4(), signing_key)
        signed_text = embed_signature_safely(text, sig)

        result = embed_signed_text_in_html(html, signed_text)
        assert len(result) > len(html), "Signed HTML should be longer due to invisible markers"

    def test_markers_extractable_from_signed_html(self):
        """VS256 markers should be findable in the output HTML text nodes."""
        from app.utils.vs256_crypto import (
            create_minimal_signed_uuid,
            derive_signing_key_from_private_key,
            embed_signature_safely,
            find_all_minimal_signed_uuids,
        )
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import uuid as uuid_mod

        html = "<h1>Title</h1><p>Sentence one. Sentence two.</p>"
        text = extract_text_from_html(html)

        keypair = Ed25519PrivateKey.generate()
        signing_key = derive_signing_key_from_private_key(keypair)

        # Sign each line
        lines = text.split("\n")
        signed_lines = []
        for line in lines:
            if not line.strip():
                signed_lines.append(line)
                continue
            sig = create_minimal_signed_uuid(uuid_mod.uuid4(), signing_key)
            signed_lines.append(embed_signature_safely(line, sig))
        signed_text = "\n".join(signed_lines)

        result_html = embed_signed_text_in_html(html, signed_text)

        # Extract text from the signed HTML and check markers are present
        found = find_all_minimal_signed_uuids(result_html)
        assert len(found) >= 2, f"Expected >=2 markers in signed HTML, found {len(found)}"

    def test_chesschampion_roundtrip_with_existing_signed_output(self, example_html):
        """Use the already-generated micro_c2pa signed text to produce signed HTML."""
        signed_path = (
            Path(__file__).resolve().parent / "e2e_live" / "output" / "chesschampion_micro_c2pa_signed.txt"
        )
        if not signed_path.exists():
            pytest.skip("Signed output not available (run live e2e tests first)")

        signed_text = signed_path.read_text(encoding="utf-8")
        result_html = embed_signed_text_in_html(example_html, signed_text)

        # HTML structure preserved
        assert "<h1" in result_html
        assert "<h2" in result_html
        assert "<p>" in result_html or "<p " in result_html
        assert "<img " in result_html
        assert "<ol" in result_html

        # Content preserved
        assert "Garry Kasparov" in result_html
        assert "Deep Blue" in result_html
        assert "Magnus Carlsen" in result_html

        # Signed HTML should be longer than original (has invisible markers)
        assert len(result_html) > len(example_html), (
            f"Signed HTML ({len(result_html)}) should be longer than original ({len(example_html)})"
        )

        # Markers should be extractable from the HTML
        from app.utils.vs256_crypto import find_all_minimal_signed_uuids

        found = find_all_minimal_signed_uuids(result_html)
        assert len(found) > 10, f"Expected many markers in signed HTML, found {len(found)}"

    def test_empty_html_passthrough(self):
        assert embed_signed_text_in_html("", "signed") == ""
        assert embed_signed_text_in_html("  ", "signed") == "  "

    def test_empty_signed_text_passthrough(self):
        html = "<p>Hello</p>"
        assert embed_signed_text_in_html(html, "") == html


class TestExtractSegmentsFromHtml:
    def test_returns_list_of_segments(self, simple_html):
        segments = extract_segments_from_html(simple_html)
        assert isinstance(segments, list)
        assert len(segments) > 0
        for seg in segments:
            assert len(seg.strip()) > 0, f"Empty segment: {seg!r}"
            assert "<" not in seg, f"HTML tag in segment: {seg!r}"

    def test_chesschampion_produces_many_segments(self, example_html):
        segments = extract_segments_from_html(example_html)
        assert len(segments) >= 20, f"Expected >=20 segments, got {len(segments)}"

    def test_empty_html_returns_empty_list(self):
        assert extract_segments_from_html("") == []
        assert extract_segments_from_html("   ") == []
