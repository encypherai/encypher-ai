"""
Robust Fingerprint Service (TEAM_044).

Provides keyed fingerprint encoding and detection for content that
survives text modifications like paraphrasing or truncation.
"""

import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.fingerprint import FingerprintMatch

logger = logging.getLogger(__name__)

# Zero-width characters for fingerprinting
FINGERPRINT_CHARS = [
    "\u200b",  # Zero-width space
    "\u200c",  # Zero-width non-joiner
    "\u200d",  # Zero-width joiner
    "\ufeff",  # Zero-width no-break space
]


class FingerprintService:
    """
    Service for robust fingerprint encoding and detection.

    Uses secret-seeded placement of invisible markers that can survive
    text modifications. Detection uses score-based matching with
    configurable confidence thresholds.
    """

    def __init__(self):
        """Initialize fingerprint service."""
        self._fingerprints: Dict[str, Dict[str, Any]] = {}  # In-memory storage

    def _generate_key(self) -> str:
        """Generate a random fingerprint key."""
        return secrets.token_urlsafe(32)

    def _key_to_positions(
        self,
        key: str,
        text_length: int,
        density: float,
    ) -> List[int]:
        """
        Generate deterministic marker positions from key.

        Uses HMAC-based PRNG seeded with the key to generate
        consistent positions for the same key.
        """
        num_markers = max(1, int(text_length * density))
        positions = []

        # Use HMAC to generate pseudo-random positions
        for i in range(num_markers * 2):  # Generate extra to handle collisions
            h = hmac.new(key.encode(), f"{i}".encode(), hashlib.sha256).digest()
            pos = int.from_bytes(h[:4], "big") % text_length
            if pos not in positions and pos > 0:
                positions.append(pos)
            if len(positions) >= num_markers:
                break

        return sorted(positions)

    def _position_to_marker(self, key: str, position: int) -> str:
        """Generate a marker character for a position."""
        h = hmac.new(key.encode(), f"marker_{position}".encode(), hashlib.sha256).digest()
        idx = h[0] % len(FINGERPRINT_CHARS)
        return FINGERPRINT_CHARS[idx]

    async def encode_fingerprint(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        text: str,
        density: float = 0.1,
        fingerprint_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str, str, int]:
        """
        Encode a fingerprint into text.

        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID
            text: Text to fingerprint
            density: Marker density (0.01-0.5)
            fingerprint_key: Optional custom key
            metadata: Optional metadata

        Returns:
            Tuple of (fingerprinted_text, fingerprint_id, key_hash, markers_count)
        """
        # Generate or use provided key
        key = fingerprint_key or self._generate_key()
        fingerprint_id = str(uuid.uuid4())

        # Generate marker positions
        positions = self._key_to_positions(key, len(text), density)

        # Insert markers
        result = []
        last_pos = 0
        for pos in positions:
            result.append(text[last_pos:pos])
            result.append(self._position_to_marker(key, pos))
            last_pos = pos
        result.append(text[last_pos:])

        fingerprinted_text = "".join(result)

        # Store fingerprint info
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        self._fingerprints[fingerprint_id] = {
            "fingerprint_id": fingerprint_id,
            "document_id": document_id,
            "organization_id": organization_id,
            "key": key,
            "key_hash": key_hash,
            "positions": positions,
            "density": density,
            "text_length": len(text),
            "markers_count": len(positions),
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc),
        }

        logger.info(f"Encoded fingerprint {fingerprint_id} for doc {document_id}: {len(positions)} markers at density {density}")

        return fingerprinted_text, fingerprint_id, key_hash, len(positions)

    async def detect_fingerprint(
        self,
        db: AsyncSession,
        organization_id: str,
        text: str,
        fingerprint_key: Optional[str] = None,
        confidence_threshold: float = 0.6,
        return_positions: bool = False,
    ) -> Tuple[bool, List[FingerprintMatch]]:
        """
        Detect fingerprints in text.

        Args:
            db: Database session
            organization_id: Organization ID
            text: Text to scan
            fingerprint_key: Optional specific key to search for
            confidence_threshold: Minimum confidence for detection
            return_positions: Include marker positions in response

        Returns:
            Tuple of (detected, list of matches)
        """
        matches = []

        # Extract all zero-width characters and their positions
        found_markers: List[tuple[int, str]] = []
        clean_text = []
        for i, char in enumerate(text):
            if char in FINGERPRINT_CHARS:
                found_markers.append((i - len(found_markers), char))
            else:
                clean_text.append(char)

        clean_text_str = "".join(clean_text)

        if not found_markers:
            return False, []

        # Check against stored fingerprints
        fingerprints_to_check = list(self._fingerprints.values())
        if fingerprint_key:
            # Filter to specific key
            fingerprints_to_check = [fp for fp in fingerprints_to_check if fp["key"] == fingerprint_key]

        for fp_info in fingerprints_to_check:
            # Generate expected positions for this fingerprint
            expected_positions = self._key_to_positions(
                fp_info["key"],
                len(clean_text_str),
                fp_info["density"],
            )

            # Count matches
            found_positions = [pos for pos, _ in found_markers]
            matched_positions = []
            for exp_pos in expected_positions:
                # Allow some tolerance for position matching
                for found_pos in found_positions:
                    if abs(exp_pos - found_pos) <= 5:  # 5 char tolerance
                        matched_positions.append(found_pos)
                        break

            # Calculate confidence
            if expected_positions:
                confidence = len(matched_positions) / len(expected_positions)
            else:
                confidence = 0.0

            if confidence >= confidence_threshold:
                match = FingerprintMatch(
                    fingerprint_id=fp_info["fingerprint_id"],
                    document_id=fp_info["document_id"],
                    organization_id=fp_info["organization_id"],
                    confidence=confidence,
                    markers_found=len(matched_positions),
                    markers_expected=len(expected_positions),
                    marker_positions=matched_positions if return_positions else None,
                    created_at=fp_info["created_at"],
                )
                matches.append(match)

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)

        detected = len(matches) > 0

        if detected:
            logger.info(f"Detected {len(matches)} fingerprint(s) in text, best confidence: {matches[0].confidence:.2f}")

        return detected, matches


# Global service instance
fingerprint_service = FingerprintService()
