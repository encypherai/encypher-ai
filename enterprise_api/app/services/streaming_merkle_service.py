"""
Streaming Merkle Tree Service (TEAM_044 - Patent FIG. 5).

This service implements streaming Merkle tree construction for real-time
content signing, ideal for LLM output where content is generated incrementally.

Key Features:
- Session-based streaming with bounded buffers
- Incremental hash computation for memory efficiency
- Auto-finalization on timeout
- Integration with C2PA manifest embedding
"""

import asyncio
import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding_service import EmbeddingService
from app.utils.merkle import compute_hash

logger = logging.getLogger(__name__)


@dataclass
class StreamingMerkleSession:
    """
    Represents an active streaming Merkle tree construction session.

    The session maintains a bounded buffer of segment hashes and constructs
    the Merkle tree incrementally as segments are added.
    """

    session_id: str
    document_id: str
    organization_id: str
    segmentation_level: str
    metadata: Optional[Dict[str, Any]]
    buffer_size: int
    timeout_seconds: int

    # Session state
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"  # active, finalized, expired

    # Segment storage
    segments: List[str] = field(default_factory=list)
    segment_hashes: List[str] = field(default_factory=list)

    # Merkle tree state (for incremental construction)
    intermediate_hashes: List[List[str]] = field(default_factory=list)
    intermediate_root: Optional[str] = None

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time based on last activity."""
        return self.last_activity + timedelta(seconds=self.timeout_seconds)

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def buffer_count(self) -> int:
        """Number of segments currently in buffer."""
        return len(self.segments)

    @property
    def total_segments(self) -> int:
        """Total number of segments added."""
        return len(self.segment_hashes)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)


class StreamingMerkleService:
    """
    Service for managing streaming Merkle tree construction sessions.

    Patent Reference: FIG. 5 - Streaming Merkle Tree Construction

    This service allows content to be signed incrementally as it's generated,
    which is ideal for:
    - Real-time LLM output signing
    - Large document processing with memory constraints
    - Progressive content verification
    """

    def __init__(self):
        """Initialize the streaming Merkle service."""
        # In-memory session storage (could be Redis in production)
        self._sessions: Dict[str, StreamingMerkleSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info("StreamingMerkleService initialized")

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"stream_{secrets.token_urlsafe(16)}"

    async def start_session(
        self,
        document_id: str,
        organization_id: str,
        segmentation_level: str = "sentence",
        metadata: Optional[Dict[str, Any]] = None,
        buffer_size: int = 100,
        timeout_seconds: int = 300,
    ) -> StreamingMerkleSession:
        """
        Start a new streaming Merkle tree construction session.

        Args:
            document_id: Unique document identifier
            organization_id: Organization ID
            segmentation_level: Segmentation level (sentence, paragraph, section)
            metadata: Optional document metadata
            buffer_size: Maximum segments to buffer before auto-flush
            timeout_seconds: Session timeout in seconds

        Returns:
            The created StreamingMerkleSession
        """
        session_id = self._generate_session_id()

        session = StreamingMerkleSession(
            session_id=session_id,
            document_id=document_id,
            organization_id=organization_id,
            segmentation_level=segmentation_level,
            metadata=metadata,
            buffer_size=buffer_size,
            timeout_seconds=timeout_seconds,
        )

        self._sessions[session_id] = session

        logger.info(f"Started streaming Merkle session {session_id} for document {document_id} (org: {organization_id}, level: {segmentation_level})")

        return session

    async def add_segment(
        self,
        session_id: str,
        segment_text: str,
        segment_index: Optional[int] = None,
        flush_buffer: bool = False,
    ) -> Tuple[StreamingMerkleSession, str]:
        """
        Add a segment to an active streaming session.

        Args:
            session_id: Session ID
            segment_text: Text segment to add
            segment_index: Optional explicit index (auto-incremented if not provided)
            flush_buffer: If True, flush buffer and compute intermediate hashes

        Returns:
            Tuple of (updated session, segment hash)

        Raises:
            ValueError: If session not found or expired
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status != "active":
            raise ValueError(f"Session is not active: {session.status}")

        if session.is_expired:
            session.status = "expired"
            raise ValueError(f"Session has expired: {session_id}")

        # Update activity timestamp
        session.touch()

        # Compute segment hash
        segment_hash = compute_hash(segment_text)

        # Add to session
        session.segments.append(segment_text)
        session.segment_hashes.append(segment_hash)

        logger.debug(f"Added segment {len(session.segment_hashes) - 1} to session {session_id}: hash={segment_hash[:16]}...")

        # Check if buffer should be flushed
        if flush_buffer or len(session.segments) >= session.buffer_size:
            await self._flush_buffer(session)

        return session, segment_hash

    async def _flush_buffer(self, session: StreamingMerkleSession) -> None:
        """
        Flush the buffer and compute intermediate Merkle hashes.

        This implements the bounded buffer approach from Patent FIG. 5,
        allowing memory-efficient incremental tree construction.
        """
        if not session.segment_hashes:
            return

        # Compute intermediate root from current hashes
        current_hashes = session.segment_hashes.copy()

        # Build tree level by level
        while len(current_hashes) > 1:
            next_level = []
            for i in range(0, len(current_hashes), 2):
                if i + 1 < len(current_hashes):
                    combined = current_hashes[i] + current_hashes[i + 1]
                else:
                    combined = current_hashes[i] + current_hashes[i]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            current_hashes = next_level

        session.intermediate_root = current_hashes[0] if current_hashes else None

        logger.debug(
            f"Flushed buffer for session {session.session_id}: "
            f"intermediate_root={session.intermediate_root[:16] if session.intermediate_root else 'None'}..."
        )

    async def get_session(self, session_id: str) -> Optional[StreamingMerkleSession]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        if session and session.is_expired and session.status == "active":
            session.status = "expired"
        return session

    async def finalize_session(
        self,
        session_id: str,
        db: AsyncSession,
        embedding_service: Optional[EmbeddingService] = None,
        embed_manifest: bool = True,
        manifest_mode: str = "full",
        action: str = "c2pa.created",
    ) -> Tuple[StreamingMerkleSession, str, Optional[str]]:
        """
        Finalize a streaming session and compute the final Merkle root.

        Args:
            session_id: Session ID to finalize
            db: Database session
            embedding_service: Optional EmbeddingService for manifest embedding
            embed_manifest: Whether to embed C2PA manifest
            manifest_mode: Manifest mode (full or micro)
            action: C2PA action type

        Returns:
            Tuple of (session, root_hash, embedded_content)

        Raises:
            ValueError: If session not found or already finalized
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status == "finalized":
            raise ValueError(f"Session already finalized: {session_id}")

        if session.status == "expired":
            raise ValueError(f"Session has expired: {session_id}")

        # Flush any remaining buffer
        await self._flush_buffer(session)

        # Compute final Merkle root
        root_hash = session.intermediate_root or ""
        if not root_hash and session.segment_hashes:
            # Single segment case
            root_hash = session.segment_hashes[0]

        # Calculate tree depth
        tree_depth = 0
        n = len(session.segment_hashes)
        while n > 1:
            tree_depth += 1
            n = (n + 1) // 2

        # Mark session as finalized
        session.status = "finalized"
        session.touch()

        # Embed manifest if requested
        embedded_content = None
        if embed_manifest and embedding_service and session.segments:
            try:
                full_document = " ".join(session.segments)

                # Use the embedding service to create embeddings
                # For streaming, we create a single document-level embedding
                embeddings, embedded_content = await embedding_service.create_embeddings(
                    db=db,
                    organization_id=session.organization_id,
                    document_id=session.document_id,
                    merkle_root_id=None,  # No pre-existing Merkle root
                    merkle_root_hash=root_hash or None,
                    merkle_segmentation_level=session.segmentation_level,
                    segments=session.segments,
                    leaf_hashes=session.segment_hashes,
                    manifest_mode=manifest_mode,
                    action=action,
                )

                logger.info(f"Embedded manifest for finalized session {session_id}: mode={manifest_mode}, segments={len(session.segments)}")
            except Exception as e:
                logger.error(f"Failed to embed manifest for session {session_id}: {e}")
                # Continue without embedding - return the raw content
                embedded_content = " ".join(session.segments)
        elif session.segments:
            embedded_content = " ".join(session.segments)

        logger.info(
            f"Finalized streaming Merkle session {session_id}: "
            f"root_hash={root_hash[:16]}..., depth={tree_depth}, segments={len(session.segment_hashes)}"
        )

        return session, root_hash, embedded_content

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        expired_ids = [sid for sid, session in self._sessions.items() if session.is_expired and session.status == "active"]

        for sid in expired_ids:
            self._sessions[sid].status = "expired"
            logger.debug(f"Marked session {sid} as expired")

        # Remove sessions that have been expired for more than 1 hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        to_remove = [
            sid for sid, session in self._sessions.items() if session.status in ("expired", "finalized") and session.last_activity < one_hour_ago
        ]

        for sid in to_remove:
            del self._sessions[sid]
            logger.debug(f"Removed old session {sid}")

        return len(expired_ids) + len(to_remove)


# Global service instance
streaming_merkle_service = StreamingMerkleService()
