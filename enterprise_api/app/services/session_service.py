"""
Session Management Service for Streaming API.

Manages streaming sessions with Redis for state persistence and recovery.
"""
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """
    Manages streaming sessions with Redis backend.
    
    Features:
    - Session creation and lifecycle management
    - State persistence for reconnection
    - Session expiration
    - Buffer state management
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize session service.
        
        Args:
            redis_url: Redis connection URL (defaults to settings)
        """
        self.redis_url = redis_url or getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        self.redis_client: Optional[redis.Redis] = None
        self.session_prefix = "encypher:session:"
        self.stream_prefix = "encypher:stream:run:"
        self.default_ttl = 3600  # 1 hour default TTL
        self.stream_ttl = 3600
        self._stream_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"SessionService initialized with Redis URL: {self.redis_url}")
    
    async def connect(self) -> None:
        """Establish Redis connection."""
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
                # Fallback to in-memory mode
                logger.warning("Running in in-memory mode (no Redis)")
                self.redis_client = None
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis connection closed")
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self.session_prefix}{session_id}"
    
    async def create_session(
        self,
        organization_id: str,
        session_type: str = "websocket",
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new streaming session.
        
        Args:
            organization_id: Organization ID
            session_type: Type of session (websocket, sse, kafka)
            metadata: Optional session metadata
            ttl_seconds: Session TTL in seconds (default: 1 hour)
            
        Returns:
            Session data dictionary
        """
        session_id = f"session_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        ttl = ttl_seconds or self.default_ttl
        
        session_data = {
            "session_id": session_id,
            "organization_id": organization_id,
            "session_type": session_type,
            "created_at": now.isoformat(),
            "last_activity": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl)).isoformat(),
            "chunks_processed": 0,
            "buffer_state": {
                "accumulated_text": "",
                "is_accumulating": False,
                "has_encoded": False
            },
            "metadata": metadata or {},
            "status": "active"
        }
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    self._get_session_key(session_id),
                    ttl,
                    json.dumps(session_data)
                )
                logger.info(f"Session created: {session_id} for org {organization_id}")
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}", exc_info=True)
        
        return session_data
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found/expired
        """
        if not self.redis_client:
            logger.warning("Redis not available, cannot retrieve session")
            return None
        
        try:
            session_key = self._get_session_key(session_id)
            session_json = await self.redis_client.get(session_key)
            
            if session_json:
                session_data = json.loads(session_json)
                
                # Check expiration
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                if datetime.now(timezone.utc) > expires_at:
                    logger.info(f"Session expired: {session_id}")
                    await self.delete_session(session_id)
                    return None
                
                return session_data
            
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}", exc_info=True)
            return None
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any],
        extend_ttl: bool = True
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
            extend_ttl: Whether to extend session TTL
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                logger.warning(f"Cannot update non-existent session: {session_id}")
                return False
            
            # Update fields
            session_data.update(updates)
            session_data["last_activity"] = datetime.now(timezone.utc).isoformat()
            
            # Calculate TTL
            if extend_ttl:
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
                ttl = max(ttl, self.default_ttl)  # Extend if needed
            else:
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
            
            # Store updated session
            await self.redis_client.setex(
                self._get_session_key(session_id),
                ttl,
                json.dumps(session_data)
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}", exc_info=True)
            return False
    
    async def update_buffer_state(
        self,
        session_id: str,
        accumulated_text: str,
        is_accumulating: bool,
        has_encoded: bool
    ) -> bool:
        """
        Update session buffer state.
        
        Args:
            session_id: Session identifier
            accumulated_text: Accumulated text buffer
            is_accumulating: Whether currently accumulating
            has_encoded: Whether metadata has been encoded
            
        Returns:
            True if update successful
        """
        return await self.update_session(
            session_id,
            {
                "buffer_state": {
                    "accumulated_text": accumulated_text,
                    "is_accumulating": is_accumulating,
                    "has_encoded": has_encoded
                }
            }
        )
    
    async def increment_chunks_processed(self, session_id: str) -> bool:
        """
        Increment chunks processed counter.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if increment successful
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        return await self.update_session(
            session_id,
            {"chunks_processed": session_data["chunks_processed"] + 1}
        )
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deletion successful
        """
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(self._get_session_key(session_id))
            logger.info(f"Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}", exc_info=True)
            return False
    
    async def close_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Close a session and return final stats.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Final session data or None
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return None
        
        # Update status
        session_data["status"] = "closed"
        session_data["closed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Calculate duration
        created_at = datetime.fromisoformat(session_data["created_at"])
        duration = (datetime.now(timezone.utc) - created_at).total_seconds()
        session_data["duration_seconds"] = duration
        
        # Delete from Redis
        await self.delete_session(session_id)
        
        logger.info(
            f"Session closed: {session_id}, "
            f"chunks_processed={session_data['chunks_processed']}, "
            f"duration={duration:.2f}s"
        )
        
        return session_data
    
    async def recover_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Recover a session for reconnection.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data if recoverable, None otherwise
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            logger.warning(f"Cannot recover non-existent session: {session_id}")
            return None
        
        if session_data["status"] != "active":
            logger.warning(f"Cannot recover closed session: {session_id}")
            return None
        
        # Extend TTL on recovery
        await self.update_session(session_id, {}, extend_ttl=True)
        
        logger.info(f"Session recovered: {session_id}")
        return session_data
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Cleanup expired sessions (Redis handles this automatically).
        
        Returns:
            Number of sessions cleaned up (always 0 for Redis)
        """
        # Redis automatically handles expiration via TTL
        # This method is here for API compatibility
        return 0

    def _stream_key(self, run_id: str) -> str:
        return f"{self.stream_prefix}{run_id}"

    async def save_stream_state(
        self,
        run_id: str,
        state: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Persist streaming run state."""

        state = dict(state)
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    self._stream_key(run_id),
                    ttl_seconds or self.stream_ttl,
                    json.dumps(state),
                )
                return
            except Exception as exc:  # pragma: no cover - redis errors
                logger.warning("Failed to store stream state: %s", exc)
        self._stream_cache[run_id] = state

    async def get_stream_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve streaming run state."""

        if self.redis_client:
            try:
                value = await self.redis_client.get(self._stream_key(run_id))
                if value:
                    return json.loads(value)
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to read stream state: %s", exc)
        return self._stream_cache.get(run_id)

    async def delete_stream_state(self, run_id: str) -> None:
        """Delete run state once delivery completes."""

        if self.redis_client:
            try:
                await self.redis_client.delete(self._stream_key(run_id))
            except Exception:  # pragma: no cover
                logger.debug("Failed to delete stream state for %s", run_id)
        self._stream_cache.pop(run_id, None)


# Global session service instance
session_service = SessionService()
