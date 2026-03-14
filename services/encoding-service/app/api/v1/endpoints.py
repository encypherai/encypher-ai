"""
API endpoints for Encoding Service v1
"""

import logging
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db.session import get_db
from ...models.schemas import (
    DocumentEmbed,
    DocumentSign,
    DocumentSummary,
    ManifestResponse,
    OperationStats,
    SignedDocumentResponse,
)
from ...services.encoding_service import EncodingService
from .responses import make_error

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BINARY_HINT = "Content must be plain text. Strip binary data or base64-encode it before sending."
_AUTH_HINT = "Pass a valid Bearer token in the Authorization header. See POST /api/v1/auth/token for how to obtain one."
_KEY_HINT = "Provide a valid api_key in the request body. Keys are issued at POST /api/v1/keys."
_PERM_HINT = "Your API key lacks the required permission. Contact support to update your key permissions."
_NOT_FOUND_HINT = "Check the document_id and ensure it belongs to your account."
_SERVER_HINT = "An internal error occurred. Retry after a moment or contact support if the issue persists."
_AUTH_SVC_HINT = "The authentication service is temporarily unreachable. Retry in a few seconds."


def _validate_text_content(content: str, request: Request) -> Optional[JSONResponse]:
    """
    Guard against binary content embedded in text fields.

    Returns a 400 JSONResponse if binary content is detected, else None.
    """
    if "\x00" in content:
        return make_error(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content contains null bytes and appears to be binary.",
            hint=_BINARY_HINT,
            request=request,
        )
    # Reject C0 control chars except common whitespace (tab, newline, carriage return)
    for char in content:
        code = ord(char)
        if code < 0x20 and code not in (0x09, 0x0A, 0x0D):
            return make_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content contains a disallowed control character (U+{code:04X}).",
                hint=_BINARY_HINT,
                request=request,
            )
    return None


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


async def get_current_user(
    request: Request,
    authorization: str = Header(...),
) -> dict:
    """
    Verify user token with auth service.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization},
            )

            if response.status_code != 200:
                raise _make_401(request)

            return response.json()
    except httpx.RequestError:
        raise _make_503(request)


def _make_401(request: Request):
    from fastapi import HTTPException

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"hint": _AUTH_HINT, "X-Request-ID": _rid(request)},
    )


def _make_503(request: Request):
    from fastapi import HTTPException

    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Auth service unavailable",
        headers={"hint": _AUTH_SVC_HINT, "X-Request-ID": _rid(request)},
    )


def _rid(request: Request) -> str:
    """Return the request ID string, or empty string if unavailable."""
    return str(getattr(request.state, "request_id", "") or "")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/sign",
    response_model=SignedDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_document(
    request: Request,
    document_data: DocumentSign,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Sign a document with a cryptographic signature.

    **Important:** Requires a valid API key.

    - **content**: Document content to sign (plain text; binary data rejected)
    - **metadata**: Optional metadata to include
    - **format**: Document format (text, json, markdown)
    - **api_key**: Valid API key from Key Service
    """
    # Guard: binary content
    binary_error = _validate_text_content(document_data.content, request)
    if binary_error is not None:
        return binary_error

    # Verify API key
    key_info = await EncodingService.verify_api_key(document_data.api_key)

    if not key_info:
        return make_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            hint=_KEY_HINT,
            request=request,
        )

    # Check permissions
    if "sign" not in key_info.get("permissions", []):
        return make_error(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have 'sign' permission",
            hint=_PERM_HINT,
            request=request,
        )

    user_id = key_info["user_id"]

    # Check document size
    if len(document_data.content) > settings.MAX_DOCUMENT_SIZE:
        return make_error(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document size exceeds maximum of {settings.MAX_DOCUMENT_SIZE} bytes",
            request=request,
        )

    # Check format
    if document_data.format not in settings.supported_formats_list:
        return make_error(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format. Supported: {settings.SUPPORTED_FORMATS}",
            request=request,
        )

    # Resolve signing key from configuration (never hardcoded)
    private_key_pem = settings.SIGNING_PRIVATE_KEY
    if not private_key_pem:
        logger.error("SIGNING_PRIVATE_KEY is not configured")
        return make_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signing service is not configured",
            hint=_SERVER_HINT,
            request=request,
        )

    try:
        db_document, processing_time = EncodingService.sign_document(
            db=db,
            user_id=user_id,
            document_data=document_data,
            private_key_pem=private_key_pem,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        response_data = SignedDocumentResponse(
            document_id=db_document.document_id,
            encoded_content=db_document.encoded_content,
            signature=db_document.signature,
            content_hash=db_document.content_hash,
            manifest=db_document.manifest,
            created_at=db_document.created_at,
            processing_time_ms=round(processing_time, 2),
        )

        from fastapi.responses import Response

        json_response = response_data.model_dump_json()
        return Response(
            content=json_response,
            status_code=status.HTTP_201_CREATED,
            media_type="application/json",
            headers={"X-Processing-Time-Ms": str(round(processing_time, 2))},
        )

    except Exception:
        logger.exception("sign_document failed for user %s", user_id)
        return make_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sign document",
            hint=_SERVER_HINT,
            request=request,
        )


@router.post(
    "/embed",
    response_model=SignedDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def embed_metadata(
    request: Request,
    document_data: DocumentEmbed,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Embed metadata into a document without signing.

    - **content**: Document content (plain text; binary data rejected)
    - **metadata**: Metadata to embed
    - **format**: Document format
    """
    # Guard: binary content
    binary_error = _validate_text_content(document_data.content, request)
    if binary_error is not None:
        return binary_error

    # Check document size
    if len(document_data.content) > settings.MAX_DOCUMENT_SIZE:
        return make_error(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document size exceeds maximum of {settings.MAX_DOCUMENT_SIZE} bytes",
            request=request,
        )

    try:
        db_document = EncodingService.embed_metadata(
            db=db,
            user_id=current_user["id"],
            document_data=document_data,
        )

        return SignedDocumentResponse(
            document_id=db_document.document_id,
            encoded_content=db_document.encoded_content,
            signature=db_document.signature,
            content_hash=db_document.content_hash,
            manifest=db_document.manifest,
            created_at=db_document.created_at,
        )

    except Exception:
        logger.exception("embed_metadata failed for user %s", current_user.get("id"))
        return make_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to embed metadata",
            hint=_SERVER_HINT,
            request=request,
        )


@router.get("/documents", response_model=List[DocumentSummary])
async def list_documents(
    request: Request,
    limit: int = Query(default=20, ge=1, le=50, description="Maximum number of documents to return (1-50)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List documents for the current user.

    Returns lightweight summaries (IDs and hashes only -- no document content).

    - **limit**: Maximum number of results (1-50, default 20)
    """
    documents = EncodingService.get_user_documents(db, current_user["id"], limit)
    return documents


@router.get("/documents/{document_id}", response_model=DocumentSummary)
async def get_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a summary of a specific document.

    - **document_id**: Document ID
    """
    document = EncodingService.get_document(db, document_id, current_user["id"])

    if not document:
        return make_error(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
            hint=_NOT_FOUND_HINT,
            request=request,
        )

    return document


@router.get("/documents/{document_id}/manifest", response_model=ManifestResponse)
async def get_manifest(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get the manifest for a document.

    - **document_id**: Document ID
    """
    document = EncodingService.get_document(db, document_id, current_user["id"])

    if not document:
        return make_error(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
            hint=_NOT_FOUND_HINT,
            request=request,
        )

    return ManifestResponse(**document.manifest)


@router.get("/stats", response_model=OperationStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get operation statistics for the current user.
    """
    stats = EncodingService.get_operation_stats(db, current_user["id"])
    return OperationStats(**stats)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "encoding-service"}
