"""
Fuzzy fingerprint service for similarity search and indexing.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fuzzy_fingerprint import FuzzyFingerprint
from app.models.merkle import MerkleRoot
from app.schemas.fuzzy_fingerprint import FuzzyFingerprintConfig, FuzzySearchConfig
from app.utils.merkle import compute_leaf_hash
from app.utils.segmentation import HierarchicalSegmenter
from app.utils.segmentation.default import normalize_for_hashing

logger = logging.getLogger(__name__)

DEFAULT_FINGERPRINT_BITS = 64
DEFAULT_BUCKET_BITS = 16


class FuzzyFingerprintService:
    """Service for indexing and searching fuzzy fingerprints."""

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        normalized = normalize_for_hashing(text, lowercase=True, normalize_unicode_chars=True)
        return [token for token in re.split(r"\W+", normalized) if token]

    @staticmethod
    def _simhash(tokens: Iterable[str], bits: int) -> int:
        if bits <= 0:
            return 0
        counts = [0] * bits
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            value = int.from_bytes(digest, "big")
            for bit in range(bits):
                counts[bit] += 1 if (value >> bit) & 1 else -1
        fingerprint = 0
        for bit, count in enumerate(counts):
            if count >= 0:
                fingerprint |= 1 << bit
        return fingerprint

    @staticmethod
    def _bucket(fingerprint: int, bits: int, bucket_bits: int) -> int:
        if bits <= 0:
            return 0
        bucket_bits = min(bucket_bits, bits)
        if bucket_bits <= 0:
            return 0
        shift = max(bits - bucket_bits, 0)
        return fingerprint >> shift

    @staticmethod
    def _similarity(left: int, right: int, bits: int) -> float:
        if bits <= 0:
            return 0.0
        if bits < DEFAULT_FINGERPRINT_BITS:
            mask = (1 << bits) - 1
            left &= mask
            right &= mask
        distance = (left ^ right).bit_count()
        return 1.0 - (distance / bits)

    def _fingerprint_segment(self, text: str, bits: int, bucket_bits: int) -> Tuple[int, int]:
        tokens = self._tokenize(text)
        fingerprint = self._simhash(tokens, bits)
        bucket = self._bucket(fingerprint, bits, bucket_bits)
        return fingerprint, bucket

    async def index_document(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        text: str,
        config: FuzzyFingerprintConfig,
        merkle_roots: Optional[Dict[str, MerkleRoot]] = None,
    ) -> Dict[str, Any]:
        """Index a document's segments with fuzzy fingerprints."""
        if not config.enabled:
            return {"indexed_segments": 0, "levels": {}}

        levels = list(config.levels)
        if config.include_document_fingerprint and "document" not in levels:
            levels.append("document")

        bucket_bits = config.bucket_bits
        bits = config.fingerprint_bits
        if bucket_bits > bits:
            bucket_bits = bits

        segmenter = HierarchicalSegmenter(text, include_words=False)
        fingerprints: List[FuzzyFingerprint] = []
        indexed_levels: Dict[str, int] = {}

        for level in levels:
            if level == "document":
                segments = [text]
            else:
                segments = segmenter.get_segments(level)
            if not segments:
                continue

            await db.execute(
                delete(FuzzyFingerprint).where(
                    FuzzyFingerprint.organization_id == organization_id,
                    FuzzyFingerprint.document_id == document_id,
                    FuzzyFingerprint.segmentation_level == level,
                )
            )

            merkle_root = merkle_roots.get(level) if merkle_roots else None
            for index, segment in enumerate(segments):
                fingerprint_value, bucket = self._fingerprint_segment(segment, bits, bucket_bits)
                fingerprints.append(
                    FuzzyFingerprint(
                        organization_id=organization_id,
                        document_id=document_id,
                        merkle_root_id=merkle_root.id if merkle_root else None,
                        segmentation_level=level,
                        segment_index=index,
                        leaf_hash=compute_leaf_hash(segment),
                        fingerprint_type=config.algorithm,
                        fingerprint_value=fingerprint_value,
                        fingerprint_bits=bits,
                        fingerprint_bucket=bucket,
                        text_preview=None,
                    )
                )
            indexed_levels[level] = len(segments)

        if fingerprints:
            db.add_all(fingerprints)
        await db.commit()

        total_indexed = sum(indexed_levels.values())
        logger.info(
            "Indexed %s fuzzy fingerprints for document %s (levels=%s)",
            total_indexed,
            document_id,
            list(indexed_levels.keys()),
        )
        return {"indexed_segments": total_indexed, "levels": indexed_levels}

    async def search(
        self,
        db: AsyncSession,
        organization_id: str,
        text: str,
        config: FuzzySearchConfig,
        search_scope: str = "organization",
    ) -> Dict[str, Any]:
        """Search for fuzzy fingerprint matches."""
        start = time.perf_counter()
        levels = config.levels or ["sentence", "paragraph"]
        similarity_threshold = config.similarity_threshold
        max_candidates = config.max_candidates

        bucket_bits = DEFAULT_BUCKET_BITS
        bits = DEFAULT_FINGERPRINT_BITS

        segmenter = HierarchicalSegmenter(text, include_words=False)
        matches: Dict[str, Dict[str, Any]] = {}
        root_ids: set[str] = set()
        query_previews: Dict[Tuple[str, int], str] = {}

        for level in levels:
            if level == "document":
                segments = [text]
            else:
                segments = segmenter.get_segments(level)
            if not segments:
                continue

            query_fingerprints: List[Tuple[int, int]] = []
            buckets: set[int] = set()
            for index, segment in enumerate(segments):
                fingerprint_value, bucket = self._fingerprint_segment(segment, bits, bucket_bits)
                query_fingerprints.append((fingerprint_value, bits))
                buckets.add(bucket)
                query_previews[(level, index)] = segment[:200]

            if not buckets:
                continue

            statement = select(FuzzyFingerprint).where(
                FuzzyFingerprint.segmentation_level == level,
                FuzzyFingerprint.fingerprint_bucket.in_(buckets),
            )
            if search_scope == "organization":
                statement = statement.where(FuzzyFingerprint.organization_id == organization_id)

            result = await db.execute(statement)
            candidates = result.scalars().all()
            for candidate in candidates:
                candidate_bits = int(candidate.fingerprint_bits or bits)
                for fingerprint_value, query_bits in query_fingerprints:
                    bits_to_use = min(candidate_bits, query_bits)
                    similarity = self._similarity(
                        fingerprint_value,
                        int(candidate.fingerprint_value),
                        bits_to_use,
                    )
                    if similarity < similarity_threshold:
                        continue
                    key = f"{candidate.document_id}:{candidate.segmentation_level}:{candidate.segment_index}"
                    existing = matches.get(key)
                    if existing and existing["similarity"] >= similarity:
                        continue
                    segmentation_level = cast(str, candidate.segmentation_level)
                    segment_index = int(cast(int, candidate.segment_index or 0))
                    match_payload = {
                        "document_id": candidate.document_id,
                        "organization_id": candidate.organization_id,
                        "segmentation_level": segmentation_level,
                        "segment_index": candidate.segment_index,
                        "similarity": round(similarity, 4),
                        "text_preview": query_previews.get((segmentation_level, segment_index)),
                        "leaf_hash": candidate.leaf_hash,
                        "merkle_root_id": str(candidate.merkle_root_id) if candidate.merkle_root_id else None,
                    }
                    if candidate.merkle_root_id:
                        root_ids.add(str(candidate.merkle_root_id))
                    matches[key] = match_payload

        merkle_roots: Dict[str, MerkleRoot] = {}
        if root_ids:
            root_result = await db.execute(select(MerkleRoot).where(MerkleRoot.id.in_(list(root_ids))))
            merkle_roots = {str(root.id): root for root in root_result.scalars().all()}

        results = sorted(matches.values(), key=lambda item: item["similarity"], reverse=True)
        results = results[:max_candidates]

        if config.include_merkle_proof:
            for match in results:
                root = merkle_roots.get(match.get("merkle_root_id") or "")
                if root:
                    match["merkle_proof"] = {
                        "root_hash": root.root_hash,
                        "leaf_hash": match.get("leaf_hash"),
                        "proof_path": [],
                    }

        duration_ms = int((time.perf_counter() - start) * 1000)
        return {
            "matches_found": len(results),
            "matches": results,
            "processing_time_ms": duration_ms,
        }


fuzzy_fingerprint_service = FuzzyFingerprintService()
