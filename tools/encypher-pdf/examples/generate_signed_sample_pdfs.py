from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from encypher_pdf.extractor import extract_signed_text
from encypher_pdf.writer import Alignment, Document, TextStyle

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"
REPORTS_DIR = OUT_DIR / "reports"
MARKETING_SITE_BASE_URL = "http://localhost:3000"
VERIFY_API_URL = "http://localhost:8000/api/v1/verify"


@dataclass
class SignedPayload:
    original_text: str
    signed_text: str
    metadata: dict[str, Any] | None


def _post_json(url: str, payload: dict[str, Any], *, timeout: int = 60) -> dict[str, Any]:
    raw = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def sign_text_locally(original_text: str, provenance: str) -> SignedPayload:
    data = _post_json(
        f"{MARKETING_SITE_BASE_URL}/api/tools/sign",
        {
            "original_text": original_text,
            "metadata_format": "c2pa_v2_2",
            "ai_info": {"provenance": provenance},
        },
    )
    signed_text = data.get("encoded_text")
    if not isinstance(signed_text, str) or not signed_text:
        raise RuntimeError("Local signing route returned no encoded_text")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else None
    return SignedPayload(original_text=original_text, signed_text=signed_text, metadata=metadata)


def build_signed_editorial_pdf(font_family: str, filename: str, provenance: str) -> tuple[Path, SignedPayload]:
    original_text = (
        "A Visually Normal Signed Editorial PDF\n\n"
        "Generated through the local Encypher marketing-site signing workflow.\n\n"
        "This sample is intended to look like a normal document exported from a word processor while also carrying a real Encypher signature that can be verified by the local marketing-site verification tool and the raw verify API.\n\n"
        "Headings, paragraph spacing, readable typography, and conventional margins are preserved. Invisible characters are embedded by the signing workflow so copy-pasted text can be validated without changing the visible reading experience.\n\n"
        "The phrase Hello World and the sequence A B appear visually ordinary, but the signed text returned by the local workflow contains the embedded provenance payload needed for verification."
    )

    signed = sign_text_locally(original_text, provenance)

    title_style = TextStyle(
        font_size=18,
        font_family=font_family,
        line_height=1.2,
        alignment=Alignment.CENTER,
        bold=True,
        space_after=6,
    )
    subtitle_style = TextStyle(
        font_size=11,
        font_family=font_family,
        line_height=1.3,
        alignment=Alignment.CENTER,
        space_after=10,
    )
    heading_style = TextStyle(
        font_size=13,
        font_family=font_family,
        line_height=1.2,
        bold=True,
        space_before=14,
        space_after=6,
    )
    body_style = TextStyle(
        font_size=11,
        font_family=font_family,
        line_height=1.45,
        alignment=Alignment.JUSTIFY,
        space_after=8,
        first_line_indent=22,
    )

    doc = Document(footer_text="Signed sample via local workflow")
    doc.add_text("A Visually Normal Signed Editorial PDF", title_style)
    doc.add_text("Generated through the local Encypher marketing-site signing workflow.", subtitle_style)
    doc.add_text("1. Signed Content", heading_style)
    for chunk in signed.signed_text.split("\n\n"):
        if chunk.strip():
            doc.add_text(chunk, body_style)
    doc.set_signed_text(signed.signed_text)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / filename
    doc.save(str(output_path))
    return output_path, signed


def verify_with_marketing_site_text(signed_text: str) -> dict[str, Any]:
    return _post_json(f"{MARKETING_SITE_BASE_URL}/api/tools/verify", {"encoded_text": signed_text})


def verify_with_marketing_site_pdf(pdf_path: Path, fallback_text: str) -> dict[str, Any]:
    pdf_base64 = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    return _post_json(
        f"{MARKETING_SITE_BASE_URL}/api/tools/verify",
        {"encoded_text": fallback_text, "pdf_base64": pdf_base64},
    )


def verify_with_raw_api(signed_text: str) -> dict[str, Any]:
    return _post_json(VERIFY_API_URL, {"text": signed_text})


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    outputs: list[dict[str, Any]] = []
    for family, filename in [
        ("roboto", "sample_roboto_signed.pdf"),
        ("arial", "sample_arial_signed.pdf"),
        ("times", "sample_times_signed.pdf"),
    ]:
        pdf_path, signed = build_signed_editorial_pdf(
            family,
            filename,
            f"Signed sample PDF generated locally for {family}",
        )
        extracted_signed = extract_signed_text(pdf_path)
        if extracted_signed != signed.signed_text:
            raise RuntimeError(f"Signed text metadata mismatch for {pdf_path.name}")

        marketing_text = verify_with_marketing_site_text(signed.signed_text)
        marketing_pdf = verify_with_marketing_site_pdf(pdf_path, signed.signed_text)
        raw_verify = verify_with_raw_api(signed.signed_text)

        report = {
            "font_family": family,
            "pdf_path": str(pdf_path),
            "original_text": signed.original_text,
            "signed_text_length": len(signed.signed_text),
            "marketing_site_text_verify": marketing_text,
            "marketing_site_pdf_verify": marketing_pdf,
            "raw_verify_api": raw_verify,
            "metadata": signed.metadata,
        }
        report_path = REPORTS_DIR / f"{pdf_path.stem}.verification.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        outputs.append({"pdf": str(pdf_path), "report": str(report_path)})

    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
