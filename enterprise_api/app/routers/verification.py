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

    # Define public key resolver for encypher-ai
    async def resolve_public_key(signer_id: str):
        """
        Query database for organization's certificate and extract public key.

        This function is called by UnicodeMetadata.verify_metadata() to
        resolve the public key for the given signer ID.

        Args:
            signer_id: Organization ID from the C2PA manifest

        Returns:
            Ed25519PublicKey or None if not found
        """
        logger.debug(f"Resolving public key for signer: {signer_id}")

        result = await db.execute(
            text("SELECT certificate_pem FROM organizations WHERE organization_id = :signer_id"),
            {"signer_id": signer_id}
        )
        row = result.fetchone()

        if not row or not row[0]:
            logger.warning(f"No certificate found for signer: {signer_id}")
            return None

        cert_pem = row[0]

        try:
            # Extract public key from certificate
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
        org_name = org_row[0] if org_row else "Unknown"
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
