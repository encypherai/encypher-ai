"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional, Set
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from encypher import UnicodeMetadata
except ImportError as exc:  # pragma: no cover - import guard
        raise ImportError(
            "encypher-ai package not found. "
            "Please install the preview version with C2PA support."
        ) from exc

from app.database import get_db
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.request_models import VerifyRequest
from app.models.response_models import ErrorDetail, VerifyResponse, VerifyVerdict
from app.services.certificate_service import ResolvedCertificate, certificate_resolver

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_VERIFY_BYTES = 2 * 1024 * 1024  # 2 MB


def _coerce_manifest(raw: Any) -> Dict[str, Any]:
    """Coerce manifest payloads into dictionaries for serialization."""

    if isinstance(raw, dict):
        return raw
    for attr in ("model_dump", "dict"):
        if hasattr(raw, attr):
            try:
                return getattr(raw, attr)()
            except Exception:  # pragma: no cover - defensive
                continue
    return {}


def _parse_manifest_timestamp(manifest: Dict[str, Any]) -> Optional[datetime]:
    """Extract ISO8601 timestamp from manifest metadata."""

    timestamp_value = manifest.get("signature_timestamp") or manifest.get("timestamp")
    if isinstance(timestamp_value, datetime):
        return timestamp_value
    if isinstance(timestamp_value, str):
        value = timestamp_value.strip()
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


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


def _determine_reason_code(
    *,
    is_valid: bool,
    missing_signers: Set[str],
    revoked_signers: Set[str],
    signer_id: Optional[str],
    exception_message: Optional[str],
) -> str:
    """Map verification context to a stable reason code."""

    if is_valid:
        return "OK"
    if revoked_signers:
        return "CERT_REVOKED"
    if missing_signers:
        return "CERT_NOT_FOUND"
    if not signer_id:
        return "SIGNER_UNKNOWN"
    if exception_message:
        return "VERIFY_EXCEPTION"
    return "SIGNATURE_INVALID"


async def _execute_verification(
    *,
    payload_text: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """Run UnicodeMetadata verification with cached certificate resolution."""

    await certificate_resolver.refresh_cache(db)
    missing_signers: Set[str] = set()
    revoked_signers: Set[str] = set()

    def resolve_public_key(signer_id: str):
        cert = certificate_resolver.get(signer_id)
        if not cert:
            missing_signers.add(signer_id)
            return None
        if not cert.is_active():
            revoked_signers.add(signer_id)
            return None
        return cert.public_key

    start = time.perf_counter()
    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=payload_text,
            public_key_resolver=resolve_public_key,
        )
        exception_message = None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Verification runtime error: %s", exc, exc_info=True)
        is_valid = False
        signer_id = None
        manifest = {}
        exception_message = str(exc)

    duration_ms = int((time.perf_counter() - start) * 1000)
    manifest_dict = _coerce_manifest(manifest)
    resolved_cert = certificate_resolver.get(signer_id) if signer_id else None

    return {
        "is_valid": is_valid,
        "signer_id": signer_id,
        "manifest": manifest_dict,
        "missing_signers": missing_signers,
        "revoked_signers": revoked_signers,
        "resolved_cert": resolved_cert,
        "duration_ms": duration_ms,
        "exception_message": exception_message,
    }


def _build_verdict(
    *,
    verification: Dict[str, Any],
    reason_code: str,
    resolved_cert: Optional[ResolvedCertificate],
    manifest: Dict[str, Any],
    payload_bytes: int,
) -> VerifyVerdict:
    """Construct a VerifyVerdict payload from execution context."""

    details: Dict[str, Any] = {
        "manifest": manifest,
        "duration_ms": verification["duration_ms"],
        "payload_bytes": payload_bytes,
    }
    if verification["missing_signers"]:
        details["missing_signers"] = sorted(verification["missing_signers"])
    if verification["revoked_signers"]:
        details["revoked_signers"] = sorted(verification["revoked_signers"])
    if verification["exception_message"]:
        details["exception"] = verification["exception_message"]
    if resolved_cert:
        details["certificate_status"] = resolved_cert.status.value
        if resolved_cert.certificate_rotated_at:
            details["certificate_rotated_at"] = resolved_cert.certificate_rotated_at.isoformat()

    timestamp = _parse_manifest_timestamp(manifest)
    signer_name = resolved_cert.organization_name if resolved_cert else (verification["signer_id"] or None)

    return VerifyVerdict(
        valid=verification["is_valid"],
        tampered=not verification["is_valid"],
        reason_code=reason_code,
        signer_id=verification["signer_id"],
        signer_name=signer_name,
        timestamp=timestamp,
        details=details,
    )


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

    verification = await _execute_verification(payload_text=signed_text, db=db)
    reason_code = _determine_reason_code(
        is_valid=verification["is_valid"],
        missing_signers=verification["missing_signers"],
        revoked_signers=verification["revoked_signers"],
        signer_id=verification["signer_id"],
        exception_message=verification["exception_message"],
    )
    resolved_cert: Optional[ResolvedCertificate] = verification["resolved_cert"]
    signer_id = verification["signer_id"]
    signer_name = resolved_cert.organization_name if resolved_cert else (signer_id or "Unknown")
    manifest_json = json.dumps(verification["manifest"], indent=2) if verification["manifest"] else "{}"
    status_color = "#00875A" if verification["is_valid"] else "#D14343"
    status_text = "✅ Valid" if verification["is_valid"] else "⚠️ Invalid"

    org_result = await db.execute(
        text("SELECT organization_name FROM organizations WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    org_row = org_result.fetchone()
    org_mapping = getattr(org_row, "_mapping", None) if org_row else None
    org_name = org_mapping["organization_name"] if org_mapping else (org_row[0] if org_row else "Unknown")

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
                <p><span class="label">Signer ID:</span> {signer_id or "Unknown"}</p>
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

    verification = await _execute_verification(payload_text=verify_request.text, db=db)
    manifest = verification["manifest"]
    resolved_cert: Optional[ResolvedCertificate] = verification["resolved_cert"]
    reason_code = _determine_reason_code(
        is_valid=verification["is_valid"],
        missing_signers=verification["missing_signers"],
        revoked_signers=verification["revoked_signers"],
        signer_id=verification["signer_id"],
        exception_message=verification["exception_message"],
    )

    verdict = _build_verdict(
        verification=verification,
        reason_code=reason_code,
        resolved_cert=resolved_cert,
        manifest=manifest,
        payload_bytes=payload_bytes,
    )

    response = VerifyResponse(
        success=True,
        data=verdict,
        error=None,
        correlation_id=correlation_id,
    )
    return response
