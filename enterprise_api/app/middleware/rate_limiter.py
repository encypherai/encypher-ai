"""
Rate Limiting Middleware for Streaming API.

Implements rate limiting for WebSocket connections and streaming chunks.
"""
import logging
import time
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class StreamingRateLimiter:
    """
    Rate limiter for streaming connections and chunks.
    
    Features:
    - Connection rate limiting per organization
    - Chunk rate limiting per session
    - Sliding window algorithm
    - Configurable limits per tier
    """
    
    # Rate limits by tier (connections per minute, chunks per second)
    TIER_LIMITS = {
        "basic": {"connections_per_minute": 5, "chunks_per_second": 10},
        "professional": {"connections_per_minute": 20, "chunks_per_second": 100},
        "enterprise": {"connections_per_minute": 100, "chunks_per_second": 1000},
        "demo": {"connections_per_minute": 10, "chunks_per_second": 50},
    }
    
    def __init__(self):
        """Initialize rate limiter."""
        # Track connection attempts: {org_id: [(timestamp, count), ...]}
        self.connection_attempts: Dict[str, list] = defaultdict(list)
        
        # Track chunk processing: {session_id: [(timestamp, count), ...]}
        self.chunk_attempts: Dict[str, list] = defaultdict(list)
        
        logger.info("StreamingRateLimiter initialized")
    
    def _cleanup_old_entries(self, entries: list, window_seconds: int) -> list:
        """
        Remove entries older than the time window.
        
        Args:
            entries: List of (timestamp, count) tuples
            window_seconds: Time window in seconds
            
        Returns:
            Cleaned list of entries
        """
        cutoff = time.time() - window_seconds
        return [(ts, count) for ts, count in entries if ts > cutoff]
    
    def check_connection_rate(self, organization_id: str, tier: str) -> tuple[bool, Optional[str]]:
        """
        Check if organization can create a new connection.
        
        Args:
            organization_id: Organization ID
            tier: Organization tier
            
        Returns:
            Tuple of (allowed, error_message)
        """
        # Get rate limits for tier
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["basic"])
        max_connections = limits["connections_per_minute"]
        window_seconds = 60
        
        # Cleanup old entries
        self.connection_attempts[organization_id] = self._cleanup_old_entries(
            self.connection_attempts[organization_id],
            window_seconds
        )
        
        # Count connections in window
        connection_count = sum(count for _, count in self.connection_attempts[organization_id])
        
        if connection_count >= max_connections:
            logger.warning(
                f"Connection rate limit exceeded for org {organization_id}: "
                f"{connection_count}/{max_connections} in {window_seconds}s"
            )
            return False, f"Connection rate limit exceeded: {max_connections} connections per minute"
        
        # Record this connection attempt
        self.connection_attempts[organization_id].append((time.time(), 1))
        
        return True, None
    
    def check_chunk_rate(self, session_id: str, tier: str) -> tuple[bool, Optional[str]]:
        """
        Check if session can process another chunk.
        
        Args:
            session_id: Session ID
            tier: Organization tier
            
        Returns:
            Tuple of (allowed, error_message)
        """
        # Get rate limits for tier
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["basic"])
        max_chunks = limits["chunks_per_second"]
        window_seconds = 1
        
        # Cleanup old entries
        self.chunk_attempts[session_id] = self._cleanup_old_entries(
            self.chunk_attempts[session_id],
            window_seconds
        )
        
        # Count chunks in window
        chunk_count = sum(count for _, count in self.chunk_attempts[session_id])
        
        if chunk_count >= max_chunks:
            logger.warning(
                f"Chunk rate limit exceeded for session {session_id}: "
                f"{chunk_count}/{max_chunks} in {window_seconds}s"
            )
            return False, f"Chunk rate limit exceeded: {max_chunks} chunks per second"
        
        # Record this chunk
        self.chunk_attempts[session_id].append((time.time(), 1))
        
        return True, None
    
    def reset_session(self, session_id: str) -> None:
        """
        Reset rate limiting for a session.
        
        Args:
            session_id: Session ID to reset
        """
        if session_id in self.chunk_attempts:
            del self.chunk_attempts[session_id]
            logger.debug(f"Reset rate limiting for session {session_id}")
    
    def reset_organization(self, organization_id: str) -> None:
        """
        Reset rate limiting for an organization.
        
        Args:
            organization_id: Organization ID to reset
        """
        if organization_id in self.connection_attempts:
            del self.connection_attempts[organization_id]
            logger.debug(f"Reset rate limiting for org {organization_id}")
    
    def get_stats(self, organization_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict:
        """
        Get rate limiting statistics.
        
        Args:
            organization_id: Optional organization ID
            session_id: Optional session ID
            
        Returns:
            Statistics dictionary
        """
        stats = {}
        
        if organization_id:
            # Cleanup and count
            self.connection_attempts[organization_id] = self._cleanup_old_entries(
                self.connection_attempts[organization_id],
                60
            )
            connection_count = sum(count for _, count in self.connection_attempts[organization_id])
            stats["connections_last_minute"] = connection_count
        
        if session_id:
            # Cleanup and count
            self.chunk_attempts[session_id] = self._cleanup_old_entries(
                self.chunk_attempts[session_id],
                1
            )
            chunk_count = sum(count for _, count in self.chunk_attempts[session_id])
            stats["chunks_last_second"] = chunk_count
        
        return stats


# Global rate limiter instance
streaming_rate_limiter = StreamingRateLimiter()
