"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""
import json
import logging
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.request_models import VerifyRequest
from app.models.response_models import ErrorDetail, VerifyResponse
from app.services.verification_logic import (
    VerificationExecution,
    build_verdict,
    determine_reason_code,
    execute_verification,
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_VERIFY_BYTES = 2 * 1024 * 1024  # 2 MB


def _error_response(
    status_code: int,
    *,
    correlation_id: str,
    code: str,
    message: str,
    hint: Optional[str] = None,
) -> JSONResponse:
    """Build a structured error response envelope."""

    payload = VerifyResponse(
        success=False,
        data=None,
        error=ErrorDetail(code=code, message=message, hint=hint),
        correlation_id=correlation_id,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _render_manifest_json(execution: VerificationExecution) -> str:
    """Pretty-print manifest JSON for HTML responses."""

    try:
        return json.dumps(execution.manifest, indent=2) if execution.manifest else "{}"
    except TypeError:
        return "{}"


@router.get("/verify/{document_id}")
async def verify_by_document_id(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify a document by its ID (for clickable verification links).

    Returns an HTML page so users can preview verification state in a browser.
    """

    result = await db.execute(
        text("SELECT signed_text, title, organization_id FROM documents WHERE document_id = :doc_id"),
        {"doc_id": document_id},
    )
    row = result.fetchone()

    if not row:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Document Not Found</title></head>
                <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
                    <h1>Document Not Found in Database</h1>
                    <p><strong>Document ID:</strong> {document_id}</p>
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Demo Organization Note</h3>
                        <p>This document was signed using a demo API key. Demo documents are not stored in the database for verification.</p>
                        <p>To verify this document:</p>
                        <ol>
                            <li>Copy the signed text from the file</li>
                            <li>Use the POST <code>/api/v1/verify</code> endpoint with the signed text in the request body</li>
                            <li>Or use the Enterprise SDK's verify method</li>
                        </ol>
                    </div>
                    <h3>Alternative: Verify via API</h3>
                    <p>Use this curl command to verify the signed content:</p>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto;">
curl -X POST http://localhost:9000/api/v1/verify \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "YOUR_SIGNED_TEXT_HERE"}}'
                    </pre>
                    <p style="margin-top: 40px; color: #666; font-size: 14px;">
                        For production use with persistent verification, use a non-demo API key.
                    </p>
                </body>
            </html>
            """,
            status_code=404,
        )

    mapping = getattr(row, "_mapping", None)
    signed_text = mapping["signed_text"] if mapping else row[0]
    title = mapping["title"] if mapping else row[1]
    org_id = mapping["organization_id"] if mapping else row[2]

    execution = await execute_verification(payload_text=signed_text, db=db)
    reason_code = determine_reason_code(execution=execution)
    signer_name = (
        execution.resolved_cert.organization_name
        if execution.resolved_cert
        else (execution.signer_id or "Unknown")
    )
    manifest_json = _render_manifest_json(execution)
    status_color = "#00875A" if execution.is_valid else "#D14343"
    status_text = "Valid" if execution.is_valid else "Invalid"

    org_result = await db.execute(
        text("SELECT name FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    org_row = org_result.fetchone()
    org_mapping = getattr(org_row, "_mapping", None) if org_row else None
    org_name = org_mapping["name"] if org_mapping else (org_row[0] if org_row else "Unknown")

    return HTMLResponse(
        content=f"""
    <html>
        <head>
            <title>Verification Result - {title or document_id}</title>
            <style>
                body {{ font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
                .status {{ font-size: 24px; font-weight: bold; color: {status_color}; margin: 20px 0; }}
                .info {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .label {{ font-weight: bold; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Content Verification</h1>
            <div class="status">{status_text}</div>
            <div class="info">
                <p><span class="label">Document ID:</span> {document_id}</p>
                <p><span class="label">Title:</span> {title or "Untitled"}</p>
                <p><span class="label">Organization:</span> {org_name}</p>
                <p><span class="label">Signer ID:</span> {execution.signer_id or "Unknown"}</p>
                <p><span class="label">Signer Name:</span> {signer_name}</p>
                <p><span class="label">Reason Code:</span> {reason_code}</p>
            </div>
            <h2>Manifest Details</h2>
            <pre>{manifest_json}</pre>
            <p style="margin-top: 40px; color: #666; font-size: 14px;">
                Verified by EncypherAI Enterprise API
            </p>
        </body>
    </html>
    """
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(
    verify_request: VerifyRequest,
    raw_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify C2PA manifest in signed content using the encypher-ai library.

    This endpoint is public, rate limited, and returns structured machine-friendly
    verdicts that SDKs consume.
    """

    correlation_id = f"req-{uuid4().hex}"
    await public_rate_limiter(raw_request, endpoint_type="verify_single")

    payload_bytes = len(verify_request.text.encode("utf-8"))
    if payload_bytes == 0:
        return _error_response(
            status.HTTP_400_BAD_REQUEST,
            correlation_id=correlation_id,
            code="ERR_VERIFY_PAYLOAD_EMPTY",
            message="Verification payload is empty.",
            hint="Provide text that includes an embedded manifest.",
        )
    if payload_bytes > MAX_VERIFY_BYTES:
        return _error_response(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            correlation_id=correlation_id,
            code="ERR_VERIFY_PAYLOAD_TOO_LARGE",
            message="Verification payload exceeds the 2 MB limit.",
            hint="Submit smaller payloads or use the batch endpoint.",
        )

    execution = await execute_verification(payload_text=verify_request.text, db=db)
    reason_code = determine_reason_code(execution=execution)

    verdict = build_verdict(
        execution=execution,
        reason_code=reason_code,
        payload_bytes=payload_bytes,
    )

    response = VerifyResponse(
        success=True,
        data=verdict,
        error=None,
        correlation_id=correlation_id,
    )
    return response

