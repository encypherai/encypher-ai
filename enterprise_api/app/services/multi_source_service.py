"""
Multi-Source Hash Table Lookup Service (TEAM_044 - Patent FIG. 8).

Provides lookup of content across multiple sources with linked-list
tracking, chronological ordering, and authority ranking.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, cast

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_reference import ContentReference
from app.schemas.multi_source import SourceRecord
from app.utils.merkle import compute_hash

logger = logging.getLogger(__name__)


class MultiSourceService:
    """
    Service for multi-source hash table lookup.

    Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

    This service:
    1. Looks up content hashes across all registered sources
    2. Returns full linked list of sources
    3. Provides chronological ordering (earliest first)
    4. Supports authority ranking (configurable)
    """

    async def lookup_sources(
        self,
        db: AsyncSession,
        organization_id: str,
        text_segment: str,
        include_all_sources: bool = True,
        order_by: str = "chronological",
        include_authority_score: bool = False,
        max_results: int = 10,
    ) -> Tuple[List[SourceRecord], str, Optional[SourceRecord]]:
        """
        Look up all sources for a text segment.

        Args:
            db: Database session
            organization_id: Organization performing lookup
            text_segment: Text to search for
            include_all_sources: Return all sources (not just first)
            order_by: Ordering method
            include_authority_score: Include authority scores
            max_results: Maximum results to return

        Returns:
            Tuple of (sources list, query hash, original source)
        """
        # Compute hash of the query text
        query_hash = compute_hash(text_segment)

        # Query for all matching content references
        stmt = select(ContentReference).where(ContentReference.leaf_hash == query_hash)

        # Order by creation time for chronological
        if order_by == "chronological":
            stmt = stmt.order_by(ContentReference.created_at.asc())
        else:
            stmt = stmt.order_by(ContentReference.created_at.desc())

        if not include_all_sources:
            stmt = stmt.limit(1)
        else:
            stmt = stmt.limit(max_results)

        result = await db.execute(stmt)
        refs = result.scalars().all()

        if not refs:
            return [], query_hash, None

        # Build source records
        sources = []
        original_source = None

        for idx, ref in enumerate(refs):
            org_id = cast(str, ref.organization_id)
            created_at = cast(datetime, ref.created_at)
            document_id = cast(str, ref.document_id)

            # Get organization name
            org_name = await self._get_organization_name(db, org_id)

            # Calculate authority score if requested
            authority_score = None
            if include_authority_score:
                authority_score = await self._calculate_authority_score(db, org_id, created_at)

            # Determine if this is the original (earliest)
            is_original = idx == 0 and order_by == "chronological"

            # Build linked list references
            previous_id = cast(str, refs[idx - 1].document_id) if idx > 0 else None
            next_id = cast(str, refs[idx + 1].document_id) if idx < len(refs) - 1 else None

            source = SourceRecord(
                document_id=document_id,
                organization_id=org_id,
                organization_name=org_name,
                segment_hash=ref.leaf_hash,
                leaf_index=ref.leaf_index or 0,
                merkle_root_hash=str(ref.merkle_root_id) if ref.merkle_root_id else None,
                created_at=created_at,
                signed_at=created_at,  # Use created_at as signed_at
                confidence=1.0,  # Exact hash match
                authority_score=authority_score,
                is_original=is_original,
                previous_source_id=previous_id,
                next_source_id=next_id,
                metadata=ref.embedding_metadata,
            )
            sources.append(source)

            if is_original:
                original_source = source

        # Re-sort by authority if requested
        if order_by == "authority" and include_authority_score:
            sources.sort(key=lambda s: s.authority_score or 0, reverse=True)
        elif order_by == "confidence":
            sources.sort(key=lambda s: s.confidence, reverse=True)

        logger.info(f"Multi-source lookup for hash {query_hash[:16]}...: found {len(sources)} sources")

        return sources, query_hash, original_source

    async def _get_organization_name(
        self,
        db: AsyncSession,
        organization_id: str,
    ) -> Optional[str]:
        """Get organization name from ID."""
        try:
            result = await db.execute(
                text("SELECT name FROM organizations WHERE id = :org_id"),
                {"org_id": organization_id},
            )
            row = result.fetchone()
            return row[0] if row else None
        except Exception:
            return None

    async def _calculate_authority_score(
        self,
        db: AsyncSession,
        organization_id: str,
        created_at: datetime,
    ) -> float:
        """
        Calculate authority score for a source.

        Factors:
        - Organization verification status
        - Organization tier
        - Age of content (older = more authoritative for originals)
        - Number of documents from organization
        """
        base_score = 0.5

        try:
            # Get organization info
            result = await db.execute(
                text("""
                    SELECT tier, is_verified, 
                           (SELECT COUNT(*) FROM content_references WHERE organization_id = :org_id) as doc_count
                    FROM organizations 
                    WHERE id = :org_id
                """),
                {"org_id": organization_id},
            )
            row = result.fetchone()

            if row:
                tier, is_verified, doc_count = row

                # TEAM_145: Tier bonus (consolidated to free/enterprise/strategic_partner)
                tier_scores = {"free": 0, "starter": 0, "professional": 0, "business": 0, "enterprise": 0.3, "strategic_partner": 0.3}
                base_score += tier_scores.get(tier.lower() if tier else "free", 0)

                # Verification bonus
                if is_verified:
                    base_score += 0.15

                # Document count bonus (capped)
                doc_bonus = min(0.1, (doc_count or 0) / 1000)
                base_score += doc_bonus

            # Age bonus (older content gets slight boost for being "original")
            age_days = (datetime.now(timezone.utc) - created_at).days
            age_bonus = min(0.05, age_days / 365 * 0.05)
            base_score += age_bonus

        except Exception as e:
            logger.warning(f"Error calculating authority score: {e}")

        return min(1.0, base_score)


# Global service instance
multi_source_service = MultiSourceService()
