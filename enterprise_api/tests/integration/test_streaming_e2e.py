"""
End-to-End Integration Tests for Streaming API.

Tests complete WebSocket flows with real connections.
"""
import pytest
import asyncio
import json
from httpx import AsyncClient
import websockets

from app.main import app
from app.services.session_service import session_service
from app.middleware.rate_limiter import streaming_rate_limiter


@pytest.fixture
async def async_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def setup_redis():
    """Setup Redis connection for tests."""
    await session_service.connect()
    yield
    await session_service.disconnect()


@pytest.fixture
def demo_api_key():
    """Demo API key for testing."""
    return "demo_key_12345"


class TestWebSocketBasicFlow:
    """Test basic WebSocket streaming flow."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, demo_api_key):
        """Test WebSocket connection establishment."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            # Should receive connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "connected"
            assert "session_id" in data
            assert data["session_id"].startswith("session_")
    
    @pytest.mark.asyncio
    async def test_chunk_processing(self, demo_api_key):
        """Test processing streaming chunks."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            await websocket.recv()
            
            # Send chunk
            await websocket.send(json.dumps({
                "type": "chunk",
                "content": "This is a test chunk. ",
                "chunk_id": "chunk_001"
            }))
            
            # Receive signed chunk
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "signed_chunk"
            assert data["chunk_id"] == "chunk_001"
            assert "content" in data
            assert data["signed"] is True
    
    @pytest.mark.asyncio
    async def test_stream_finalization(self, demo_api_key):
        """Test stream finalization."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            response = await websocket.recv()
            session_data = json.loads(response)
            session_id = session_data["session_id"]
            
            # Send multiple chunks
            chunks = [
                "First sentence. ",
                "Second sentence. ",
                "Third sentence."
            ]
            
            for i, chunk in enumerate(chunks):
                await websocket.send(json.dumps({
                    "type": "chunk",
                    "content": chunk,
                    "chunk_id": f"chunk_{i:03d}"
                }))
                await websocket.recv()  # Receive response
            
            # Finalize
            await websocket.send(json.dumps({"type": "finalize"}))
            
            # Receive completion
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "complete"
            assert data["success"] is True
            assert data["session_id"] == session_id
            assert "document_id" in data
            assert data["total_chunks"] == 3
            assert "duration_seconds" in data


class TestWebSocketAuthentication:
    """Test WebSocket authentication."""
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test connection without API key."""
        uri = "ws://localhost:8000/api/v1/stream/sign"
        
        with pytest.raises(websockets.exceptions.WebSocketException):
            async with websockets.connect(uri) as websocket:
                await websocket.recv()
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test connection with invalid API key."""
        uri = "ws://localhost:8000/api/v1/stream/sign?api_key=invalid_key"
        
        with pytest.raises(websockets.exceptions.WebSocketException):
            async with websockets.connect(uri) as websocket:
                await websocket.recv()


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_chunk_rate_limiting(self, demo_api_key):
        """Test chunk rate limiting."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            await websocket.recv()
            
            # Send chunks rapidly to trigger rate limit
            rate_limited = False
            for i in range(100):
                await websocket.send(json.dumps({
                    "type": "chunk",
                    "content": f"Chunk {i}. ",
                    "chunk_id": f"chunk_{i:03d}"
                }))
                
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "error" and "rate limit" in data.get("message", "").lower():
                    rate_limited = True
                    break
            
            # Should hit rate limit for demo tier (50 chunks/second)
            assert rate_limited, "Rate limiting should be triggered"
            
            # Cleanup
            await websocket.send(json.dumps({"type": "finalize"}))
            await websocket.recv()
    
    @pytest.mark.asyncio
    async def test_connection_rate_limiting(self, demo_api_key):
        """Test connection rate limiting."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        # Demo tier allows 10 connections per minute
        connections = []
        
        try:
            # Try to create 15 connections rapidly
            for i in range(15):
                try:
                    ws = await websockets.connect(uri)
                    connections.append(ws)
                    await ws.recv()  # Wait for connection confirmation
                except websockets.exceptions.WebSocketException as e:
                    # Should hit rate limit
                    assert "rate limit" in str(e).lower() or "exceeded" in str(e).lower()
                    break
            
            # Should not be able to create all 15 connections
            assert len(connections) < 15, "Connection rate limiting should be triggered"
        
        finally:
            # Cleanup all connections
            for ws in connections:
                try:
                    await ws.close()
                except:
                    pass


class TestSessionRecovery:
    """Test session recovery functionality."""
    
    @pytest.mark.asyncio
    async def test_session_recovery(self, demo_api_key, setup_redis):
        """Test session recovery after disconnection."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        # First connection
        session_id = None
        async with websockets.connect(uri) as websocket:
            # Get session ID
            response = await websocket.recv()
            data = json.loads(response)
            session_id = data["session_id"]
            
            # Send a few chunks
            for i in range(3):
                await websocket.send(json.dumps({
                    "type": "chunk",
                    "content": f"Chunk {i}. "
                }))
                await websocket.recv()
        
        # Reconnect and recover
        async with websockets.connect(uri) as websocket:
            await websocket.recv()  # Connection confirmation
            
            # Try to recover session
            await websocket.send(json.dumps({
                "type": "recover_session",
                "session_id": session_id
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data.get("recovered") is True
            assert data.get("chunks_processed") == 3
            
            # Finalize
            await websocket.send(json.dumps({"type": "finalize"}))
            await websocket.recv()


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_message_type(self, demo_api_key):
        """Test handling of invalid message type."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            await websocket.recv()  # Connection confirmation
            
            # Send invalid message type
            await websocket.send(json.dumps({
                "type": "invalid_type",
                "content": "test"
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "error"
            assert "unknown" in data["message"].lower() or "invalid" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, demo_api_key):
        """Test handling of invalid JSON."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            await websocket.recv()  # Connection confirmation
            
            # Send invalid JSON
            await websocket.send("not valid json")
            
            response = await websocket.recv()
            data = json.loads(response)
            
            assert data["type"] == "error"
            assert "json" in data["message"].lower()


class TestSessionManagementEndpoints:
    """Test session management REST endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_session_endpoint(self, async_client):
        """Test session creation endpoint."""
        # Note: This requires proper authentication setup
        # For now, this is a placeholder for when auth is fully integrated
        pass
    
    @pytest.mark.asyncio
    async def test_close_session_endpoint(self, async_client):
        """Test session closure endpoint."""
        # Note: This requires proper authentication setup
        # For now, this is a placeholder for when auth is fully integrated
        pass


class TestConcurrentConnections:
    """Test concurrent connection handling."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_connections(self, demo_api_key):
        """Test handling multiple concurrent connections."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async def create_and_use_connection(conn_id: int):
            """Create connection and send chunks."""
            async with websockets.connect(uri) as websocket:
                await websocket.recv()  # Connection confirmation
                
                # Send a few chunks
                for i in range(5):
                    await websocket.send(json.dumps({
                        "type": "chunk",
                        "content": f"Connection {conn_id}, Chunk {i}. "
                    }))
                    await websocket.recv()
                
                # Finalize
                await websocket.send(json.dumps({"type": "finalize"}))
                await websocket.recv()
        
        # Create 5 concurrent connections
        tasks = [create_and_use_connection(i) for i in range(5)]
        await asyncio.gather(*tasks)
        
        # All should complete successfully


class TestStreamingPerformance:
    """Test streaming performance benchmarks."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_throughput(self, demo_api_key):
        """Test chunk processing throughput."""
        uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={demo_api_key}"
        
        async with websockets.connect(uri) as websocket:
            await websocket.recv()  # Connection confirmation
            
            import time
            start_time = time.time()
            num_chunks = 50  # Limited by rate limiting
            
            # Send chunks
            for i in range(num_chunks):
                await websocket.send(json.dumps({
                    "type": "chunk",
                    "content": f"Performance test chunk {i}. "
                }))
                
                response = await websocket.recv()
                data = json.loads(response)
                
                # Stop if rate limited
                if data.get("type") == "error":
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Finalize
            await websocket.send(json.dumps({"type": "finalize"}))
            await websocket.recv()
            
            # Calculate throughput
            throughput = num_chunks / duration
            print(f"\nThroughput: {throughput:.2f} chunks/second")
            print(f"Duration: {duration:.2f} seconds")
            
            # Should process at least 10 chunks per second
            assert throughput >= 10, f"Throughput {throughput:.2f} is below minimum"


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test."""
    yield
    
    # Reset rate limiters
    streaming_rate_limiter.connection_attempts.clear()
    streaming_rate_limiter.chunk_attempts.clear()
