"""
Status Service for Bitstring Status Lists.

Implements W3C StatusList2021 for per-document revocation at internet scale.
Provides:
- Status index allocation during signing
- Revocation status checking during verification
- Bitstring generation for CDN upload

TEAM_002: Core service for document revocation system.
"""

import base64
import gzip
import hashlib
import logging
import time
from datetime import datetime, timezone
from inspect import isawaitable
from urllib.parse import urlparse
from typing import Any, Dict, Optional, Tuple, cast
from uuid import uuid4

import httpx
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.status_list import (
    BITS_PER_LIST,
    BYTES_PER_LIST,
    RevocationReason,
    StatusListEntry,
    StatusListMetadata,
)

logger = logging.getLogger(__name__)


async def _await_if_needed(value):
    if isawaitable(value):
        return await value
    return value


class StatusService:
    """
    Service for managing document revocation status via bitstring status lists.

    Supports 10+ billion documents with O(1) status lookups.
    """

    def __init__(self, cache_ttl_seconds: int = 300):
        """
        Initialize status service.

        Args:
            cache_ttl_seconds: TTL for cached status lists (default 5 minutes)
        """
        self.cache_ttl = cache_ttl_seconds
        self._list_cache: Dict[str, Tuple[bytes, float]] = {}

        # TEAM_056: Basic SSRF hardening - only allow fetching from these hosts.
        # TEAM_056: Intentionally strict; expand only with explicit security review.
        self._allowed_status_list_hosts = {"status.encypherai.com"}

    # -------------------------------------------------------------------------
    # Status Allocation (used during signing)
    # -------------------------------------------------------------------------

    async def allocate_status_index(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
    ) -> Tuple[int, int, str]:
        """
        Allocate a status list position for a new document.

        This is called during document signing to reserve a bit position
        in the organization's status list.

        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID being signed

        Returns:
            Tuple of (list_index, bit_index, status_list_url)

        Raises:
            ValueError: If allocation fails
        """
        # Find or create the current (non-full) list for this org
        metadata = await self._get_or_create_current_list(db, organization_id)
        metadata_any = cast(Any, metadata)

        list_index = int(metadata_any.list_index)
        bit_index = int(metadata_any.next_bit_index)

        # Create the status entry
        entry = StatusListEntry(
            organization_id=organization_id,
            list_index=list_index,
            bit_index=bit_index,
            document_id=document_id,
            revoked=False,
        )
        db.add(entry)

        # Increment the allocation pointer
        metadata_any.next_bit_index = int(metadata_any.next_bit_index) + 1
        metadata_any.total_documents = int(metadata_any.total_documents) + 1

        # Check if list is now full
        if int(metadata_any.next_bit_index) >= BITS_PER_LIST:
            metadata_any.is_full = True
            logger.info(f"Status list {organization_id}/{list_index} is now full ({BITS_PER_LIST} documents)")

        await db.flush()

        status_list_url = self._build_status_list_url(organization_id, list_index)

        logger.debug(f"Allocated status index for doc {document_id}: list={list_index}, bit={bit_index}")

        return list_index, bit_index, status_list_url

    async def _get_or_create_current_list(
        self,
        db: AsyncSession,
        organization_id: str,
    ) -> StatusListMetadata:
        """
        Get the current (non-full) status list for an organization.
        Creates a new list if none exists or all are full.
        """
        # Find the latest non-full list
        result = await db.execute(
            select(StatusListMetadata)
            .where(
                StatusListMetadata.organization_id == organization_id,
                StatusListMetadata.is_full.is_(False),
            )
            .order_by(StatusListMetadata.list_index.desc())
            .limit(1)
        )
        metadata = await _await_if_needed(result.scalar_one_or_none())

        if metadata:
            return cast(StatusListMetadata, metadata)

        # No available list, create a new one
        # Find the highest list_index for this org
        result = await db.execute(select(func.max(StatusListMetadata.list_index)).where(StatusListMetadata.organization_id == organization_id))
        max_index = await _await_if_needed(result.scalar())
        max_index_value = cast(Optional[int], max_index)
        new_index = (max_index_value or -1) + 1

        metadata = StatusListMetadata(
            id=uuid4(),
            organization_id=organization_id,
            list_index=new_index,
            next_bit_index=0,
            is_full=False,
            current_version=0,
            total_documents=0,
            revoked_count=0,
        )
        db.add(metadata)
        await db.flush()

        logger.info(f"Created new status list for org {organization_id}: list_index={new_index}")

        return metadata

    def _build_status_list_url(self, organization_id: str, list_index: int) -> str:
        """Build the canonical URL for a status list."""
        # TEAM_002: Make base URL configurable
        base_url = getattr(settings, "status_list_base_url", "https://status.encypherai.com/v1")
        return f"{base_url}/{organization_id}/list/{list_index}"

    # -------------------------------------------------------------------------
    # Revocation Status Checking (used during verification)
    # -------------------------------------------------------------------------

    async def check_revocation(
        self,
        status_list_url: str,
        bit_index: int,
    ) -> Tuple[Optional[bool], Optional[str]]:
        """
        Check if a document is revoked.

        Uses cached status lists for O(1) lookups.

        Args:
            status_list_url: URL of the status list
            bit_index: Bit position in the list

        Returns:
            Tuple of (is_revoked, error).
            - is_revoked=True/False when status could be determined.
            - is_revoked=None when status could not be determined.
        """
        try:
            bitstring = await self._get_status_list(status_list_url)

            # Check bit at index
            byte_index = bit_index // 8
            bit_position = 7 - (bit_index % 8)  # MSB first per W3C spec

            if byte_index >= len(bitstring):
                return False, None  # Index out of range = not revoked

            return bool(bitstring[byte_index] & (1 << bit_position)), None

        except Exception as e:
            logger.warning(f"Failed to check revocation status: {e}")
            return None, str(e)

    async def check_revocation_from_db(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check revocation status directly from database.

        Use this for authoritative checks (e.g., in revocation API).
        For verification, prefer check_revocation() with cached lists.

        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID

        Returns:
            Tuple of (is_revoked, revocation_reason)
        """
        result = await db.execute(
            select(StatusListEntry.revoked, StatusListEntry.revoked_reason).where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        row = await _await_if_needed(result.first())

        if not row:
            return False, None

        return bool(row.revoked), cast(Optional[str], row.revoked_reason)

    async def _get_status_list(self, url: str) -> bytes:
        """
        Fetch and cache a status list.

        Fetches a W3C StatusList2021Credential JSON-LD and decodes the compressed
        `credentialSubject.encodedList` bitstring.
        """
        now = time.time()

        # Check cache
        if url in self._list_cache:
            data, expires = self._list_cache[url]
            if now < expires:
                return data

        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Untrusted status list url")

        host = parsed.hostname
        if host not in self._allowed_status_list_hosts:
            raise ValueError("Untrusted status list url")

        logger.debug("Status list cache miss for %s, fetching", url)

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            payload = resp.json()

        credential_subject = payload.get("credentialSubject") if isinstance(payload, dict) else None
        if not isinstance(credential_subject, dict):
            raise ValueError("Invalid status list credential")

        encoded_list = credential_subject.get("encodedList")
        if not isinstance(encoded_list, str) or not encoded_list.strip():
            raise ValueError("Invalid status list credential")

        try:
            compressed = base64.b64decode(encoded_list, validate=True)
            bitstring = gzip.decompress(compressed)
        except Exception as exc:
            raise ValueError(f"Invalid status list encoding: {exc}") from exc

        if len(bitstring) != BYTES_PER_LIST:
            raise ValueError("Invalid status list length")

        # Cache the result
        self._list_cache[url] = (bytes(bitstring), now + self.cache_ttl)
        return bytes(bitstring)

    def invalidate_cache(self, url: Optional[str] = None) -> None:
        """
        Invalidate cached status lists.

        Args:
            url: Specific URL to invalidate, or None for all
        """
        if url:
            self._list_cache.pop(url, None)
        else:
            self._list_cache.clear()

    # -------------------------------------------------------------------------
    # Revocation Management
    # -------------------------------------------------------------------------

    async def revoke_document(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        reason: RevocationReason,
        reason_detail: Optional[str] = None,
        revoked_by: Optional[str] = None,
    ) -> StatusListEntry:
        """
        Revoke a document.

        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID to revoke
            reason: Revocation reason code
            reason_detail: Optional detailed explanation
            revoked_by: User/API key performing revocation

        Returns:
            Updated StatusListEntry

        Raises:
            ValueError: If document not found
        """
        result = await db.execute(
            select(StatusListEntry).where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        entry = await _await_if_needed(result.scalar_one_or_none())

        if not entry:
            raise ValueError(f"Document {document_id} not found in status list")

        entry_any = cast(Any, entry)
        if entry_any.revoked:
            logger.warning(f"Document {document_id} is already revoked")
            return cast(StatusListEntry, entry)

        # Update entry
        entry_any.revoked = True
        entry_any.revoked_at = datetime.now(timezone.utc)
        entry_any.revoked_reason = reason.value
        entry_any.revoked_reason_detail = reason_detail
        entry_any.revoked_by = revoked_by
        entry_any.reinstated_at = None
        entry_any.reinstated_by = None

        # Update metadata revoked count
        await db.execute(
            update(StatusListMetadata)
            .where(
                StatusListMetadata.organization_id == organization_id,
                StatusListMetadata.list_index == entry.list_index,
            )
            .values(revoked_count=StatusListMetadata.revoked_count + 1)
        )

        await db.flush()

        # Invalidate cache for this list
        status_list_url = self._build_status_list_url(organization_id, int(entry_any.list_index))
        self.invalidate_cache(status_list_url)

        logger.info(f"Revoked document {document_id} (org={organization_id}, reason={reason.value})")

        return cast(StatusListEntry, entry)

    async def reinstate_document(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        reinstated_by: Optional[str] = None,
    ) -> StatusListEntry:
        """
        Reinstate a previously revoked document.

        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID to reinstate
            reinstated_by: User/API key performing reinstatement

        Returns:
            Updated StatusListEntry

        Raises:
            ValueError: If document not found or not revoked
        """
        result = await db.execute(
            select(StatusListEntry).where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        entry = await _await_if_needed(result.scalar_one_or_none())

        if not entry:
            raise ValueError(f"Document {document_id} not found in status list")

        entry_any = cast(Any, entry)
        if not entry_any.revoked:
            logger.warning(f"Document {document_id} is not revoked")
            return cast(StatusListEntry, entry)

        # Update entry
        entry_any.revoked = False
        entry_any.reinstated_at = datetime.now(timezone.utc)
        entry_any.reinstated_by = reinstated_by

        # Update metadata revoked count
        await db.execute(
            update(StatusListMetadata)
            .where(
                StatusListMetadata.organization_id == organization_id,
                StatusListMetadata.list_index == entry.list_index,
            )
            .values(revoked_count=StatusListMetadata.revoked_count - 1)
        )

        await db.flush()

        # Invalidate cache for this list
        status_list_url = self._build_status_list_url(organization_id, int(entry_any.list_index))
        self.invalidate_cache(status_list_url)

        logger.info(f"Reinstated document {document_id} (org={organization_id})")

        return cast(StatusListEntry, entry)

    # -------------------------------------------------------------------------
    # Bitstring Generation
    # -------------------------------------------------------------------------

    async def generate_status_list(
        self,
        db: AsyncSession,
        organization_id: str,
        list_index: int,
    ) -> Dict:
        """
        Generate a W3C StatusList2021 credential for a status list.

        This creates the JSON structure that will be uploaded to CDN.

        Args:
            db: Database session
            organization_id: Organization ID
            list_index: List index to generate

        Returns:
            StatusList2021Credential as dict
        """
        start_time = time.perf_counter()

        # Fetch all entries for this list
        result = await db.execute(
            select(StatusListEntry.bit_index, StatusListEntry.revoked)
            .where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.list_index == list_index,
            )
            .order_by(StatusListEntry.bit_index)
        )
        entries = await _await_if_needed(result.all())

        # Build bitstring
        bitstring = bytearray(BYTES_PER_LIST)

        for bit_index, revoked in entries:
            if revoked:
                byte_index = bit_index // 8
                bit_position = 7 - (bit_index % 8)  # MSB first
                bitstring[byte_index] |= 1 << bit_position

        # Compress and encode
        compressed = gzip.compress(bytes(bitstring), compresslevel=9)
        encoded = base64.b64encode(compressed).decode("ascii")

        # Build credential
        status_list_url = self._build_status_list_url(organization_id, list_index)
        issued = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        credential = {
            "@context": ["https://www.w3.org/2018/credentials/v1", "https://w3id.org/vc/status-list/2021/v1"],
            "id": status_list_url,
            "type": ["VerifiableCredential", "StatusList2021Credential"],
            "issuer": f"did:web:encypherai.com:orgs:{organization_id}",
            "issued": issued,
            "credentialSubject": {"id": f"{status_list_url}#list", "type": "StatusList2021", "statusPurpose": "revocation", "encodedList": encoded},
        }

        # Calculate ETag
        etag = hashlib.sha256(encoded.encode()).hexdigest()[:16]

        # Update metadata
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        await db.execute(
            update(StatusListMetadata)
            .where(
                StatusListMetadata.organization_id == organization_id,
                StatusListMetadata.list_index == list_index,
            )
            .values(
                current_version=StatusListMetadata.current_version + 1,
                last_generated_at=datetime.now(timezone.utc),
                generation_duration_ms=duration_ms,
                cdn_url=status_list_url,
                cdn_etag=etag,
            )
        )

        await db.flush()

        logger.info(
            f"Generated status list {organization_id}/{list_index}: {len(entries)} entries, {len(compressed)} bytes compressed, {duration_ms}ms"
        )

        return credential

    async def get_lists_needing_regeneration(
        self,
        db: AsyncSession,
        stale_threshold_seconds: int = 300,
    ) -> list:
        """
        Find status lists that need regeneration.

        A list needs regeneration if:
        - It has never been generated, OR
        - It was generated more than stale_threshold_seconds ago

        Args:
            db: Database session
            stale_threshold_seconds: How old before considered stale

        Returns:
            List of (organization_id, list_index) tuples
        """
        threshold = datetime.now(timezone.utc).timestamp() - stale_threshold_seconds
        threshold_dt = datetime.fromtimestamp(threshold, tz=timezone.utc)

        result = await db.execute(
            select(StatusListMetadata.organization_id, StatusListMetadata.list_index).where(
                (StatusListMetadata.last_generated_at.is_(None)) | (StatusListMetadata.last_generated_at < threshold_dt)
            )
        )

        rows = await _await_if_needed(result.all())
        return [(row.organization_id, row.list_index) for row in rows]


# Shared service instance
status_service = StatusService()
