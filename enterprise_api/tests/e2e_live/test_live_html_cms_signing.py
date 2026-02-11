"""
Live e2e tests for HTML CMS content signing (TEAM_169).

Pipeline:
1. Extract rendered text from chesschampion example_article.html
2. Sign via live production API with micro_c2pa and micro_ecc_c2pa
3. Verify via live production API
4. Write signed text to files for manual copy-paste into encypherai.com/tools/verify

Run with:
    LIVE_API_TESTS=true uv run pytest tests/e2e_live/test_live_html_cms_signing.py -v -s
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app.utils.html_text_extractor import (
    embed_signed_text_in_html,
    extract_segments_from_html,
    extract_text_from_html,
)

EXAMPLE_HTML_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "examples"
    / "chesschampion"
    / "example_article.html"
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def _unique_document_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _assert_status(response, expected_status: int, label: str) -> None:
    assert response.status_code == expected_status, (
        f"{label} expected {expected_status}, got {response.status_code}. "
        f"Body: {response.text[:2000]}"
    )


@pytest.fixture(scope="module")
def example_html() -> str:
    assert EXAMPLE_HTML_PATH.exists(), f"Example HTML not found: {EXAMPLE_HTML_PATH}"
    return EXAMPLE_HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def extracted_text(example_html: str) -> str:
    text = extract_text_from_html(example_html)
    assert len(text) > 5000, f"Extracted text too short: {len(text)} chars"
    return text


@pytest.fixture(scope="module")
def extracted_segments(example_html: str) -> list[str]:
    segments = extract_segments_from_html(example_html)
    assert len(segments) >= 20, f"Expected >=20 segments, got {len(segments)}"
    return segments


def _write_output(filename: str, content: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


# ===========================================================================
# HTML extraction sanity checks (run even without live API)
# ===========================================================================


class TestHtmlExtractionForCms:
    def test_extraction_produces_clean_text(self, extracted_text):
        assert "<h1" not in extracted_text
        assert "<p>" not in extracted_text
        assert "<img" not in extracted_text
        assert "Garry Kasparov" in extracted_text
        assert "Deep Blue" in extracted_text

    def test_extraction_produces_segments(self, extracted_segments):
        assert len(extracted_segments) >= 20
        for seg in extracted_segments:
            assert "<" not in seg, f"HTML tag in segment: {seg[:80]!r}"


# ===========================================================================
# Live API: sign with micro_c2pa, verify, output for manual paste
# ===========================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_html_sign_micro_c2pa(
    live_client,
    live_auth_headers,
    live_api_config,
    extracted_text,
) -> None:
    """Sign chesschampion HTML text with micro_c2pa via live unified /sign, verify, write output."""
    assert live_api_config.base_url.startswith("https://api.encypherai.com")

    document_id = _unique_document_id("html_micro_c2pa")

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json={
            "document_id": document_id,
            "text": extracted_text,
            "document_title": "Best Chess Games of All Time",
            "options": {
                "document_type": "article",
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
            },
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign (micro_c2pa)")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True

    data = sign_payload["data"]
    document = data["document"]
    assert document["document_id"] == document_id
    signed_text = document["signed_text"]
    assert isinstance(signed_text, str), "Expected signed_text in data.document"
    assert len(signed_text) > len(extracted_text), "Signed text should be longer (has markers)"

    # Write signed text for manual copy-paste into encypherai.com/tools/verify
    out_path = _write_output("chesschampion_micro_c2pa_signed.txt", signed_text)
    print(f"\n>>> micro_c2pa signed text written to: {out_path}")
    print(f">>> Document ID: {document_id}")
    print(f">>> Signed text length: {len(signed_text)} chars")

    # Verify via live API
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": signed_text},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify (micro_c2pa)")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        f"micro_c2pa verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Details: {verify_payload['data'].get('details')}. "
        f"Full: {verify_payload}"
    )

    print(">>> micro_c2pa API verification: PASSED")
    print(f">>> Copy the contents of {out_path} and paste into https://encypherai.com/tools/verify")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_html_sign_micro_ecc_c2pa(
    live_client,
    live_auth_headers,
    live_api_config,
    extracted_text,
) -> None:
    """Sign chesschampion HTML text with micro_ecc_c2pa via live unified /sign, verify, write output."""
    assert live_api_config.base_url.startswith("https://api.encypherai.com")

    document_id = _unique_document_id("html_micro_ecc_c2pa")

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json={
            "document_id": document_id,
            "text": extracted_text,
            "document_title": "Best Chess Games of All Time",
            "options": {
                "document_type": "article",
                "manifest_mode": "micro_ecc_c2pa",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
            },
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign (micro_ecc_c2pa)")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True

    data = sign_payload["data"]
    document = data["document"]
    assert document["document_id"] == document_id
    signed_text = document["signed_text"]
    assert isinstance(signed_text, str), "Expected signed_text in data.document"
    assert len(signed_text) > len(extracted_text), "Signed text should be longer (has RS markers)"

    # Write signed text for manual copy-paste
    out_path = _write_output("chesschampion_micro_ecc_c2pa_signed.txt", signed_text)
    print(f"\n>>> micro_ecc_c2pa signed text written to: {out_path}")
    print(f">>> Document ID: {document_id}")
    print(f">>> Signed text length: {len(signed_text)} chars")

    # Verify via live API
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": signed_text},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify (micro_ecc_c2pa)")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        f"micro_ecc_c2pa verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Details: {verify_payload['data'].get('details')}. "
        f"Full: {verify_payload}"
    )

    print(">>> micro_ecc_c2pa API verification: PASSED")
    print(f">>> Copy the contents of {out_path} and paste into https://encypherai.com/tools/verify")


# ===========================================================================
# Live API: also sign with basic /sign endpoint for comparison
# ===========================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_html_sign_basic(
    live_client,
    live_auth_headers,
    live_api_config,
    extracted_text,
) -> None:
    """Sign chesschampion HTML text with basic /sign (default options) for comparison."""
    assert live_api_config.base_url.startswith("https://api.encypherai.com")

    document_id = _unique_document_id("html_basic")

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json={
            "document_id": document_id,
            "text": extracted_text,
            "document_title": "Best Chess Games of All Time",
            "options": {
                "document_type": "article",
            },
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign (basic)")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True

    data = sign_payload["data"]
    document = data["document"]
    assert document["document_id"] == document_id
    signed_text = document["signed_text"]
    assert isinstance(signed_text, str)

    out_path = _write_output("chesschampion_basic_signed.txt", signed_text)
    print(f"\n>>> Basic signed text written to: {out_path}")
    print(f">>> Document ID: {document_id}")

    # Verify
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": signed_text},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify (basic)")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        f"Basic verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Full: {verify_payload}"
    )

    print(">>> Basic API verification: PASSED")


# ===========================================================================
# Live API: sign text, embed back into HTML, output .html files
# ===========================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_html_inplace_micro_c2pa(
    live_client,
    live_auth_headers,
    live_api_config,
    example_html,
    extracted_text,
) -> None:
    """Sign text via API with micro_c2pa, embed back into HTML, output .html file."""
    assert live_api_config.base_url.startswith("https://api.encypherai.com")

    document_id = _unique_document_id("html_inplace_micro_c2pa")

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json={
            "document_id": document_id,
            "text": extracted_text,
            "document_title": "Best Chess Games of All Time",
            "options": {
                "document_type": "article",
                "manifest_mode": "micro_c2pa",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
            },
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign (micro_c2pa inplace)")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True
    signed_text = sign_payload["data"]["document"]["signed_text"]

    # Embed signed text back into original HTML
    signed_html = embed_signed_text_in_html(example_html, signed_text)

    # HTML structure must be preserved
    assert "<h1" in signed_html
    assert "<h2" in signed_html
    assert "<img " in signed_html
    assert "<ol" in signed_html
    assert len(signed_html) > len(example_html)

    out_path = _write_output("chesschampion_micro_c2pa_signed.html", signed_html)
    print(f"\n>>> micro_c2pa signed HTML written to: {out_path}")
    print(f">>> Original HTML: {len(example_html)} chars")
    print(f">>> Signed HTML:   {len(signed_html)} chars")
    print(">>> Open in browser, select-all, copy, paste into https://encypherai.com/tools/verify")

    # Verify: extract text from signed HTML, send to verify API
    text_from_signed_html = extract_text_from_html(signed_html)
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": text_from_signed_html},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify (micro_c2pa inplace)")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        f"micro_c2pa inplace verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Full: {verify_payload}"
    )
    print(">>> micro_c2pa inplace HTML verification: PASSED")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_live_html_inplace_micro_ecc_c2pa(
    live_client,
    live_auth_headers,
    live_api_config,
    example_html,
    extracted_text,
) -> None:
    """Sign text via API with micro_ecc_c2pa, embed back into HTML, output .html file."""
    assert live_api_config.base_url.startswith("https://api.encypherai.com")

    document_id = _unique_document_id("html_inplace_micro_ecc")

    sign_response = await live_client.post(
        "/api/v1/sign",
        headers=live_auth_headers,
        json={
            "document_id": document_id,
            "text": extracted_text,
            "document_title": "Best Chess Games of All Time",
            "options": {
                "document_type": "article",
                "manifest_mode": "micro_ecc_c2pa",
                "segmentation_level": "sentence",
                "segmentation_levels": ["sentence", "paragraph"],
                "embedding_strategy": "single_point",
                "index_for_attribution": True,
            },
        },
    )

    _assert_status(sign_response, 201, "POST /api/v1/sign (micro_ecc_c2pa inplace)")
    sign_payload = sign_response.json()
    assert sign_payload["success"] is True
    signed_text = sign_payload["data"]["document"]["signed_text"]

    # Embed signed text back into original HTML
    signed_html = embed_signed_text_in_html(example_html, signed_text)

    assert "<h1" in signed_html
    assert "<img " in signed_html
    assert len(signed_html) > len(example_html)

    out_path = _write_output("chesschampion_micro_ecc_c2pa_signed.html", signed_html)
    print(f"\n>>> micro_ecc_c2pa signed HTML written to: {out_path}")
    print(f">>> Original HTML: {len(example_html)} chars")
    print(f">>> Signed HTML:   {len(signed_html)} chars")

    # Verify
    text_from_signed_html = extract_text_from_html(signed_html)
    verify_response = await live_client.post(
        "/api/v1/verify",
        headers=live_auth_headers,
        json={"text": text_from_signed_html},
    )

    _assert_status(verify_response, 200, "POST /api/v1/verify (micro_ecc_c2pa inplace)")
    verify_payload = verify_response.json()
    assert verify_payload["success"] is True
    assert verify_payload["data"]["valid"] is True, (
        f"micro_ecc_c2pa inplace verification failed. "
        f"Reason: {verify_payload['data'].get('reason_code')}. "
        f"Full: {verify_payload}"
    )
    print(">>> micro_ecc_c2pa inplace HTML verification: PASSED")
