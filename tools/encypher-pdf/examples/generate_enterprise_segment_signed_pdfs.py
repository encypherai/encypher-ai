from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from encypher_pdf.extractor import extract_signed_text
from encypher_pdf.writer import Alignment, Document, TextStyle

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
REPORTS_DIR = OUT_DIR / "reports"
ENTERPRISE_SIGN_URL = "http://localhost:8000/api/v1/sign"
VERIFY_API_URL = "http://localhost:8000/api/v1/verify"
MARKETING_SITE_VERIFY_URL = "http://localhost:3000/api/tools/verify"
DEFAULT_LOCAL_SIGN_KEY = "ency_marketing_site_prod_2026"


@dataclass(frozen=True)
class Variant:
    slug: str
    label: str
    options: dict[str, Any]


@dataclass
class SignResult:
    original_text: str
    signed_text: str
    api_signed_text: str
    embedding_plan: dict[str, Any] | None
    document_id: str | None
    verification_url: str | None
    response_document: dict[str, Any]
    raw_response: dict[str, Any]


def _post_json(url: str, payload: dict[str, Any], *, headers: dict[str, str] | None = None, timeout: int = 90) -> dict[str, Any]:
    raw = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def _resolve_sign_api_key() -> str:
    return os.getenv("ENTERPRISE_API_KEY") or os.getenv("ENCYPHER_API_KEY") or DEFAULT_LOCAL_SIGN_KEY


def apply_embedding_plan(visible_text: str, embedding_plan: dict[str, Any]) -> str:
    chars = list(visible_text)
    operations = sorted(
        embedding_plan.get("operations", []),
        key=lambda op: int(op.get("insert_after_index", -1)),
        reverse=True,
    )
    for op in operations:
        idx = int(op.get("insert_after_index", -1))
        marker = str(op.get("marker", ""))
        if idx < -1:
            raise RuntimeError("insert_after_index must be >= -1")
        insert_at = idx + 1
        chars[insert_at:insert_at] = list(marker)
    return "".join(chars)


def sign_with_enterprise_api(original_text: str, title: str, options: dict[str, Any]) -> SignResult:
    payload = {
        "document_title": title,
        "text": original_text,
        "options": options,
    }
    data = _post_json(
        ENTERPRISE_SIGN_URL,
        payload,
        headers={"Authorization": f"Bearer {_resolve_sign_api_key()}"},
    )
    document = (data.get("data") or {}).get("document") or {}
    api_signed_text = document.get("signed_text")
    if not isinstance(api_signed_text, str) or not api_signed_text:
        raise RuntimeError("Enterprise sign response missing data.document.signed_text")
    embedding_plan = document.get("embedding_plan") if isinstance(document.get("embedding_plan"), dict) else None
    signed_text = api_signed_text
    if embedding_plan and embedding_plan.get("operations"):
        reconstructed = apply_embedding_plan(original_text, embedding_plan)
        signed_text = reconstructed
    return SignResult(
        original_text=original_text,
        signed_text=signed_text,
        api_signed_text=api_signed_text,
        embedding_plan=embedding_plan,
        document_id=document.get("document_id") if isinstance(document.get("document_id"), str) else None,
        verification_url=document.get("verification_url") if isinstance(document.get("verification_url"), str) else None,
        response_document=document,
        raw_response=data,
    )


def verify_with_marketing_site_text(signed_text: str) -> dict[str, Any]:
    return _post_json(MARKETING_SITE_VERIFY_URL, {"encoded_text": signed_text})


def verify_with_marketing_site_pdf(pdf_path: Path, fallback_text: str) -> dict[str, Any]:
    pdf_base64 = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    return _post_json(
        MARKETING_SITE_VERIFY_URL,
        {"encoded_text": fallback_text, "pdf_base64": pdf_base64},
    )


def verify_with_raw_api(signed_text: str) -> dict[str, Any]:
    return _post_json(VERIFY_API_URL, {"text": signed_text})


def build_pdf(variant: Variant, sign_result: SignResult, output_path: Path) -> None:
    title_style = TextStyle(
        font_size=18,
        font_family="roboto",
        line_height=1.2,
        alignment=Alignment.CENTER,
        bold=True,
        space_after=6,
    )
    subtitle_style = TextStyle(
        font_size=11,
        font_family="roboto",
        line_height=1.3,
        alignment=Alignment.CENTER,
        space_after=10,
    )
    heading_style = TextStyle(
        font_size=13,
        font_family="roboto",
        line_height=1.2,
        bold=True,
        space_before=14,
        space_after=6,
    )
    body_style = TextStyle(
        font_size=11,
        font_family="roboto",
        line_height=1.45,
        alignment=Alignment.JUSTIFY,
        space_after=8,
        first_line_indent=22,
    )

    doc = Document(footer_text=variant.label)
    doc.add_text("Enterprise API Segment-Signed PDF", title_style)
    doc.add_text(variant.label, subtitle_style)
    doc.add_text("1. Signed Content", heading_style)
    for chunk in sign_result.signed_text.split("\n\n"):
        if chunk.strip():
            doc.add_text(chunk, body_style)
    doc.set_signed_text(sign_result.signed_text)
    doc.save(str(output_path))


def build_source_text() -> str:
    return (
        "This PDF is generated from the enterprise sign API using sentence-level signing. "
        "Each sentence should receive its own invisible marker plan before the PDF is rendered.\n\n"
        "We are testing micro mode and micro legacy-safe mode because Chrome, PDF viewers, "
        "and office tools do not all preserve the same invisible Unicode families. "
        "The PDF should still look like a normal editorial export.\n\n"
        "The verification pipeline must accept the signed output through the marketing-site tools, "
        "the raw verify API, and the PDF metadata extraction path. "
        "These fixtures are intended to exercise embed_c2pa true and false combinations."
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    base_options = {
        "document_type": "article",
        "segmentation_level": "sentence",
        "embedding_strategy": "single_point",
        "return_embedding_plan": True,
        "store_c2pa_manifest": True,
        "action": "c2pa.created",
    }

    variants = [
        Variant(
            slug="micro_vs256_rs_c2pa",
            label="micro · VS256-RS · embed_c2pa=true",
            options={**base_options, "manifest_mode": "micro", "ecc": True, "legacy_safe": False, "embed_c2pa": True},
        ),
        Variant(
            slug="micro_vs256_rs_markers_only",
            label="micro · VS256-RS · embed_c2pa=false",
            options={**base_options, "manifest_mode": "micro", "ecc": True, "legacy_safe": False, "embed_c2pa": False},
        ),
        Variant(
            slug="micro_legacy_safe_rs_c2pa",
            label="micro · legacy_safe_rs · embed_c2pa=true",
            options={**base_options, "manifest_mode": "micro", "ecc": True, "legacy_safe": True, "embed_c2pa": True},
        ),
        Variant(
            slug="micro_legacy_safe_rs_markers_only",
            label="micro · legacy_safe_rs · embed_c2pa=false",
            options={**base_options, "manifest_mode": "micro", "ecc": True, "legacy_safe": True, "embed_c2pa": False},
        ),
    ]

    original_text = build_source_text()
    outputs: list[dict[str, str]] = []

    for variant in variants:
        sign_result = sign_with_enterprise_api(original_text, variant.label, variant.options)
        pdf_path = OUT_DIR / f"{variant.slug}.pdf"
        build_pdf(variant, sign_result, pdf_path)

        extracted_signed = extract_signed_text(pdf_path)
        if extracted_signed != sign_result.signed_text:
            raise RuntimeError(f"Signed text metadata mismatch for {pdf_path.name}")

        marketing_text = verify_with_marketing_site_text(sign_result.signed_text)
        marketing_pdf = verify_with_marketing_site_pdf(pdf_path, sign_result.signed_text)
        raw_verify = verify_with_raw_api(sign_result.signed_text)

        report = {
            "label": variant.label,
            "slug": variant.slug,
            "pdf_path": str(pdf_path),
            "options": variant.options,
            "document_id": sign_result.document_id,
            "verification_url": sign_result.verification_url,
            "original_text": sign_result.original_text,
            "signed_text_length": len(sign_result.signed_text),
            "api_signed_text_length": len(sign_result.api_signed_text),
            "embedding_plan": sign_result.embedding_plan,
            "embedding_plan_operation_count": len((sign_result.embedding_plan or {}).get("operations", [])),
            "marketing_site_text_verify": marketing_text,
            "marketing_site_pdf_verify": marketing_pdf,
            "raw_verify_api": raw_verify,
            "response_document": sign_result.response_document,
        }
        report_path = REPORTS_DIR / f"{variant.slug}.verification.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        outputs.append({"pdf": str(pdf_path), "report": str(report_path)})

    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
