"""
Basic tests for streaming functionality.

Tests WebSocket connection manager and session service.
"""
import pytest
from app.core.websocket_manager import ConnectionManager
from app.services.session_service import SessionService


class TestConnectionManager:
    """Test WebSocket connection manager."""
    
    def test_connection_manager_init(self):
        """Test connection manager initialization."""
        manager = ConnectionManager(max_connections_per_org=10)
        
        assert manager.max_connections_per_org == 10
        assert len(manager.active_connections) == 0
        assert len(manager.org_connections) == 0
    
    def test_get_connection_count(self):
        """Test connection count retrieval."""
        manager = ConnectionManager()
        
        # No connections initially
        assert manager.get_connection_count() == 0
        assert manager.get_connection_count("org_test") == 0


class TestSessionService:
    """Test session management service."""
    
    def test_session_service_init(self):
        """Test session service initialization."""
        service = SessionService(redis_url="redis://localhost:6379/0")
        
        assert service.redis_url == "redis://localhost:6379/0"
        assert service.default_ttl == 3600
    
    def test_session_key_generation(self):
        """Test session key generation."""
        service = SessionService()
        
        key = service._get_session_key("test_session_123")
        assert key == "encypher:session:test_session_123"
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation."""
        service = SessionService()
        
        session_data = await service.create_session(
            organization_id="org_test",
            session_type="websocket",
            metadata={"test": "data"}
        )
        
        assert session_data["organization_id"] == "org_test"
        assert session_data["session_type"] == "websocket"
        assert session_data["status"] == "active"
        assert session_data["chunks_processed"] == 0
        assert "session_id" in session_data
        assert "created_at" in session_data
        assert "expires_at" in session_data
