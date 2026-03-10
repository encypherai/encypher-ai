"""CDN Provenance Service.

Manages registration and lookup of CDN-tracked images with perceptual hash
and SHA-256 based provenance continuity.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cdn_image_record import CdnImageRecord
from app.utils.image_utils import compute_phash, compute_sha256

logger = logging.getLogger(__name__)


def _hamming_distance(a: int, b: int) -> int:
    """Compute Hamming distance between two signed int64 pHash values.

    Handles signed int64 by masking to unsigned 64-bit before XOR.
    """
    xor = (a & 0xFFFFFFFFFFFFFFFF) ^ (b & 0xFFFFFFFFFFFFFFFF)
    return bin(xor).count("1")


class CdnProvenanceService:
    """Service for registering and looking up CDN images by provenance."""

    @staticmethod
    async def register_image(
        db: AsyncSession,
        org_id: str,
        image_bytes: bytes,
        mime_type: str,
        manifest_data: Optional[dict] = None,
        original_url: Optional[str] = None,
    ) -> CdnImageRecord:
        """Register an image for CDN provenance tracking.

        Computes pHash and SHA-256 from the provided bytes. Checks for an
        existing record by SHA-256 to be idempotent (same bytes → same record).

        Args:
            db: Async database session.
            org_id: Organization identifier.
            image_bytes: Raw image bytes.
            mime_type: MIME type of the image (e.g. "image/jpeg").
            manifest_data: Optional C2PA manifest dict to store.
            original_url: Optional canonical URL of the original image.

        Returns:
            The newly created (or existing) CdnImageRecord.
        """
        sha256 = compute_sha256(image_bytes)
        phash = compute_phash(image_bytes)

        # Idempotency: return existing record if SHA-256 matches
        result = await db.execute(
            select(CdnImageRecord).where(
                CdnImageRecord.organization_id == org_id,
                CdnImageRecord.content_sha256 == sha256,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            logger.debug("cdn_provenance: idempotent register for org=%s sha256=%s", org_id, sha256[:20])
            return existing

        record = CdnImageRecord(
            organization_id=org_id,
            original_url=original_url,
            content_sha256=sha256,
            phash=phash if phash != 0 else None,
            manifest_store=manifest_data,
            is_variant=False,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)

        logger.info(
            "cdn_provenance: registered image org=%s record_id=%s phash=%s",
            org_id,
            record.id,
            phash,
        )
        return record

    @staticmethod
    async def lookup_by_phash(
        db: AsyncSession,
        org_id: str,
        image_bytes: bytes,
        threshold: int = 8,
    ) -> Optional[tuple[CdnImageRecord, int]]:
        """Look up a registered image by perceptual hash similarity.

        Computes the pHash of the query image and finds the closest stored
        record within the given Hamming distance threshold.

        Args:
            db: Async database session.
            org_id: Organization identifier.
            image_bytes: Raw image bytes to search for.
            threshold: Maximum Hamming distance to consider a match (default 8).

        Returns:
            (best_match_record, hamming_distance) if a match is found within
            the threshold, or None if no match is found.
        """
        query_phash = compute_phash(image_bytes)
        if query_phash == 0:
            logger.debug("cdn_provenance: pHash computation returned 0, skipping lookup")
            return None

        # Load all records with non-null phash for this org (limit 10000)
        result = await db.execute(
            select(CdnImageRecord)
            .where(
                CdnImageRecord.organization_id == org_id,
                CdnImageRecord.phash.isnot(None),
            )
            .limit(10000)
        )
        records = result.scalars().all()

        best_record: Optional[CdnImageRecord] = None
        best_distance = threshold + 1

        for record in records:
            dist = _hamming_distance(query_phash, record.phash)
            if dist < best_distance:
                best_distance = dist
                best_record = record

        if best_record is not None and best_distance <= threshold:
            logger.debug(
                "cdn_provenance: phash match org=%s record_id=%s distance=%d",
                org_id,
                best_record.id,
                best_distance,
            )
            return (best_record, best_distance)

        return None

    @staticmethod
    async def pre_register_variants(
        db: AsyncSession,
        parent_record: CdnImageRecord,
        transform_descriptions: list[str],
    ) -> list[CdnImageRecord]:
        """Pre-register expected CDN derivative variants for an image.

        Creates placeholder variant records so that CDN-reprocessed images
        (resized, re-encoded, etc.) can be looked up by their parent's manifest.

        Args:
            db: Async database session.
            parent_record: The original CdnImageRecord.
            transform_descriptions: List of transform strings e.g. ["resize:800x600", "webp"].

        Returns:
            List of newly created variant CdnImageRecord objects.
        """
        variants: list[CdnImageRecord] = []
        for transform in transform_descriptions:
            variant = CdnImageRecord(
                organization_id=parent_record.organization_id,
                original_url=parent_record.original_url,
                is_variant=True,
                parent_record_id=parent_record.id,
                transform_description=transform,
                # No bytes computed for pre-registered variants
                content_sha256=None,
                phash=None,
                manifest_store=None,
            )
            db.add(variant)
            variants.append(variant)

        await db.flush()
        for v in variants:
            await db.refresh(v)

        logger.info(
            "cdn_provenance: pre-registered %d variants for parent_record_id=%s",
            len(variants),
            parent_record.id,
        )
        return variants
