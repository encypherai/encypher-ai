"""
Streaming Service for Real-Time Content Signing.

Integrates with encypher_enterprise SDK for streaming content signing.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.session_service import session_service
from app.utils.crypto_utils import decrypt_private_key

logger = logging.getLogger(__name__)


class StreamingService:
    """
    Service for processing streaming content and signing chunks.

    Integrates with:
    - SessionService for state management
    - encypher-ai StreamingHandler for signing
    - Organization key management
    """

    def __init__(self):
        """Initialize streaming service."""
        self.session_service = session_service
        logger.info("StreamingService initialized")

    async def create_session(
        self,
        organization_id: str,
        session_type: str = "websocket",
        metadata: Optional[Dict[str, Any]] = None,
        signing_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new streaming session.

        Args:
            organization_id: Organization ID
            session_type: Type of session (websocket, sse, kafka)
            metadata: Optional session metadata
            signing_options: Optional signing configuration

        Returns:
            Session data with session_id and configuration
        """
        # Merge signing options into metadata
        full_metadata = metadata or {}
        if signing_options:
            full_metadata["signing_options"] = signing_options

        session_data = await self.session_service.create_session(organization_id=organization_id, session_type=session_type, metadata=full_metadata)

        return {
            "success": True,
            "session_id": session_data["session_id"],
            "session_type": session_data["session_type"],
            "created_at": session_data["created_at"],
            "expires_at": session_data["expires_at"],
            "signing_options": signing_options or {},
        }

    async def process_chunk(
        self, chunk: str, session_id: str, organization_id: str, private_key_encrypted: bytes, chunk_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a streaming chunk and sign if needed.

        Args:
            chunk: Text chunk to process
            session_id: Session identifier
            organization_id: Organization ID
            private_key_encrypted: Encrypted private key
            chunk_id: Optional chunk identifier

        Returns:
            Processing result with signed text if applicable
        """
        # Get session state
        session_data = await self.session_service.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found or expired: {session_id}")

        # Verify organization
        if session_data["organization_id"] != organization_id:
            raise ValueError("Organization mismatch for session")

        # Decrypt private key
        try:
            private_key = decrypt_private_key(private_key_encrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt private key: {e}")
            raise ValueError("Failed to decrypt signing key")

        # Get signing options
        signing_options = session_data.get("metadata", {}).get("signing_options", {})

        # Import StreamingHandler from encypher-ai
        try:
            from encypher.streaming.handlers import StreamingHandler
        except ImportError:
            logger.error("encypher-ai package not available")
            raise ValueError("Streaming handler not available")

        # Initialize or retrieve handler state
        session_data.get("buffer_state", {})

        # For now, we'll process each chunk independently
        # TODO: Implement stateful handler that persists across chunks
        handler = StreamingHandler(
            private_key=private_key,
            signer_id=organization_id,
            custom_metadata=signing_options.get("custom_metadata", {}),
            encode_first_chunk_only=signing_options.get("encode_first_chunk_only", True),
        )

        # Process chunk
        try:
            processed_chunk = handler.process_chunk(chunk)

            # Update session state
            await self.session_service.increment_chunks_processed(session_id)
            await self.session_service.update_buffer_state(
                session_id, accumulated_text=handler.accumulated_text, is_accumulating=handler.is_accumulating, has_encoded=handler.has_encoded
            )

            return {
                "type": "signed_chunk",
                "chunk_id": chunk_id,
                "content": processed_chunk,
                "signed": handler.has_encoded,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error processing chunk: {e}", exc_info=True)
            raise ValueError(f"Failed to process chunk: {str(e)}")

    async def finalize_stream(self, session_id: str, organization_id: str, private_key_encrypted: bytes) -> Dict[str, Any]:
        """
        Finalize a streaming session.

        Args:
            session_id: Session identifier
            organization_id: Organization ID
            private_key_encrypted: Encrypted private key

        Returns:
            Finalization result with document ID and stats
        """
        # Get session state
        session_data = await self.session_service.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")

        # Verify organization
        if session_data["organization_id"] != organization_id:
            raise ValueError("Organization mismatch for session")

        # Close session and get final stats
        final_stats = await self.session_service.close_session(session_id)

        if not final_stats:
            raise ValueError("Failed to close session")

        # Generate document ID (in production, this would be stored in DB)
        document_id = f"doc_{session_id.split('_')[1]}"

        return {
            "type": "complete",
            "success": True,
            "session_id": session_id,
            "document_id": document_id,
            "total_chunks": final_stats["chunks_processed"],
            "duration_seconds": final_stats.get("duration_seconds", 0),
            "verification_url": f"https://encypher.com/verify/{document_id}",
        }

    async def recover_session(self, session_id: str) -> Dict[str, Any]:
        """
        Recover a session for reconnection.

        Args:
            session_id: Session identifier

        Returns:
            Recovery result with session state
        """
        session_data = await self.session_service.recover_session(session_id)

        if not session_data:
            raise ValueError(f"Cannot recover session: {session_id}")

        return {
            "recovered": True,
            "session_id": session_id,
            "chunks_processed": session_data["chunks_processed"],
            "buffer_state": session_data["buffer_state"],
            "last_activity": session_data["last_activity"],
        }

    async def disconnect_session(self, session_id: str) -> bool:
        """
        Mark session as disconnected (but don't delete for recovery).

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        return await self.session_service.update_session(session_id, {"status": "disconnected"})


# Global streaming service instance
streaming_service = StreamingService()
