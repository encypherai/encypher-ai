"""
WebSocket Connection Manager for Streaming API.

Manages WebSocket connections, connection pooling, and session state.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for streaming API.
    
    Features:
    - Connection pooling per organization
    - Connection limits enforcement
    - Active connection tracking
    - Broadcast capabilities
    """
    
    def __init__(self, max_connections_per_org: int = 100):
        """
        Initialize connection manager.
        
        Args:
            max_connections_per_org: Maximum concurrent connections per organization
        """
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
        self.org_connections: Dict[str, Set[str]] = {}
        self.max_connections_per_org = max_connections_per_org
        self._lock = asyncio.Lock()
        
        logger.info(f"ConnectionManager initialized with max {max_connections_per_org} connections per org")
    
    async def connect(
        self, 
        session_id: str, 
        websocket: WebSocket, 
        organization_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Register a new WebSocket connection.
        
        Args:
            session_id: Unique session identifier
            websocket: WebSocket connection
            organization_id: Organization ID
            metadata: Optional connection metadata
            
        Raises:
            ConnectionError: If connection limit exceeded
        """
        async with self._lock:
            # Check organization connection limit
            org_conn_count = len(self.org_connections.get(organization_id, set()))
            if org_conn_count >= self.max_connections_per_org:
                raise ConnectionError(
                    f"Maximum connections exceeded for organization {organization_id}. "
                    f"Limit: {self.max_connections_per_org}"
                )
            
            # Accept WebSocket connection
            await websocket.accept()
            
            # Store connection
            self.active_connections[session_id] = websocket
            self.connection_metadata[session_id] = {
                "organization_id": organization_id,
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }
            
            # Track organization connections
            if organization_id not in self.org_connections:
                self.org_connections[organization_id] = set()
            self.org_connections[organization_id].add(session_id)
            
            logger.info(
                f"WebSocket connected: session={session_id}, org={organization_id}, "
                f"total_connections={len(self.active_connections)}"
            )
    
    async def disconnect(self, session_id: str) -> None:
        """
        Disconnect and cleanup a WebSocket connection.
        
        Args:
            session_id: Session identifier to disconnect
        """
        async with self._lock:
            if session_id in self.active_connections:
                # Get organization ID before cleanup
                org_id = self.connection_metadata.get(session_id, {}).get("organization_id")
                
                # Remove from active connections
                websocket = self.active_connections.pop(session_id)
                self.connection_metadata.pop(session_id, None)
                
                # Remove from organization tracking
                if org_id and org_id in self.org_connections:
                    self.org_connections[org_id].discard(session_id)
                    if not self.org_connections[org_id]:
                        del self.org_connections[org_id]
                
                # Close WebSocket
                try:
                    await websocket.close()
                except Exception as e:
                    logger.warning(f"Error closing WebSocket for session {session_id}: {e}")
                
                logger.info(
                    f"WebSocket disconnected: session={session_id}, "
                    f"remaining_connections={len(self.active_connections)}"
                )
    
    async def send_message(self, session_id: str, message: Dict) -> bool:
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            session_id: Target session identifier
            message: Message dictionary to send (will be JSON serialized)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if session_id not in self.active_connections:
            logger.warning(f"Attempted to send message to non-existent session: {session_id}")
            return False
        
        try:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
            
            # Update last activity
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]["last_activity"] = \
                    datetime.now(timezone.utc).isoformat()
            
            return True
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during send: {session_id}")
            await self.disconnect(session_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to session {session_id}: {e}", exc_info=True)
            return False
    
    async def send_text(self, session_id: str, text: str) -> bool:
        """
        Send raw text to a specific WebSocket connection.
        
        Args:
            session_id: Target session identifier
            text: Text to send
            
        Returns:
            True if text sent successfully, False otherwise
        """
        if session_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[session_id]
            await websocket.send_text(text)
            
            # Update last activity
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]["last_activity"] = \
                    datetime.now(timezone.utc).isoformat()
            
            return True
        except WebSocketDisconnect:
            await self.disconnect(session_id)
            return False
        except Exception as e:
            logger.error(f"Error sending text to session {session_id}: {e}")
            return False
    
    async def broadcast_to_org(self, organization_id: str, message: Dict) -> int:
        """
        Broadcast a message to all connections for an organization.
        
        Args:
            organization_id: Target organization ID
            message: Message to broadcast
            
        Returns:
            Number of successful sends
        """
        if organization_id not in self.org_connections:
            return 0
        
        session_ids = list(self.org_connections[organization_id])
        successful_sends = 0
        
        for session_id in session_ids:
            if await self.send_message(session_id, message):
                successful_sends += 1
        
        return successful_sends
    
    def get_connection(self, session_id: str) -> Optional[WebSocket]:
        """
        Get WebSocket connection by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            WebSocket connection or None if not found
        """
        return self.active_connections.get(session_id)
    
    def get_connection_metadata(self, session_id: str) -> Optional[Dict]:
        """
        Get connection metadata by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Connection metadata or None if not found
        """
        return self.connection_metadata.get(session_id)
    
    def get_connection_count(self, organization_id: Optional[str] = None) -> int:
        """
        Get connection count, optionally filtered by organization.
        
        Args:
            organization_id: Optional organization ID to filter by
            
        Returns:
            Number of active connections
        """
        if organization_id:
            return len(self.org_connections.get(organization_id, set()))
        return len(self.active_connections)
    
    def get_all_sessions(self, organization_id: Optional[str] = None) -> Set[str]:
        """
        Get all active session IDs, optionally filtered by organization.
        
        Args:
            organization_id: Optional organization ID to filter by
            
        Returns:
            Set of session IDs
        """
        if organization_id:
            return self.org_connections.get(organization_id, set()).copy()
        return set(self.active_connections.keys())
    
    async def cleanup_inactive_connections(self, timeout_seconds: int = 300) -> int:
        """
        Cleanup connections that have been inactive for too long.
        
        Args:
            timeout_seconds: Inactivity timeout in seconds
            
        Returns:
            Number of connections cleaned up
        """
        now = datetime.now(timezone.utc)
        sessions_to_cleanup = []
        
        for session_id, metadata in self.connection_metadata.items():
            last_activity = datetime.fromisoformat(metadata["last_activity"])
            inactive_seconds = (now - last_activity).total_seconds()
            
            if inactive_seconds > timeout_seconds:
                sessions_to_cleanup.append(session_id)
        
        for session_id in sessions_to_cleanup:
            await self.disconnect(session_id)
        
        if sessions_to_cleanup:
            logger.info(f"Cleaned up {len(sessions_to_cleanup)} inactive connections")
        
        return len(sessions_to_cleanup)


# Global connection manager instance
connection_manager = ConnectionManager()
