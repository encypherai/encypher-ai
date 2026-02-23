"""
Evidence PDF Service.

Generates an Encypher-branded, court-presentable PDF from a JSON evidence
package returned by generate_evidence_package(). The PDF contains:
  Page 1  - Cover + notice details
  Page 2  - Notice text + cryptographic hash
  Page 3+ - Evidence chain table

Returns raw bytes (application/pdf) so the router can stream directly.
"""

import io
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Encypher brand colours ────────────────────────────────────────────────────
DELFT_BLUE = (0.106, 0.169, 0.306)       # #1B2B4E
BLUE_NCS = (0.165, 0.529, 0.769)         # #2A87C4
COLUMBIA_BLUE = (0.659, 0.835, 0.961)    # #A8D5F5
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
LIGHT_GREY = (0.93, 0.93, 0.93)
MID_GREY = (0.45, 0.45, 0.45)
GREEN = (0.13, 0.55, 0.13)
RED = (0.75, 0.15, 0.15)

# ── Asset path ────────────────────────────────────────────────────────────────
_ASSETS_DIR = Path(__file__).parent.parent / "assets"
_LOGO_PATH = _ASSETS_DIR / "logo_white.png"


def generate_evidence_pdf(
    evidence_package: Dict[str, Any],
    org_name: Optional[str] = None,
) -> bytes:
    """
    Generate Encypher-branded PDF from an evidence package dict.

    Args:
        evidence_package: Dict returned by rights_service.generate_evidence_package().
        org_name: Human-readable org name for the header. Falls back to org_id.

    Returns:
        PDF bytes.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        Image,
        NextPageTemplate,
        PageBreak,
        PageTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.flowables import HRFlowable

    buf = io.BytesIO()
    PAGE_W, PAGE_H = LETTER  # 612 x 792 pts
    MARGIN = 0.75 * inch
    HEADER_H = 0.85 * inch
    FOOTER_H = 0.35 * inch
    BODY_W = PAGE_W - 2 * MARGIN

    generation_ts = evidence_package.get("generated_at", "")
    notice_id = evidence_package.get("notice_id", "")

    # ── Header / Footer callbacks ─────────────────────────────────────────────

    def _draw_header(canvas, doc):
        canvas.saveState()
        # Dark header band
        canvas.setFillColorRGB(*DELFT_BLUE)
        canvas.rect(0, PAGE_H - HEADER_H, PAGE_W, HEADER_H, fill=1, stroke=0)

        # Logo (white PNG) — falls back to text wordmark
        logo_x = MARGIN
        logo_y = PAGE_H - HEADER_H + 0.18 * inch
        logo_h = 0.42 * inch
        if _LOGO_PATH.exists():
            try:
                canvas.drawImage(
                    str(_LOGO_PATH),
                    logo_x,
                    logo_y,
                    height=logo_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                _draw_text_wordmark(canvas, logo_x, logo_y + 0.05 * inch)
        else:
            _draw_text_wordmark(canvas, logo_x, logo_y + 0.05 * inch)

        # "Evidence Package" right-aligned
        canvas.setFillColorRGB(*WHITE)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.38 * inch, "Evidence Package")

        # Sub-line: notice ID + timestamp
        canvas.setFont("Helvetica", 7)
        sub = f"Notice {notice_id}  |  Generated {generation_ts}"
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.58 * inch, sub)
        canvas.restoreState()

    def _draw_text_wordmark(canvas, x, y):
        canvas.setFillColorRGB(*WHITE)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(x, y, "ENCYPHER")

    def _draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColorRGB(*MID_GREY)
        canvas.setFont("Helvetica", 7)
        page_str = f"Page {doc.page}"
        canvas.drawString(MARGIN, FOOTER_H, page_str)
        canvas.drawCentredString(PAGE_W / 2, FOOTER_H, "Encypher Evidence Package")
        canvas.drawRightString(PAGE_W - MARGIN, FOOTER_H, generation_ts)
        # thin rule above footer
        canvas.setStrokeColorRGB(*COLUMBIA_BLUE)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, FOOTER_H + 10, PAGE_W - MARGIN, FOOTER_H + 10)
        canvas.restoreState()

    def _on_page(canvas, doc):
        _draw_header(canvas, doc)
        _draw_footer(canvas, doc)

    # ── Doc + Page templates ──────────────────────────────────────────────────
    body_top = PAGE_H - HEADER_H - MARGIN * 0.4
    body_bot = FOOTER_H + MARGIN * 0.5
    frame = Frame(
        MARGIN,
        body_bot,
        BODY_W,
        body_top - body_bot,
        leftPadding=0,
        rightPadding=0,
        topPadding=4,
        bottomPadding=4,
        id="body",
    )
    page_tmpl = PageTemplate(id="main", frames=[frame], onPage=_on_page)
    doc = BaseDocTemplate(
        buf,
        pagesize=LETTER,
        pageTemplates=[page_tmpl],
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_H + MARGIN * 0.4,
        bottomMargin=FOOTER_H + MARGIN * 0.5,
        title=f"Encypher Evidence Package — {notice_id}",
        author="Encypher",
    )

    # ── Styles ────────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()

    def _s(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=styles[parent], **kw)

    h1 = _s("H1", fontSize=16, textColor=colors.HexColor("#1B2B4E"), spaceAfter=6, fontName="Helvetica-Bold")
    h2 = _s("H2", fontSize=11, textColor=colors.HexColor("#1B2B4E"), spaceBefore=12, spaceAfter=4, fontName="Helvetica-Bold")
    body_style = _s("Body", fontSize=9, spaceAfter=3, leading=13)
    label_style = _s("Label", fontSize=8, textColor=colors.HexColor("#444444"), spaceAfter=1, fontName="Helvetica-Bold")
    value_style = _s("Value", fontSize=9, spaceAfter=6)
    mono_style = _s("Mono", fontSize=8, fontName="Courier", leading=12, wordWrap="CJK")
    legal_style = _s(
        "Legal",
        fontSize=8,
        textColor=colors.HexColor("#555555"),
        leading=11,
        spaceAfter=10,
    )

    # ── Story ─────────────────────────────────────────────────────────────────
    story: List[Any] = []

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 1 — Cover + Notice Details
    # ─────────────────────────────────────────────────────────────────────────
    story.append(Paragraph("Formal Notice Evidence Package", h1))
    story.append(HRFlowable(width=BODY_W, color=colors.HexColor("#2A87C4"), thickness=1.5, spaceAfter=8))

    # Legal preamble
    story.append(
        Paragraph(
            "This document was generated by Encypher's automated evidence management system. "
            "The cryptographic hashes included herein are independently verifiable and reflect "
            "the state of the formal notice record at the time of generation. "
            "This package is suitable for attachment to legal correspondence or submission to "
            "media law clinics and counsel.",
            legal_style,
        )
    )

    # ── Section: Issuing Organization ────────────────────────────────────────
    story.append(Paragraph("Issuing Organization", h2))
    issuer_rows = [
        ["Organization", org_name or evidence_package.get("organization_id", "")],
        ["Notice ID", notice_id],
        ["Status", (evidence_package.get("notice", {}) or {}).get("status", "").upper()],
        ["Generated At", generation_ts],
    ]
    story.append(_kv_table(issuer_rows, BODY_W))

    # ── Section: Recipient ───────────────────────────────────────────────────
    notice = evidence_package.get("notice") or {}
    story.append(Paragraph("Recipient", h2))
    recipient_rows = [
        ["Entity Name", notice.get("target_entity_name", "")],
        ["Domain", notice.get("target_entity_domain", "")],
        ["Contact Email", notice.get("target_contact_email", "")],
        ["Entity Type", notice.get("target_entity_type", "")],
    ]
    story.append(_kv_table(recipient_rows, BODY_W))

    # ── Section: Scope of Violation ──────────────────────────────────────────
    story.append(Paragraph("Scope of Violation", h2))
    scope_rows = [
        ["Scope Type", notice.get("scope_type", "")],
        ["Date Range", _date_range(notice)],
        ["Document Count", str(len(notice.get("scope_document_ids") or []) or "All content")],
    ]
    story.append(_kv_table(scope_rows, BODY_W))

    # ── Section: Notice Details ──────────────────────────────────────────────
    story.append(Paragraph("Notice Details", h2))
    detail_rows = [
        ["Notice Type", notice.get("notice_type", "")],
        ["Created At", notice.get("created_at", "")],
        ["Delivered At", notice.get("delivered_at", "")],
        ["Delivery Method", notice.get("delivery_method", "")],
    ]
    story.append(_kv_table(detail_rows, BODY_W))

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 2 — Notice Text + Cryptographic Hash
    # ─────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Notice Text", h2))

    notice_text = notice.get("notice_text") or ""
    # Render in a bordered box
    text_lines = notice_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text_para = Paragraph(text_lines.replace("\n", "<br/>"), mono_style)
    text_table = Table(
        [[text_para]],
        colWidths=[BODY_W - 12],
        style=TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#A8D5F5")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5FAFF")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]),
    )
    story.append(text_table)
    story.append(Spacer(1, 12))

    # ── Cryptographic Integrity section ──────────────────────────────────────
    story.append(Paragraph("Cryptographic Integrity", h2))
    notice_hash = evidence_package.get("notice_hash") or notice.get("notice_hash") or ""
    story.append(Paragraph("Notice Hash (SHA-256)", label_style))
    story.append(Paragraph(notice_hash, mono_style))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "To verify: SHA-256(notice_text) must equal the hash above.",
            legal_style,
        )
    )

    hash_verified = evidence_package.get("notice_hash_verified", False)
    status_color = GREEN if hash_verified else RED
    status_text = "VERIFIED" if hash_verified else "UNVERIFIED"
    story.append(
        Paragraph(
            f'Hash status: <font color="{"#219121" if hash_verified else "#BF2626"}"><b>{status_text}</b></font>',
            body_style,
        )
    )

    # Package hash
    pkg_hash = evidence_package.get("package_hash", "")
    if pkg_hash:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Package Hash (SHA-256 of entire package)", label_style))
        story.append(Paragraph(pkg_hash, mono_style))

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 3+ — Evidence Chain
    # ─────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    chain = evidence_package.get("evidence_chain") or []
    story.append(Paragraph(f"Evidence Chain ({len(chain)} events)", h2))

    chain_verified = evidence_package.get("chain_integrity_verified", False)
    chain_status_color = "#219121" if chain_verified else "#BF2626"
    chain_status_text = "VERIFIED" if chain_verified else "UNVERIFIED"
    story.append(
        Paragraph(
            f'Chain integrity: <font color="{chain_status_color}"><b>{chain_status_text}</b></font>',
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    if chain:
        col_widths = [
            0.30 * inch,   # #
            1.35 * inch,   # Event Type
            1.55 * inch,   # Timestamp
            1.80 * inch,   # Event Hash
            1.80 * inch,   # Prev Hash
        ]
        header_row = [
            Paragraph("<b>#</b>", mono_style),
            Paragraph("<b>Event Type</b>", mono_style),
            Paragraph("<b>Timestamp</b>", mono_style),
            Paragraph("<b>Event Hash</b>", mono_style),
            Paragraph("<b>Prev Hash</b>", mono_style),
        ]
        data_rows = [header_row]
        for idx, event in enumerate(chain):
            evt_hash = event.get("event_hash") or ""
            prev_hash = event.get("previous_hash") or ""
            ts = event.get("created_at") or event.get("timestamp") or ""
            data_rows.append([
                Paragraph(str(idx + 1), mono_style),
                Paragraph(event.get("event_type", ""), mono_style),
                Paragraph(ts, mono_style),
                Paragraph(_truncate_hash(evt_hash), mono_style),
                Paragraph(_truncate_hash(prev_hash), mono_style),
            ])

        chain_table = Table(
            data_rows,
            colWidths=col_widths,
            repeatRows=1,
        )
        chain_table.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2B4E")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            # Alternating rows
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F6FC")]),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#2A87C4")),
            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(chain_table)
    else:
        story.append(Paragraph("No evidence chain events recorded.", body_style))

    # ── Build PDF ─────────────────────────────────────────────────────────────
    doc.build(story)
    return buf.getvalue()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _kv_table(rows: List[List[str]], body_w: float) -> Any:
    """Render a two-column label/value table."""
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Table, TableStyle

    label_style = ParagraphStyle(
        "kv_label",
        fontSize=8,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#444444"),
    )
    value_style = ParagraphStyle(
        "kv_value",
        fontSize=9,
        fontName="Helvetica",
    )

    data = [
        [Paragraph(r[0], label_style), Paragraph(str(r[1]) if r[1] else "-", value_style)]
        for r in rows
    ]
    t = Table(data, colWidths=[1.5 * 72, body_w - 1.5 * 72])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    return t


def _truncate_hash(h: str, length: int = 16) -> str:
    if not h:
        return "-"
    if len(h) <= length:
        return h
    return h[:length] + "..."


def _date_range(notice: Dict[str, Any]) -> str:
    start = notice.get("scope_start_date") or ""
    end = notice.get("scope_end_date") or ""
    if start and end:
        return f"{start} to {end}"
    if start:
        return f"From {start}"
    if end:
        return f"Until {end}"
    return "All dates"
