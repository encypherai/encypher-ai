"""Perceptual hash (pHash) based image attribution service."""
import logging
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article_image import ArticleImage

logger = logging.getLogger(__name__)

MAX_CROSS_ORG_CANDIDATES = 10_000  # Safety limit for cross-org search


@dataclass
class ImageAttributionMatch:
    image_id: str
    document_id: str
    organization_id: str
    filename: Optional[str]
    hamming_distance: int
    similarity_score: float  # 1.0 - (hamming_distance / 64)
    signed_hash: str
    created_at: str


def hamming_distance(a: int, b: int) -> int:
    """Count differing bits between two integers (XOR then popcount)."""
    return bin(a ^ b).count("1")


async def search_by_phash(
    *,
    phash_query: int,
    threshold_bits: int = 10,
    scope: str = "org",
    org_id: Optional[str] = None,
    db: AsyncSession,
) -> List[ImageAttributionMatch]:
    """
    Find images with similar perceptual hash.

    Args:
        phash_query: 64-bit pHash as signed int64 (from compute_phash())
        threshold_bits: Maximum Hamming distance to consider a match (default 10)
        scope: "org" (org-scoped, all tiers) or "all" (cross-org, Enterprise only)
        org_id: Required when scope="org"
        db: Content DB session

    Returns:
        List of matches sorted by similarity (closest first)
    """
    # Build query
    stmt = select(
        ArticleImage.image_id,
        ArticleImage.document_id,
        ArticleImage.organization_id,
        ArticleImage.filename,
        ArticleImage.phash,
        ArticleImage.signed_hash,
        ArticleImage.created_at,
    ).where(ArticleImage.phash.is_not(None))

    if scope == "org":
        if org_id is None:
            raise ValueError("org_id required for scope='org'")
        stmt = stmt.where(ArticleImage.organization_id == org_id)
    else:
        # Cross-org: limit candidates for safety
        stmt = stmt.limit(MAX_CROSS_ORG_CANDIDATES)

    rows = (await db.execute(stmt)).all()

    # Compute Hamming distances in Python
    matches = []
    for row in rows:
        if row.phash is None:
            continue
        dist = hamming_distance(phash_query, row.phash)
        if dist <= threshold_bits:
            matches.append(
                ImageAttributionMatch(
                    image_id=row.image_id,
                    document_id=row.document_id,
                    organization_id=row.organization_id,
                    filename=row.filename,
                    hamming_distance=dist,
                    similarity_score=round(1.0 - (dist / 64.0), 4),
                    signed_hash=row.signed_hash,
                    created_at=row.created_at.isoformat() if row.created_at else "",
                )
            )

    # Sort by closest match first
    matches.sort(key=lambda m: m.hamming_distance)
    return matches
