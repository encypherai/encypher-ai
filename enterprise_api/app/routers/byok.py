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
    C2PA_TSA_TRUST_LIST_URL,
    get_revocation_denylist_metadata,
    get_trust_anchor_subjects,
    get_trust_list_metadata,
    get_tsa_trust_list_metadata,
    validate_certificate_for_upload,
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

    # Check add_ons dict for BYOK purchased as a subscription add-on
    add_ons = organization.get("add_ons", {})
    if isinstance(add_ons, dict):
        byok_add_on = add_ons.get("byok", {})
        if isinstance(byok_add_on, dict) and byok_add_on.get("active"):
            byok_enabled = True

    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    allowed_tiers = {"enterprise", "strategic_partner", "demo"}

    if not byok_enabled and tier not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="BYOK (Bring Your Own Key) requires Enterprise tier or BYOK add-on. Please upgrade your plan.",
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
    private_key_pem: Optional[str] = Field(
        None,
        description="PEM-encoded private key matching the certificate. Required for the API to sign with this certificate.",
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

    @validator("private_key_pem")
    def validate_private_key_format(cls, v):
        if v and "-----BEGIN" not in v:
            raise ValueError("Private key must be in PEM format")
        return v.strip() if v else v


class CertificateUploadResponse(BaseModel):
    """Response for certificate upload."""

    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
    warnings: Optional[list[str]] = None


class TrustListResponse(BaseModel):
    """Response listing trusted CAs."""

    success: bool = True
    trusted_cas: list[str] = Field(default_factory=list)
    trust_list_url: str = "https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem"
    trust_list_fingerprint: Optional[str] = None
    trust_list_loaded_at: Optional[str] = None
    trust_list_source: Optional[str] = None
    trust_list_count: Optional[str] = None
    required_signer_eku_oids: list[str] = Field(default_factory=list)
    revocation_denylist: dict[str, str] = Field(default_factory=dict)
    tsa_trust_list: dict[str, Optional[str]] = Field(default_factory=dict)
    default_signing_mode: str = "organization"
    managed_signer_id: str = "encypher_managed"


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
    tsa_metadata = get_tsa_trust_list_metadata()
    tsa_trust_list_url = settings.c2pa_tsa_trust_list_url or C2PA_TSA_TRUST_LIST_URL
    trust_list_url = settings.c2pa_trust_list_url or C2PA_TRUST_LIST_URL
    return TrustListResponse(
        success=True,
        trusted_cas=subjects,
        trust_list_url=trust_list_url,
        trust_list_fingerprint=metadata.get("fingerprint"),
        trust_list_loaded_at=metadata.get("loaded_at"),
        trust_list_source=metadata.get("source"),
        trust_list_count=metadata.get("count"),
        required_signer_eku_oids=settings.c2pa_required_signer_eku_oids_list,
        revocation_denylist=get_revocation_denylist_metadata(),
        tsa_trust_list={
            "url": tsa_trust_list_url,
            "fingerprint": tsa_metadata.get("fingerprint"),
            "loaded_at": tsa_metadata.get("loaded_at"),
            "source": tsa_metadata.get("source"),
            "count": tsa_metadata.get("count"),
        },
        default_signing_mode=settings.default_signing_mode_normalized,
        managed_signer_id=settings.managed_signer_id,
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

    # Validate certificate structure, expiry, EKU, and chain integrity.
    # Trust list check is a soft warning -- untrusted certs can still be uploaded.
    is_valid, warnings_or_errors, parsed_cert = validate_certificate_for_upload(
        cert_pem=request.certificate_pem,
        chain_pem=request.chain_pem,
        required_eku_oids=settings.c2pa_required_signer_eku_oids_list,
    )

    if not is_valid:
        error_msg = warnings_or_errors[0] if warnings_or_errors else "Unknown validation error"
        logger.warning(f"Certificate validation failed for org {org_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate validation failed: {error_msg}",
        )

    trust_warnings: list[str] = warnings_or_errors if warnings_or_errors else []
    if trust_warnings:
        logger.info(f"Certificate uploaded with warnings for org {org_id}: {trust_warnings}")

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

    # Validate and encrypt private key if provided
    encrypted_private_key: Optional[bytes] = None
    if request.private_key_pem:
        from cryptography.hazmat.backends import default_backend as _default_backend

        from app.utils.crypto_utils import encrypt_private_key_pem

        try:
            private_key = serialization.load_pem_private_key(request.private_key_pem.encode(), password=None, backend=_default_backend())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid private key: {e}",
            )

        # Verify the private key matches the certificate's public key
        private_pub_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        cert_pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        if private_pub_bytes != cert_pub_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Private key does not match the certificate's public key",
            )

        encrypted_private_key = encrypt_private_key_pem(private_key)
        logger.info(f"Private key encrypted for org {org_id} (algorithm: {key_algorithm})")
    else:
        trust_warnings.append("No private key provided. The API cannot sign with this certificate until a matching private key is uploaded.")

    # Register the public key (or reactivate if already registered)
    result = await PublicKeyService.register_public_key(
        db=db,
        organization_id=org_id,
        public_key_pem=public_key_pem,
        key_name=request.key_name or f"CA-signed: {cert_subject[:50]}",
        key_algorithm=key_algorithm,
    )

    if not result.get("success"):
        error_msg = result.get("error", "")
        if "already registered" in error_msg:
            # Key exists (possibly revoked) -- reactivate it
            from sqlalchemy import text as sa_text

            fingerprint = PublicKeyService.compute_key_fingerprint(public_key_pem)
            await db.execute(
                sa_text("""
                    UPDATE public_keys
                    SET is_active = true, revoked_at = NULL, revoked_reason = NULL, key_name = :key_name
                    WHERE organization_id = :org_id AND key_fingerprint = :fingerprint
                """),
                {
                    "org_id": org_id,
                    "key_name": request.key_name or f"CA-signed: {cert_subject[:50]}",
                    "fingerprint": fingerprint,
                },
            )
            # Fetch the existing key ID
            existing = await db.execute(
                sa_text("SELECT id, key_fingerprint FROM public_keys WHERE organization_id = :org_id AND key_fingerprint = :fingerprint"),
                {"org_id": org_id, "fingerprint": fingerprint},
            )
            row = existing.fetchone()
            result = {
                "success": True,
                "data": {"id": row.id if row else "unknown", "key_fingerprint": fingerprint},
            }
            logger.info(f"Reactivated existing BYOK key for org {org_id}: {fingerprint}")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to register certificate"),
            )

    # Update organization's certificate and optionally private key
    from sqlalchemy import text

    try:
        if encrypted_private_key:
            update_result = await db.execute(
                text("""
                    UPDATE organizations
                    SET certificate_pem = :cert_pem,
                        certificate_chain = :chain_pem,
                        private_key_encrypted = :private_key_encrypted,
                        certificate_status = 'active',
                        certificate_rotated_at = :now,
                        certificate_expiry = :expiry
                    WHERE id = :org_id
                    RETURNING id
                """),
                {
                    "cert_pem": request.certificate_pem,
                    "chain_pem": request.chain_pem or "",
                    "private_key_encrypted": encrypted_private_key,
                    "now": datetime.utcnow(),
                    "expiry": cert_expiry,
                    "org_id": org_id,
                },
            )
        else:
            update_result = await db.execute(
                text("""
                    UPDATE organizations
                    SET certificate_pem = :cert_pem,
                        certificate_chain = :chain_pem,
                        certificate_status = 'active',
                        certificate_rotated_at = :now,
                        certificate_expiry = :expiry
                    WHERE id = :org_id
                    RETURNING id
                """),
                {
                    "cert_pem": request.certificate_pem,
                    "chain_pem": request.chain_pem or "",
                    "now": datetime.utcnow(),
                    "expiry": cert_expiry,
                    "org_id": org_id,
                },
            )

        updated_row = update_result.fetchone()
        if not updated_row:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Certificate upload failed: organization record not updated. The organization ID may not exist in the database.",
            )

        await db.commit()

        # Verify the data was actually persisted by reading it back
        verify_result = await db.execute(
            text("""
                SELECT certificate_pem IS NOT NULL AS has_cert,
                       private_key_encrypted IS NOT NULL AS has_key,
                       certificate_status
                FROM organizations WHERE id = :org_id
            """),
            {"org_id": org_id},
        )
        verify_row = verify_result.fetchone()
        if not verify_row or not verify_row.has_cert:
            logger.error("Post-commit verification failed: certificate_pem is NULL for org %s", org_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Certificate upload failed: data did not persist after commit. Contact support.",
            )
        if encrypted_private_key and not verify_row.has_key:
            logger.error("Post-commit verification failed: private_key_encrypted is NULL for org %s", org_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Certificate upload failed: private key did not persist after commit. Contact support.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update organization certificate for org {org_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Certificate upload failed: could not store certificate data. Error: {e}",
        )

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
            "certificate_stored": True,
            "private_key_stored": encrypted_private_key is not None,
        },
        warnings=trust_warnings or None,
    )
