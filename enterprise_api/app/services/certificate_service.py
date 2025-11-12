"""
Certificate resolution utilities for verification endpoints.

Provides a cached view of organization certificates so verification
requests can synchronously resolve signer public keys.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationCertificateStatus
from app.utils.crypto_utils import extract_public_key_from_certificate


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
    public_key: Ed25519PublicKey
    status: OrganizationCertificateStatus
    certificate_rotated_at: Optional[datetime] = None
    certificate_expiry: Optional[datetime] = None
    cert_chain_pem: Optional[str] = None

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

        if (
            self._ttl > 0
            and self._cache
            and self._cache_expiry
            and self._cache_expiry > datetime.utcnow()
        ):
            return

        async with self._lock:
            if (
                self._ttl > 0
                and self._cache
                and self._cache_expiry
                and self._cache_expiry > datetime.utcnow()
            ):
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
                except Exception:
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
                )

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

    def resolve_public_key(self, signer_id: str) -> Optional[Ed25519PublicKey]:
        """
        Return the Ed25519 public key for the signer, if available and active.

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
