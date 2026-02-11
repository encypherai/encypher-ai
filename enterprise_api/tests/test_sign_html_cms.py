"""
Unit tests for the sign_html_cms.py script functions (TEAM_169).

Tests the core functions: _collect_text_nodes, _extract_text_from_element,
_embed_signed_text_in_element, and sign_html content-selector logic.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

from scripts.sign_html_cms import (
    _collect_text_nodes,
    _embed_signed_text_in_element,
    _extract_text_from_element,
)

COMPLEX_HTML_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "chesschampion"
    / "example_article_complex_parsing.html"
)


@pytest.fixture
def complex_html() -> str:
    assert COMPLEX_HTML_PATH.exists(), f"Complex HTML not found: {COMPLEX_HTML_PATH}"
    return COMPLEX_HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture
def complex_soup(complex_html: str) -> BeautifulSoup:
    return BeautifulSoup(complex_html, "html.parser")


class TestCollectTextNodes:
    def test_collects_from_article_only(self, complex_soup: BeautifulSoup):
        article = complex_soup.find("article")
        assert article is not None
        nodes = _collect_text_nodes(article)
        assert len(nodes) > 0
        # All nodes should have non-empty normalized text
        for _, text in nodes:
            assert len(text.strip()) > 0

    def test_article_has_fewer_nodes_than_full_page(self, complex_soup: BeautifulSoup):
        all_nodes = _collect_text_nodes(complex_soup)
        article = complex_soup.find("article")
        article_nodes = _collect_text_nodes(article)
        assert len(article_nodes) < len(all_nodes), (
            "Article should have fewer text nodes than the full page"
        )

    def test_skips_script_and_style(self, complex_soup: BeautifulSoup):
        article = complex_soup.find("article")
        nodes = _collect_text_nodes(article)
        for _, text in nodes:
            assert "charset" not in text.lower(), f"Style content leaked: {text[:60]}"
            assert "function" not in text.lower() or "function" in text.lower() and "chess" in text.lower(), (
                f"Script content may have leaked: {text[:60]}"
            )


class TestExtractTextFromElement:
    def test_article_text_has_chess_content(self, complex_soup: BeautifulSoup):
        article = complex_soup.find("article")
        text = _extract_text_from_element(article)
        assert "Garry Kasparov" in text
        assert "Deep Blue" in text
        assert "Bobby Fischer" in text

    def test_article_text_excludes_nav(self, complex_soup: BeautifulSoup):
        article = complex_soup.find("article")
        text = _extract_text_from_element(article)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # Nav items like standalone "Learn", "Play", "Strategy" should not appear
        assert "Learn" not in lines, "Nav item 'Learn' should not be in article text"
        assert "Play" not in lines, "Nav item 'Play' should not be in article text"

    def test_full_page_text_includes_footer(self, complex_soup: BeautifulSoup):
        body = complex_soup.find("body")
        text = _extract_text_from_element(body)
        assert "Terms of Service" in text

    def test_article_text_excludes_footer(self, complex_soup: BeautifulSoup):
        article = complex_soup.find("article")
        text = _extract_text_from_element(article)
        assert "Terms of Service" not in text


class TestEmbedSignedTextInElement:
    def test_simple_embed(self):
        """Embed signed text into a simple HTML element."""
        from app.utils.vs256_crypto import (
            VS_CHAR_SET,
            create_minimal_signed_uuid,
            derive_signing_key_from_private_key,
            embed_signature_safely,
        )
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import uuid as uuid_mod

        html = "<article><h1>Title</h1><p>Hello world.</p></article>"
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article")

        text = _extract_text_from_element(article)
        keypair = Ed25519PrivateKey.generate()
        signing_key = derive_signing_key_from_private_key(keypair)

        lines = text.split("\n")
        signed_lines = []
        for line in lines:
            if not line.strip():
                signed_lines.append(line)
                continue
            sig = create_minimal_signed_uuid(uuid_mod.uuid4(), signing_key)
            signed_lines.append(embed_signature_safely(line, sig))
        signed_text = "\n".join(signed_lines)

        vs_chars = set(VS_CHAR_SET)
        matched = _embed_signed_text_in_element(article, signed_text, vs_chars)
        assert matched >= 2, f"Expected >=2 matches, got {matched}"

        result = str(soup)
        assert "<article>" in result
        assert "<h1>" in result
        assert "Title" in result

    def test_complex_html_preserves_structure(self, complex_soup: BeautifulSoup):
        """Embedding into complex HTML preserves page structure."""
        signed_path = (
            Path(__file__).resolve().parent
            / "e2e_live"
            / "output"
            / "chesschampion_complex_micro_c2pa_signed.html"
        )
        if not signed_path.exists():
            pytest.skip("Complex signed output not available (run script first)")

        signed_html = signed_path.read_text(encoding="utf-8")
        signed_soup = BeautifulSoup(signed_html, "html.parser")

        # Full page structure preserved
        assert signed_soup.find("head") is not None
        assert signed_soup.find("body") is not None
        assert signed_soup.find("header") is not None
        assert signed_soup.find("footer") is not None
        assert signed_soup.find("article") is not None
        assert signed_soup.find("nav") is not None

        # Meta tags preserved
        assert signed_soup.find("meta", attrs={"name": "Description"}) is not None
        assert signed_soup.find("title") is not None

        # Images preserved
        imgs = signed_soup.find_all("img")
        assert len(imgs) > 5, f"Expected many images, found {len(imgs)}"

        # Scripts preserved
        scripts = signed_soup.find_all("script")
        assert len(scripts) > 0

        # Styles preserved
        styles = signed_soup.find_all("style")
        assert len(styles) > 0

    def test_complex_html_has_markers(self):
        """Signed complex HTML should contain VS256 markers."""
        signed_path = (
            Path(__file__).resolve().parent
            / "e2e_live"
            / "output"
            / "chesschampion_complex_micro_c2pa_signed.html"
        )
        if not signed_path.exists():
            pytest.skip("Complex signed output not available (run script first)")

        from app.utils.vs256_crypto import find_all_minimal_signed_uuids

        signed_html = signed_path.read_text(encoding="utf-8")
        found = find_all_minimal_signed_uuids(signed_html)
        assert len(found) > 10, f"Expected many markers, found {len(found)}"

    def test_complex_html_longer_than_original(self, complex_html: str):
        """Signed HTML should be longer than original due to invisible markers."""
        signed_path = (
            Path(__file__).resolve().parent
            / "e2e_live"
            / "output"
            / "chesschampion_complex_micro_c2pa_signed.html"
        )
        if not signed_path.exists():
            pytest.skip("Complex signed output not available (run script first)")

        signed_html = signed_path.read_text(encoding="utf-8")
        assert len(signed_html) > len(complex_html), (
            f"Signed ({len(signed_html)}) should be longer than original ({len(complex_html)})"
        )
