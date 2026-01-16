"""API endpoints for Verification Service v1"""
import time

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import httpx
import json
import os
from uuid import uuid4
import base64
import structlog

from encypher.core.keys import load_public_key_from_data
from encypher.core.payloads import deserialize_jumbf_payload
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.signing import extract_certificates_from_cose
try:
    from encypher.interop.c2pa import find_wrapper_info_bytes
except ImportError:  # pragma: no cover
    def find_wrapper_info_bytes(_text: str):
        return None

from ...db.session import get_db
from ...models.enterprise_schemas import ErrorDetail, VerifyRequest, VerifyResponse, VerifyVerdict
from ...models.schemas import (
    SignatureVerify,
    DocumentVerify,
    VerificationResponse,
    VerificationHistory,
    VerificationStats,
)
from ...services.verification_service import VerificationService
from ...core.config import settings
from ...utils.c2pa_trust_list import (
    fetch_trust_list,
    get_trust_anchors,
    set_trust_anchors_pem,
    validate_certificate_chain,
)

router = APIRouter()

MAX_VERIFY_BYTES = 2 * 1024 * 1024


def _count_variation_selectors(text: str) -> int:
    count = 0
    for ch in text:
        code = ord(ch)
        if 0xFE00 <= code <= 0xFE0F:
            count += 1
        elif 0xE0100 <= code <= 0xE01EF:
            count += 1
    return count


def _render_manifest_json(manifest: dict) -> str:
    """Pretty-print manifest JSON for HTML responses."""
    try:
        return json.dumps(manifest, indent=2) if manifest else "{}"
    except TypeError:
        return "{}"


def _error_response(
    status_code: int,
    *,
    correlation_id: str,
    code: str,
    message: str,
    hint: str | None = None,
) -> JSONResponse:
    payload = VerifyResponse(
        success=False,
        data=None,
        error=ErrorDetail(code=code, message=message, hint=hint),
        correlation_id=correlation_id,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def get_current_user(authorization: str = Header(None)) -> Optional[dict]:
    """Verify user token with auth service (optional)"""
    if not authorization:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


async def get_optional_organization(authorization: str = Header(None)) -> Optional[dict]:
    # TEAM_065: POST /api/v1/verify is public; only validate API key when provided.
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None

    api_key = authorization.split(" ", 1)[1].strip()
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KEY_SERVICE_URL}/api/v1/keys/validate",
                json={"key": api_key},
                timeout=5.0,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Key service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = response.json()
    data = payload.get("data")
    if not payload.get("success") or not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return data


def _demo_private_key_bytes() -> bytes:
    # TEAM_065: Align demo verification with local docker-compose (32 bytes of 0x00) and allow override.
    for env_name in ("DEMO_PRIVATE_KEY_HEX", "SECRET_KEY"):
        candidate = os.getenv(env_name)
        if candidate:
            try:
                value = bytes.fromhex(candidate.strip())
                if len(value) == 32:
                    return value
            except ValueError:
                pass
    return b"\x00" * 32


def _demo_public_key():
    from cryptography.hazmat.primitives.asymmetric import ed25519

    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(_demo_private_key_bytes())
    return private_key.public_key()


def _extract_embedded_c2pa_public_key(_text: str):
    """Extract leaf public key from embedded C2PA COSE x5chain if present."""
    try:
        info = find_wrapper_info_bytes(_text)
    except Exception:  # pragma: no cover
        info = None
    if not info:
        return None

    manifest_bytes, _wrapper_start, _wrapper_length = info
    try:
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
    except Exception:
        return None
    if not isinstance(manifest_store, dict):
        return None

    cose_sign1_b64 = manifest_store.get("cose_sign1")
    if not isinstance(cose_sign1_b64, str) or not cose_sign1_b64:
        return None

    try:
        cose_bytes = base64.b64decode(cose_sign1_b64)
    except Exception:
        return None

    try:
        certs = extract_certificates_from_cose(cose_bytes)
    except Exception:
        return None

    if not certs:
        return None

    return certs[0].public_key()


async def _ensure_trust_list_loaded() -> None:
    if get_trust_anchors():
        return

    pem = os.getenv("C2PA_TRUST_LIST_PEM")
    if pem:
        set_trust_anchors_pem(pem)
        return

    fetch_enabled = os.getenv("C2PA_TRUST_LIST_FETCH", "").strip().lower() in {"1", "true", "yes"}
    if not fetch_enabled:
        return

    try:
        pem = await fetch_trust_list()
    except Exception:  # pragma: no cover
        return
    set_trust_anchors_pem(pem)


async def _is_embedded_c2pa_key_trusted(text: str) -> bool:
    await _ensure_trust_list_loaded()

    if not get_trust_anchors():
        return False

    try:
        info = find_wrapper_info_bytes(text)
    except Exception:  # pragma: no cover
        info = None
    if not info:
        return False

    manifest_bytes, _wrapper_start, _wrapper_length = info
    try:
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
    except Exception:
        return False
    if not isinstance(manifest_store, dict):
        return False

    cose_sign1_b64 = manifest_store.get("cose_sign1")
    if not isinstance(cose_sign1_b64, str) or not cose_sign1_b64:
        return False

    try:
        cose_bytes = base64.b64decode(cose_sign1_b64)
    except Exception:
        return False

    try:
        certs = extract_certificates_from_cose(cose_bytes)
    except Exception:
        return False

    if not certs:
        return False

    from cryptography.hazmat.primitives import serialization

    leaf_pem = certs[0].public_bytes(serialization.Encoding.PEM).decode("utf-8")
    chain_pem = None
    if len(certs) > 1:
        chain_pem = "\n".join(
            cert.public_bytes(serialization.Encoding.PEM).decode("utf-8") for cert in certs[1:]
        )
    ok, _err, _parsed = validate_certificate_chain(leaf_pem, chain_pem)
    return ok


@router.post(
    "",
    response_model=VerifyResponse,
    description="Verify signed content and return a structured verdict.",
)
async def verify_text(
    verify_request: VerifyRequest,
    organization: Optional[dict] = Depends(get_optional_organization),
):
    logger = structlog.get_logger(__name__)
    correlation_id = f"req-{uuid4().hex}"
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    payload_bytes = len(verify_request.text.encode("utf-8"))
    vs_count = _count_variation_selectors(verify_request.text)
    try:
        wrapper_info = find_wrapper_info_bytes(verify_request.text)
    except Exception:  # pragma: no cover
        wrapper_info = None
    has_c2pa_wrapper = bool(wrapper_info)

    logger.info(
        "verify_received",
        payload_bytes=payload_bytes,
        variation_selectors=vs_count,
        has_c2pa_wrapper=has_c2pa_wrapper,
        has_auth_context=bool(organization),
    )
    if payload_bytes > MAX_VERIFY_BYTES:
        return _error_response(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            correlation_id=correlation_id,
            code="ERR_VERIFY_PAYLOAD_TOO_LARGE",
            message="Verification payload exceeds the 2 MB limit.",
            hint="Submit smaller payloads.",
        )

    organization_id = organization.get("organization_id") if organization else None
    organization_name = organization.get("organization_name") if organization else None
    certificate_pem = organization.get("certificate_pem") if organization else None

    logger.info(
        "verify_org_context",
        organization_id=organization_id,
        has_org_certificate=bool(certificate_pem),
    )

    public_key = None
    if certificate_pem:
        try:
            public_key = load_public_key_from_data(certificate_pem)
        except Exception:
            public_key = None

    embedded_public_key = _extract_embedded_c2pa_public_key(verify_request.text)
    embedded_trusted = await _is_embedded_c2pa_key_trusted(verify_request.text)

    logger.info(
        "verify_embedded_key_context",
        has_embedded_public_key=embedded_public_key is not None,
        embedded_trusted=embedded_trusted,
    )

    def public_key_resolver(signer_id: str):
        # TEAM_065: Support demo/user signers without requiring org auth.
        # TEAM_066: Also support org_encypher* signers (e.g., org_encypher_marketing) which use demo key.
        if signer_id == "org_demo" or signer_id.startswith("user_") or signer_id.startswith("org_encypher"):
            return _demo_public_key()
        if organization_id and signer_id == organization_id:
            return public_key
        if embedded_public_key is not None:
            return embedded_public_key
        return None

    start = time.perf_counter()
    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=verify_request.text,
            public_key_resolver=public_key_resolver,
        )
        logger.info(
            "verify_unicode_metadata_result",
            is_valid=is_valid,
            signer_id=signer_id,
            manifest_type=type(manifest).__name__,
            manifest_keys=list(manifest.keys()) if isinstance(manifest, dict) else None,
        )
    except Exception as exc:
        logger.warning(
            "verify_unicode_metadata_exception",
            exception_type=type(exc).__name__,
            exception=str(exc),
            has_c2pa_wrapper=has_c2pa_wrapper,
        )
        # Fallback: Attempt C2PA wrapper-only verification.
        # This avoids failures when non-JSON VS blocks (e.g. mixed multi-embeddings)
        # break the legacy outer-payload extraction logic.
        try:
            info = find_wrapper_info_bytes(verify_request.text)
        except Exception:  # pragma: no cover - defensive
            info = None

        if info:
            manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
            try:
                manifest_store = deserialize_jumbf_payload(manifest_bytes)
                if isinstance(manifest_store, dict):
                    fallback_signer_id = manifest_store.get("signer_id")
                    cose_sign1 = manifest_store.get("cose_sign1")
                else:
                    fallback_signer_id = None
                    cose_sign1 = None

                if isinstance(fallback_signer_id, str) and isinstance(cose_sign1, str):
                    outer_payload = {
                        "format": "c2pa",
                        "signer_id": fallback_signer_id,
                        "cose_sign1": cose_sign1,
                    }
                    is_valid, signer_id, manifest = UnicodeMetadata._verify_c2pa(
                        original_text=verify_request.text,
                        outer_payload=outer_payload,
                        public_key_resolver=public_key_resolver,
                        return_payload_on_failure=True,
                        require_hard_binding=True,
                        wrapper_exclusion=(wrapper_start_byte, wrapper_length_byte),
                    )
                else:
                    is_valid, signer_id, manifest = False, None, None
            except Exception:  # pragma: no cover - defensive
                is_valid, signer_id, manifest = False, None, None

            logger.info(
                "verify_c2pa_fallback_result",
                is_valid=is_valid,
                signer_id=signer_id,
                manifest_type=type(manifest).__name__ if manifest is not None else None,
            )
        else:
            duration_ms = int((time.perf_counter() - start) * 1000)
            verdict = VerifyVerdict(
                valid=False,
                tampered=False,
                reason_code="VERIFY_EXCEPTION",
                signer_id=None,
                signer_name=None,
                timestamp=None,
                details={
                    "manifest": {},
                    "duration_ms": duration_ms,
                    "payload_bytes": payload_bytes,
                    "exception": str(exc),
                },
            )
            return VerifyResponse(success=True, data=verdict, error=None, correlation_id=correlation_id)

    # Fallback: no exception, but no signer_id extracted.
    if not signer_id:
        logger.info(
            "verify_missing_signer_id_primary",
            has_c2pa_wrapper=has_c2pa_wrapper,
            is_valid=is_valid,
        )
        try:
            info = find_wrapper_info_bytes(verify_request.text)
        except Exception:  # pragma: no cover - defensive
            info = None
        if info:
            manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
            try:
                manifest_store = deserialize_jumbf_payload(manifest_bytes)
                if isinstance(manifest_store, dict):
                    fallback_signer_id = manifest_store.get("signer_id")
                    cose_sign1 = manifest_store.get("cose_sign1")
                else:
                    fallback_signer_id = None
                    cose_sign1 = None
                if isinstance(fallback_signer_id, str) and isinstance(cose_sign1, str):
                    outer_payload = {
                        "format": "c2pa",
                        "signer_id": fallback_signer_id,
                        "cose_sign1": cose_sign1,
                    }
                    is_valid, signer_id, manifest = UnicodeMetadata._verify_c2pa(
                        original_text=verify_request.text,
                        outer_payload=outer_payload,
                        public_key_resolver=public_key_resolver,
                        return_payload_on_failure=True,
                        require_hard_binding=True,
                        wrapper_exclusion=(wrapper_start_byte, wrapper_length_byte),
                    )
            except Exception:  # pragma: no cover - defensive
                pass

        logger.info(
            "verify_missing_signer_id_fallback_result",
            is_valid=is_valid,
            signer_id=signer_id,
            manifest_type=type(manifest).__name__ if manifest is not None else None,
        )

    duration_ms = int((time.perf_counter() - start) * 1000)

    reason_code = "OK" if is_valid else "SIGNATURE_INVALID"
    if not signer_id:
        reason_code = "SIGNER_UNKNOWN"
    elif public_key_resolver(signer_id) is None:
        reason_code = "CERT_NOT_FOUND"
    elif is_valid and embedded_public_key is not None and not embedded_trusted and not (organization_id and signer_id == organization_id):
        # TEAM_065: Valid signature, but signer cannot be validated to a trusted root.
        reason_code = "UNTRUSTED_SIGNER"

    logger.info(
        "verify_verdict",
        reason_code=reason_code,
        is_valid=is_valid,
        signer_id=signer_id,
        payload_bytes=payload_bytes,
        duration_ms=duration_ms,
        has_c2pa_wrapper=has_c2pa_wrapper,
        variation_selectors=vs_count,
    )

    verdict = VerifyVerdict(
        valid=is_valid,
        tampered=(not is_valid and reason_code == "SIGNATURE_INVALID"),
        reason_code=reason_code,
        signer_id=signer_id,
        signer_name=(organization_name if (signer_id and signer_id == organization_id) else signer_id),
        timestamp=None,
        details={
            "manifest": manifest or {},
            "duration_ms": duration_ms,
            "payload_bytes": payload_bytes,
        },
    )

    return VerifyResponse(success=True, data=verdict, error=None, correlation_id=correlation_id)


@router.get("/{document_id}")
async def verify_by_document_id(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Verify a document by its ID (for clickable verification links).

    Returns an HTML page so users can preview verification state in a browser.
    This endpoint queries the content database for the signed document.
    """
    # Query content database for document
    # Note: verification-service uses same DATABASE_URL as content DB
    result = db.execute(
        text("SELECT signed_text, title, organization_id FROM documents WHERE id = :doc_id"),
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
curl -X POST https://api.encypherai.com/api/v1/verify \\
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

    # Extract row data (handle both mapping and tuple access)
    mapping = getattr(row, "_mapping", None)
    signed_text = mapping["signed_text"] if mapping else row[0]
    title = mapping["title"] if mapping else row[1]
    org_id = mapping["organization_id"] if mapping else row[2]

    # Verify the signed text
    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=signed_text,
            public_key_resolver=lambda _: None,  # No key resolver for HTML portal
        )
    except Exception:
        is_valid = False
        signer_id = None
        manifest = None

    reason_code = "OK" if is_valid else "SIGNATURE_INVALID"
    if not signer_id:
        reason_code = "SIGNER_UNKNOWN"

    manifest_json = _render_manifest_json(manifest or {})
    status_color = "#00875A" if is_valid else "#D14343"
    status_text = "Valid" if is_valid else "Invalid"
    signer_name = signer_id or "Unknown"

    # Try to get organization name from auth DB
    org_name = "Unknown"
    try:
        # Note: This requires verification-service to have access to auth DB
        # For now, we'll use a simple fallback
        org_name = org_id or "Unknown"
    except Exception:
        pass

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
                Verified by Encypher Verification Service
            </p>
        </body>
    </html>
    """
    )


@router.post("/signature", response_model=VerificationResponse)
async def verify_signature(
    verify_data: SignatureVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Verify a signature (public endpoint)
    
    - **content**: Original content
    - **signature**: Hex-encoded signature
    - **public_key_pem**: PEM-encoded public key
    """
    try:
        result, processing_time = VerificationService.verify_signature_only(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.post("/document", response_model=VerificationResponse)
async def verify_document(
    verify_data: DocumentVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Complete document verification (public endpoint)
    
    - **document_id**: Document ID from encoding service
    - **content**: Current content to verify
    """
    try:
        result, processing_time = await VerificationService.verify_document_complete(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.get("/history/{document_id}", response_model=List[VerificationHistory])
async def get_verification_history(
    document_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get verification history for a document (public endpoint)
    
    - **document_id**: Document ID
    - **limit**: Maximum number of results
    """
    history = VerificationService.get_verification_history(db, document_id, limit)
    return history


@router.get("/stats", response_model=VerificationStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Get verification statistics"""
    user_id = current_user["id"] if current_user else None
    stats = VerificationService.get_verification_stats(db, user_id)
    return VerificationStats(**stats)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "verification-service"}
