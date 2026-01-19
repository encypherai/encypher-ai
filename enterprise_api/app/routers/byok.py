"""Customer-facing BYOK (Bring Your Own Key) endpoints."""

import logging
from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.admin import PublicKeyListResponse, PublicKeyRegisterRequest, PublicKeyRegisterResponse
from app.services.admin_service import PublicKeyService
from app.utils.c2pa_trust_list import (
    C2PA_TRUST_LIST_URL,
    get_trust_anchor_subjects,
    get_trust_list_metadata,
    validate_certificate_chain,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/byok", tags=["BYOK"])


def require_byok_business_tier(
    organization: dict = Depends(get_current_organization),
) -> dict:
    features = organization.get("features", {})
    byok_enabled = False
    if isinstance(features, dict):
        byok_enabled = features.get("byok", False)

    byok_enabled = byok_enabled or organization.get("byok_enabled", False)

    tier = (organization.get("tier") or "starter").lower().replace("-", "_")
    allowed_tiers = {"business", "enterprise", "strategic_partner", "demo"}

    if not byok_enabled and tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="BYOK (Bring Your Own Key) requires Business tier or higher. Please upgrade your plan.",
        )

    return organization


@router.post(
    "/public-keys",
    response_model=PublicKeyRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a public key",
    description="Register a BYOK public key for signature verification.",
)
async def register_public_key(
    request: PublicKeyRegisterRequest,
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyRegisterResponse:
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")
    org_id = cast(str, org_id)

    result = await PublicKeyService.register_public_key(
        db=db,
        organization_id=org_id,
        public_key_pem=request.public_key_pem,
        key_name=request.key_name,
        key_algorithm=request.key_algorithm,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to register public key"),
        )

    return PublicKeyRegisterResponse(success=True, data=result.get("data"))


@router.get(
    "/public-keys",
    response_model=PublicKeyListResponse,
    summary="List public keys",
    description="List all registered public keys for the organization.",
)
async def list_public_keys(
    include_revoked: bool = Query(False, description="Include revoked keys"),
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> PublicKeyListResponse:
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")
    org_id = cast(str, org_id)

    result = await PublicKeyService.list_public_keys(
        db=db,
        organization_id=org_id,
        include_revoked=include_revoked,
    )

    return PublicKeyListResponse(success=True, data=result.get("data", {}))


@router.delete(
    "/public-keys/{key_id}",
    summary="Revoke a public key",
    description="Revoke a registered public key. Revoked keys cannot be used for verification.",
)
async def revoke_public_key(
    key_id: str,
    reason: str | None = Query(None, description="Reason for revocation"),
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> dict:
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")
    org_id = cast(str, org_id)

    result = await PublicKeyService.revoke_public_key(
        db=db,
        organization_id=org_id,
        key_id=key_id,
        reason=reason,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to revoke public key"),
        )

    return {"success": True, "data": result.get("data")}


# =============================================================================
# Certificate Upload (CA-Signed BYOK)
# =============================================================================


class CertificateUploadRequest(BaseModel):
    """Request to upload a CA-signed certificate for BYOK."""

    certificate_pem: str = Field(
        ...,
        description="PEM-encoded X.509 certificate (must chain to C2PA trusted CA)",
        min_length=100,
    )
    chain_pem: Optional[str] = Field(
        None,
        description="PEM-encoded intermediate certificates (if not included in certificate_pem)",
    )
    key_name: Optional[str] = Field(
        None,
        description="Friendly name for this certificate",
    )

    @validator("certificate_pem")
    def validate_cert_format(cls, v):
        if "-----BEGIN CERTIFICATE-----" not in v:
            raise ValueError("Certificate must be in PEM format")
        return v.strip()


class CertificateUploadResponse(BaseModel):
    """Response for certificate upload."""

    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None


class TrustListResponse(BaseModel):
    """Response listing trusted CAs."""

    success: bool = True
    trusted_cas: list[str] = Field(default_factory=list)
    trust_list_url: str = "https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem"
    trust_list_fingerprint: Optional[str] = None
    trust_list_loaded_at: Optional[str] = None
    trust_list_source: Optional[str] = None
    trust_list_count: Optional[str] = None


@router.get(
    "/trusted-cas",
    response_model=TrustListResponse,
    summary="List trusted Certificate Authorities",
    description="Returns the list of C2PA-trusted CAs that can issue signing certificates.",
)
async def list_trusted_cas() -> TrustListResponse:
    """
    List Certificate Authorities trusted for BYOK certificate validation.

    These CAs are from the official C2PA trust list. Certificates issued by
    these CAs (or their subordinate CAs) can be used for BYOK signing.
    """
    subjects = get_trust_anchor_subjects()
    metadata = get_trust_list_metadata()
    trust_list_url = settings.c2pa_trust_list_url or C2PA_TRUST_LIST_URL
    return TrustListResponse(
        success=True,
        trusted_cas=subjects,
        trust_list_url=trust_list_url,
        trust_list_fingerprint=metadata.get("fingerprint"),
        trust_list_loaded_at=metadata.get("loaded_at"),
        trust_list_source=metadata.get("source"),
        trust_list_count=metadata.get("count"),
    )


@router.post(
    "/certificates",
    response_model=CertificateUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CA-signed certificate",
    description="Upload an X.509 certificate signed by a C2PA-trusted CA for BYOK signing.",
)
async def upload_certificate(
    request: CertificateUploadRequest,
    organization: dict = Depends(require_byok_business_tier),
    db: AsyncSession = Depends(get_db),
) -> CertificateUploadResponse:
    """
    Upload a CA-signed certificate for BYOK.

    The certificate must chain to a CA in the C2PA trust list:
    - Google C2PA Root CA
    - SSL.com C2PA Root CAs
    - DigiCert C2PA Root CAs
    - Adobe, Trufo, vivo, Xiaomi, Irdeto

    Enterprise customers can obtain certificates from these CAs and upload
    them here to use their own signing identity.
    """
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")
    org_id = cast(str, org_id)

    # Validate certificate chains to C2PA trust anchor
    is_valid, error_msg, parsed_cert = validate_certificate_chain(
        cert_pem=request.certificate_pem,
        chain_pem=request.chain_pem,
    )

    if not is_valid:
        logger.warning(f"Certificate validation failed for org {org_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate validation failed: {error_msg}. "
            f"Certificate must chain to a C2PA-trusted CA. "
            f"See GET /byok/trusted-cas for the list of trusted CAs.",
        )

    # Extract certificate info
    from cryptography.hazmat.primitives import serialization

    if parsed_cert is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificate parsing failed")

    cert_subject = parsed_cert.subject.rfc4514_string()
    cert_issuer = parsed_cert.issuer.rfc4514_string()
    cert_expiry = parsed_cert.not_valid_after_utc

    # Extract public key PEM for storage
    public_key = parsed_cert.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    # Determine key algorithm
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

    if isinstance(public_key, ed25519.Ed25519PublicKey):
        key_algorithm = "Ed25519"
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        key_algorithm = f"EC-{public_key.curve.name}"
    elif isinstance(public_key, rsa.RSAPublicKey):
        key_algorithm = f"RSA-{public_key.key_size}"
    else:
        key_algorithm = "Unknown"

    # Register the public key
    result = await PublicKeyService.register_public_key(
        db=db,
        organization_id=org_id,
        public_key_pem=public_key_pem,
        key_name=request.key_name or f"CA-signed: {cert_subject[:50]}",
        key_algorithm=key_algorithm,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to register certificate"),
        )

    # Also update organization's certificate fields for verification
    from sqlalchemy import text

    try:
        await db.execute(
            text("""
                UPDATE organizations
                SET certificate_pem = :cert_pem,
                    certificate_chain = :chain_pem,
                    certificate_status = 'active',
                    certificate_rotated_at = :now,
                    certificate_expiry = :expiry
                WHERE id = :org_id
            """),
            {
                "cert_pem": request.certificate_pem,
                "chain_pem": request.chain_pem or "",
                "now": datetime.utcnow(),
                "expiry": cert_expiry,
                "org_id": org_id,
            },
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to update organization certificate: {e}")
        # Don't fail - the public key was registered successfully

    logger.info(f"Certificate uploaded for org {org_id}: subject={cert_subject}, issuer={cert_issuer}")

    return CertificateUploadResponse(
        success=True,
        data={
            "key_id": result["data"]["id"],
            "subject": cert_subject,
            "issuer": cert_issuer,
            "algorithm": key_algorithm,
            "expires_at": cert_expiry.isoformat(),
            "fingerprint": result["data"]["key_fingerprint"],
        },
    )
