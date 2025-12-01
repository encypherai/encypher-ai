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
from typing import Dict, Optional, Tuple
from uuid import uuid4

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.status_list import (
    StatusListEntry,
    StatusListMetadata,
    RevocationReason,
    BITS_PER_LIST,
    BYTES_PER_LIST,
)
from app.config import settings

logger = logging.getLogger(__name__)


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
        
        list_index = metadata.list_index
        bit_index = metadata.next_bit_index
        
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
        metadata.next_bit_index += 1
        metadata.total_documents += 1
        
        # Check if list is now full
        if metadata.next_bit_index >= BITS_PER_LIST:
            metadata.is_full = True
            logger.info(
                f"Status list {organization_id}/{list_index} is now full "
                f"({BITS_PER_LIST} documents)"
            )
        
        await db.flush()
        
        status_list_url = self._build_status_list_url(organization_id, list_index)
        
        logger.debug(
            f"Allocated status index for doc {document_id}: "
            f"list={list_index}, bit={bit_index}"
        )
        
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
                StatusListMetadata.is_full == False,
            )
            .order_by(StatusListMetadata.list_index.desc())
            .limit(1)
        )
        metadata = result.scalar_one_or_none()
        
        if metadata:
            return metadata
        
        # No available list, create a new one
        # Find the highest list_index for this org
        result = await db.execute(
            select(func.max(StatusListMetadata.list_index))
            .where(StatusListMetadata.organization_id == organization_id)
        )
        max_index = result.scalar()
        new_index = (max_index or -1) + 1
        
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
        
        logger.info(
            f"Created new status list for org {organization_id}: list_index={new_index}"
        )
        
        return metadata
    
    def _build_status_list_url(self, organization_id: str, list_index: int) -> str:
        """Build the canonical URL for a status list."""
        # TEAM_002: Make base URL configurable
        base_url = getattr(settings, 'status_list_base_url', 'https://status.encypherai.com/v1')
        return f"{base_url}/{organization_id}/list/{list_index}"
    
    # -------------------------------------------------------------------------
    # Revocation Status Checking (used during verification)
    # -------------------------------------------------------------------------
    
    async def check_revocation(
        self,
        status_list_url: str,
        bit_index: int,
    ) -> bool:
        """
        Check if a document is revoked.
        
        Uses cached status lists for O(1) lookups.
        
        Args:
            status_list_url: URL of the status list
            bit_index: Bit position in the list
        
        Returns:
            True if revoked, False if active
        """
        try:
            bitstring = await self._get_status_list(status_list_url)
            
            # Check bit at index
            byte_index = bit_index // 8
            bit_position = 7 - (bit_index % 8)  # MSB first per W3C spec
            
            if byte_index >= len(bitstring):
                return False  # Index out of range = not revoked
            
            return bool(bitstring[byte_index] & (1 << bit_position))
            
        except Exception as e:
            logger.warning(f"Failed to check revocation status: {e}")
            # Fail open - if we can't check, assume not revoked
            # This is a policy decision; could also fail closed
            return False
    
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
            select(StatusListEntry.revoked, StatusListEntry.revoked_reason)
            .where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        row = result.first()
        
        if not row:
            return False, None
        
        return row.revoked, row.revoked_reason
    
    async def _get_status_list(self, url: str) -> bytes:
        """
        Fetch and cache a status list.
        
        In production, this fetches from CDN. For now, returns empty bitstring.
        """
        now = time.time()
        
        # Check cache
        if url in self._list_cache:
            data, expires = self._list_cache[url]
            if now < expires:
                return data
        
        # TODO: Implement CDN fetch
        # For now, return empty bitstring (all documents active)
        # This will be replaced with actual HTTP fetch in production
        logger.debug(f"Status list cache miss for {url}, returning empty bitstring")
        bitstring = bytes(BYTES_PER_LIST)
        
        # Cache the result
        self._list_cache[url] = (bitstring, now + self.cache_ttl)
        
        return bitstring
    
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
            select(StatusListEntry)
            .where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise ValueError(f"Document {document_id} not found in status list")
        
        if entry.revoked:
            logger.warning(f"Document {document_id} is already revoked")
            return entry
        
        # Update entry
        entry.revoked = True
        entry.revoked_at = datetime.now(timezone.utc)
        entry.revoked_reason = reason.value
        entry.revoked_reason_detail = reason_detail
        entry.revoked_by = revoked_by
        entry.reinstated_at = None
        entry.reinstated_by = None
        
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
        status_list_url = self._build_status_list_url(organization_id, entry.list_index)
        self.invalidate_cache(status_list_url)
        
        logger.info(
            f"Revoked document {document_id} (org={organization_id}, "
            f"reason={reason.value})"
        )
        
        return entry
    
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
            select(StatusListEntry)
            .where(
                StatusListEntry.organization_id == organization_id,
                StatusListEntry.document_id == document_id,
            )
        )
        entry = result.scalar_one_or_none()
        
        if not entry:
            raise ValueError(f"Document {document_id} not found in status list")
        
        if not entry.revoked:
            logger.warning(f"Document {document_id} is not revoked")
            return entry
        
        # Update entry
        entry.revoked = False
        entry.reinstated_at = datetime.now(timezone.utc)
        entry.reinstated_by = reinstated_by
        
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
        status_list_url = self._build_status_list_url(organization_id, entry.list_index)
        self.invalidate_cache(status_list_url)
        
        logger.info(f"Reinstated document {document_id} (org={organization_id})")
        
        return entry
    
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
        entries = result.all()
        
        # Build bitstring
        bitstring = bytearray(BYTES_PER_LIST)
        
        for bit_index, revoked in entries:
            if revoked:
                byte_index = bit_index // 8
                bit_position = 7 - (bit_index % 8)  # MSB first
                bitstring[byte_index] |= (1 << bit_position)
        
        # Compress and encode
        compressed = gzip.compress(bytes(bitstring), compresslevel=9)
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # Build credential
        status_list_url = self._build_status_list_url(organization_id, list_index)
        issued = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://w3id.org/vc/status-list/2021/v1"
            ],
            "id": status_list_url,
            "type": ["VerifiableCredential", "StatusList2021Credential"],
            "issuer": f"did:web:encypherai.com:orgs:{organization_id}",
            "issued": issued,
            "credentialSubject": {
                "id": f"{status_list_url}#list",
                "type": "StatusList2021",
                "statusPurpose": "revocation",
                "encodedList": encoded
            }
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
            f"Generated status list {organization_id}/{list_index}: "
            f"{len(entries)} entries, {len(compressed)} bytes compressed, "
            f"{duration_ms}ms"
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
            select(
                StatusListMetadata.organization_id,
                StatusListMetadata.list_index
            )
            .where(
                (StatusListMetadata.last_generated_at == None) |
                (StatusListMetadata.last_generated_at < threshold_dt)
            )
        )
        
        return [(row.organization_id, row.list_index) for row in result.all()]


# Shared service instance
status_service = StatusService()
