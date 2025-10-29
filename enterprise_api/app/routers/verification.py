"""
Verification router for C2PA manifest verification.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

try:
    from encypher import UnicodeMetadata
except ImportError:
    raise ImportError(
        "encypher-ai package not found. "
        "Please install the preview version with C2PA support."
    )

from app.database import get_db
from app.models.request_models import VerifyRequest
from app.models.response_models import VerifyResponse
from app.utils.crypto_utils import extract_public_key_from_certificate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/verify/{document_id}")
async def verify_by_document_id(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a document by its ID (for clickable verification links).
    
    This endpoint retrieves the signed text from the database and verifies it.
    Returns HTML page with verification results for browser display.
    
    Args:
        document_id: Document ID to verify
        db: Database session
        
    Returns:
        HTML page with verification results
    """
    from fastapi.responses import HTMLResponse
    
    # Retrieve document from database
    result = await db.execute(
        text("SELECT signed_text, title, organization_id FROM documents WHERE document_id = :doc_id"),
        {"doc_id": document_id}
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
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto;">curl -X POST http://localhost:9000/api/v1/verify \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "YOUR_SIGNED_TEXT_HERE"}}'</pre>
                    
                    <p style="margin-top: 40px; color: #666; font-size: 14px;">
                        For production use with persistent verification, use a non-demo API key.
                    </p>
                </body>
            </html>
            """,
            status_code=404
        )
    
    mapping = getattr(row, "_mapping", None)
    signed_text = mapping["signed_text"] if mapping else row[0]
    title = mapping["title"] if mapping else row[1]
    org_id = mapping["organization_id"] if mapping else row[2]
    
    # Verify the signed text using the existing verify logic
    # Get certificate for public key resolution
    cert_result = await db.execute(
        text("SELECT organization_id, certificate_pem FROM organizations")
    )
    cert_rows = cert_result.fetchall() if hasattr(cert_result, "fetchall") else [cert_result.fetchone()] if hasattr(cert_result, "fetchone") else []
    
    cert_map = {}
    for cert_row in cert_rows:
        if not cert_row:
            continue
        cert_mapping = getattr(cert_row, "_mapping", None)
        cert_org_id = cert_mapping["organization_id"] if cert_mapping else cert_row[0]
        certificate_pem = cert_mapping["certificate_pem"] if cert_mapping else cert_row[1]
        if certificate_pem:
            cert_map[cert_org_id] = certificate_pem
    
    def resolve_public_key(signer_id: str):
        cert_pem = cert_map.get(signer_id)
        if not cert_pem:
            return None
        try:
            return extract_public_key_from_certificate(cert_pem)
        except Exception:
            return None
    
    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=signed_text,
            public_key_resolver=resolve_public_key
        )
    except Exception as e:
        is_valid = False
        manifest = {}
    
    # Get organization name
    org_result = await db.execute(
        text("SELECT organization_name FROM organizations WHERE organization_id = :org_id"),
        {"org_id": org_id}
    )
    org_row = org_result.fetchone()
    org_mapping = getattr(org_row, "_mapping", None) if org_row else None
    org_name = org_mapping["organization_name"] if org_mapping else (org_row[0] if org_row else "Unknown")
    
    # Return HTML verification page
    status_color = "green" if is_valid else "red"
    status_text = "✓ Valid" if is_valid else "✗ Invalid"
    
    return HTMLResponse(content=f"""
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
            </div>
            
            <h2>Manifest Details</h2>
            <pre>{str(manifest)}</pre>
            
            <p style="margin-top: 40px; color: #666; font-size: 14px;">
                Verified by EncypherAI Enterprise API
            </p>
        </body>
    </html>
    """)


@router.post("/verify", response_model=VerifyResponse)
async def verify_content(
    request: VerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify C2PA manifest in signed content using encypher-ai library.

    This endpoint:
    1. Defines a public key resolver that queries the database
    2. Uses encypher-ai's UnicodeMetadata.verify_metadata()
    3. Returns verification result with manifest details

    Note: This endpoint does NOT require authentication (public verification).

    Args:
        request: VerifyRequest containing signed text
        db: Database session

    Returns:
        VerifyResponse with verification status and manifest details
    """
    logger.info(f"Verification request for {len(request.text)} characters")

    cert_result = await db.execute(
        text("SELECT organization_id, certificate_pem FROM organizations")
    )
    try:
        cert_rows = cert_result.fetchall()
    except AttributeError:
        single_row = (
            cert_result.fetchone()
            if hasattr(cert_result, "fetchone")
            else None
        )
        cert_rows = [single_row] if single_row else []

    cert_map = {}
    for row in cert_rows:
        if not row:
            continue
        mapping = getattr(row, "_mapping", None)
        organization_id = (
            mapping["organization_id"]
            if mapping and "organization_id" in mapping
            else row[0]
        )
        certificate_pem = (
            mapping["certificate_pem"]
            if mapping and "certificate_pem" in mapping
            else row[1]
        )
        if certificate_pem:
            cert_map[organization_id] = certificate_pem

    # Define public key resolver for encypher-ai
    def resolve_public_key(signer_id: str):
        """
        Resolve the public key for a signer from the cached certificate map.

        Args:
            signer_id: Organization ID from the C2PA manifest

        Returns:
            Ed25519PublicKey or None if not found
        """
        logger.debug(f"Resolving public key for signer: {signer_id}")
        cert_pem = cert_map.get(signer_id)
        if not cert_pem:
            logger.warning(f"No certificate found for signer: {signer_id}")
            return None

        try:
            public_key = extract_public_key_from_certificate(cert_pem)
            logger.debug(f"Successfully extracted public key for signer: {signer_id}")
            return public_key
        except Exception as e:
            logger.error(f"Failed to extract public key from certificate: {e}")
            return None

    # Use encypher-ai library to verify C2PA manifest
    try:
        logger.debug("Calling UnicodeMetadata.verify_metadata()")
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=request.text,
            public_key_resolver=resolve_public_key
        )
        logger.info(
            f"Verification result: valid={is_valid}, signer={signer_id}, "
            f"tampered={not is_valid}"
        )
    except Exception as e:
        logger.error(f"Verification failed with exception: {e}", exc_info=True)
        # Verification failed (tampered or invalid)
        return VerifyResponse(
            success=True,
            is_valid=False,
            tampered=True,
            signer_id="unknown",
            organization_name="Unknown",
            signature_timestamp=None,
            manifest={}
        )

    # Fetch organization details
    if signer_id:
        org_result = await db.execute(
            text("SELECT organization_name FROM organizations WHERE organization_id = :signer_id"),
            {"signer_id": signer_id}
        )
        org_row = org_result.fetchone()
        if org_row:
            mapping = getattr(org_row, "_mapping", None)
            if mapping and "organization_name" in mapping:
                org_name = mapping["organization_name"]
            else:
                org_name = org_row[0]
        else:
            org_name = "Unknown"
    else:
        org_name = "Unknown"

    # Extract timestamp from manifest
    signature_timestamp = manifest.get('signature_timestamp') if manifest else None

    return VerifyResponse(
        success=True,
        is_valid=is_valid,
        signer_id=signer_id or "unknown",
        organization_name=org_name,
        signature_timestamp=signature_timestamp,
        manifest=manifest or {},
        tampered=not is_valid
    )
