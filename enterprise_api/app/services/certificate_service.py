"""
Certificate resolution utilities for verification endpoints.

Provides a cached view of organization certificates and BYOK public keys
so verification requests can synchronously resolve signer public keys.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationCertificateStatus
from app.models.public_key import PublicKey
from app.utils.crypto_utils import decrypt_private_key, extract_public_key_from_certificate

logger = logging.getLogger(__name__)

# Type alias for supported public key types
SupportedPublicKey = Union[Ed25519PublicKey, ec.EllipticCurvePublicKey, rsa.RSAPublicKey]


class CertificateResolutionError(Exception):
    """Base exception for certificate resolver failures."""


class CertificateNotFoundError(CertificateResolutionError):
    """Raised when no certificate is available for a signer."""


class CertificateRevokedError(CertificateResolutionError):
    """Raised when a certificate exists but is revoked or inactive."""


@dataclass
class ResolvedCertificate:
    """Cached representation of an organization's certificate data."""

    signer_id: str
    organization_name: str
    certificate_pem: str
    public_key: SupportedPublicKey
    status: OrganizationCertificateStatus
    certificate_rotated_at: Optional[datetime] = None
    certificate_expiry: Optional[datetime] = None
    cert_chain_pem: Optional[str] = None
    is_byok: bool = False  # True if this is a BYOK public key (not org certificate)

    def is_active(self) -> bool:
        """Return True if the certificate should be trusted for verification."""

        if self.status in (OrganizationCertificateStatus.REVOKED,):
            return False
        if self.certificate_expiry and self.certificate_expiry < datetime.now(timezone.utc):
            return False
        return True


class CertificateResolver:
    """Caches organization certificates for fast public key resolution."""

    def __init__(self, ttl_seconds: int = 0):
        self._ttl = ttl_seconds
        self._cache: Dict[str, ResolvedCertificate] = {}
        self._cache_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def refresh_cache(self, db: AsyncSession) -> None:
        """Refresh the certificate cache when expired."""

        if self._ttl > 0 and self._cache and self._cache_expiry and self._cache_expiry > datetime.utcnow():
            return

        async with self._lock:
            if self._ttl > 0 and self._cache and self._cache_expiry and self._cache_expiry > datetime.utcnow():
                return

            stmt = select(
                Organization.organization_id,
                Organization.organization_name,
                Organization.certificate_pem,
                Organization.cert_chain_pem,
                Organization.certificate_status,
                Organization.certificate_rotated_at,
                Organization.certificate_expiry,
            )
            result = await db.execute(stmt)
            try:
                rows = result.all()
            except AttributeError:
                try:
                    rows = result.fetchall()
                except AttributeError:
                    single_row = result.fetchone() if hasattr(result, "fetchone") else None
                    rows = [single_row] if single_row else []

            refreshed: Dict[str, ResolvedCertificate] = {}
            for row in rows:
                if not row:
                    continue
                (
                    organization_id,
                    organization_name,
                    certificate_pem,
                    cert_chain_pem,
                    certificate_status,
                    certificate_rotated_at,
                    certificate_expiry,
                ) = row
                if not certificate_pem:
                    continue
                status = certificate_status or OrganizationCertificateStatus.ACTIVE
                try:
                    public_key = extract_public_key_from_certificate(certificate_pem)
                except (ValueError, TypeError) as e:
                    # Skip certificates that can't be parsed - log for debugging
                    import logging

                    logging.getLogger(__name__).warning(f"Failed to extract public key for org {organization_id}: {e}")
                    continue

                refreshed[organization_id] = ResolvedCertificate(
                    signer_id=organization_id,
                    organization_name=organization_name,
                    certificate_pem=certificate_pem,
                    public_key=public_key,
                    status=status,
                    certificate_rotated_at=certificate_rotated_at,
                    certificate_expiry=certificate_expiry,
                    cert_chain_pem=cert_chain_pem,
                    is_byok=False,
                )

            # Also load auto-provisioned keys (orgs with public_key or
            # private_key_encrypted but no certificate_pem).
            from sqlalchemy import text as sa_text

            auto_prov_result = await db.execute(
                sa_text(
                    "SELECT id, name, public_key, private_key_encrypted, "
                    "certificate_status, certificate_rotated_at, certificate_expiry "
                    "FROM organizations "
                    "WHERE certificate_pem IS NULL "
                    "AND (public_key IS NOT NULL OR private_key_encrypted IS NOT NULL)"
                )
            )
            try:
                auto_prov_rows = auto_prov_result.all()
            except AttributeError:
                auto_prov_rows = auto_prov_result.fetchall() if hasattr(auto_prov_result, "fetchall") else []

            for row in auto_prov_rows:
                if not row:
                    continue
                org_id = row[0]
                org_name = row[1]
                raw_pub = row[2]
                raw_priv = row[3]
                cert_status = row[4]
                cert_rotated = row[5]
                cert_expiry = row[6]

                if org_id in refreshed:
                    continue

                resolved_key = None
                if raw_pub:
                    try:
                        resolved_key = Ed25519PublicKey.from_public_bytes(bytes(raw_pub))
                    except Exception as e:
                        logger.debug("Failed to load public_key bytes for org %s: %s", org_id, e)

                if resolved_key is None and raw_priv:
                    try:
                        priv = decrypt_private_key(bytes(raw_priv))
                        resolved_key = priv.public_key()
                    except Exception as e:
                        logger.debug("Failed to derive public key from private_key_encrypted for org %s: %s", org_id, e)

                if resolved_key is not None:
                    status = cert_status or OrganizationCertificateStatus.ACTIVE
                    refreshed[org_id] = ResolvedCertificate(
                        signer_id=org_id,
                        organization_name=org_name or org_id,
                        certificate_pem="",  # No certificate PEM for auto-provisioned keys
                        public_key=resolved_key,
                        status=status,
                        certificate_rotated_at=cert_rotated,
                        certificate_expiry=cert_expiry,
                        cert_chain_pem=None,
                        is_byok=False,
                    )
                    logger.debug("Loaded auto-provisioned key for org %s", org_id)

            # Also load BYOK public keys from public_keys table
            byok_stmt = select(
                PublicKey.organization_id,
                PublicKey.key_name,
                PublicKey.public_key_pem,
                PublicKey.is_active,
                PublicKey.created_at,
            ).where(PublicKey.is_active.is_(True))

            byok_result = await db.execute(byok_stmt)
            try:
                byok_rows = byok_result.all()
            except AttributeError:
                byok_rows = byok_result.fetchall() if hasattr(byok_result, "fetchall") else []

            for row in byok_rows:
                if not row:
                    continue
                org_id, key_name, public_key_pem, is_active, created_at = row
                if not public_key_pem or not is_active:
                    continue

                # Skip if org already has a certificate (certificate takes precedence)
                if org_id in refreshed:
                    logger.debug(f"Org {org_id} has certificate, skipping BYOK key")
                    continue

                try:
                    byok_public_key = load_pem_public_key(public_key_pem.encode(), backend=default_backend())
                    if not isinstance(byok_public_key, (Ed25519PublicKey, ec.EllipticCurvePublicKey, rsa.RSAPublicKey)):
                        logger.warning("Unsupported BYOK public key type for org %s", org_id)
                        continue
                    refreshed[org_id] = ResolvedCertificate(
                        signer_id=org_id,
                        organization_name=key_name or org_id,
                        certificate_pem=public_key_pem,  # Store PEM for reference
                        public_key=byok_public_key,
                        status=OrganizationCertificateStatus.ACTIVE,
                        certificate_rotated_at=created_at,
                        certificate_expiry=None,  # BYOK keys don't expire (managed separately)
                        cert_chain_pem=None,
                        is_byok=True,
                    )
                    logger.debug(f"Loaded BYOK key for org {org_id}")
                except Exception as e:
                    logger.warning(f"Failed to load BYOK key for org {org_id}: {e}")

            self._cache = refreshed
            if self._ttl > 0:
                self._cache_expiry = datetime.utcnow() + timedelta(seconds=self._ttl)
            else:
                self._cache_expiry = None

    def get(self, signer_id: Optional[str]) -> Optional[ResolvedCertificate]:
        """Retrieve certificate metadata for a signer."""

        if not signer_id:
            return None
        return self._cache.get(signer_id)

    def resolve_public_key(self, signer_id: str) -> Optional[SupportedPublicKey]:
        """
        Return the public key for the signer, if available and active.

        Supports Ed25519, EC, and RSA keys from both organization certificates
        and BYOK public keys.

        This method is synchronous so it can be provided directly to the
        UnicodeMetadata.verify_metadata resolver callback.
        """

        cert = self._cache.get(signer_id)
        if not cert:
            return None
        if not cert.is_active():
            return None
        return cert.public_key

    def invalidate(self) -> None:
        """Clear the cache (used primarily in tests)."""

        self._cache = {}
        self._cache_expiry = None


# Shared resolver instance
certificate_resolver = CertificateResolver()
