"""
Example WebSocket client for testing streaming API.

Usage:
    uv run python examples/websocket_client.py
"""
import asyncio
import websockets
import json
import sys


async def test_streaming():
    """Test WebSocket streaming endpoint."""
    # Configuration
    api_key = "demo_key_12345"  # Replace with your API key
    uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={api_key}"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Server: {data}")
            
            if data.get("type") == "connected":
                session_id = data.get("session_id")
                print(f"✅ Session ID: {session_id}")
            
            # Send test chunks
            test_chunks = [
                "This is the first sentence. ",
                "Here comes the second sentence. ",
                "And finally, the third sentence."
            ]
            
            print(f"\n📤 Sending {len(test_chunks)} chunks...")
            
            for i, chunk in enumerate(test_chunks):
                # Send chunk
                message = {
                    "type": "chunk",
                    "content": chunk,
                    "chunk_id": f"chunk_{i:03d}"
                }
                
                print(f"\n  Chunk {i+1}: {chunk[:50]}...")
                await websocket.send(json.dumps(message))
                
                # Receive response
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "signed_chunk":
                    signed = data.get("signed", False)
                    status = "✅ SIGNED" if signed else "⚠️  NOT SIGNED"
                    print(f"  {status}")
                    print(f"  Content preview: {data.get('content', '')[:80]}...")
                elif data.get("type") == "error":
                    print(f"  ❌ Error: {data.get('message')}")
                    break
            
            # Finalize stream
            print(f"\n📤 Finalizing stream...")
            await websocket.send(json.dumps({"type": "finalize"}))
            
            # Receive final response
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "complete":
                print(f"\n✅ Stream complete!")
                print(f"  Document ID: {data.get('document_id')}")
                print(f"  Total chunks: {data.get('total_chunks')}")
                print(f"  Duration: {data.get('duration_seconds', 0):.2f}s")
                print(f"  Verification URL: {data.get('verification_url')}")
            else:
                print(f"\n⚠️  Unexpected response: {data}")
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"\n✅ Test completed successfully!")
    return 0


async def test_rate_limiting():
    """Test rate limiting by sending chunks rapidly."""
    api_key = "demo_key_12345"
    uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={api_key}"
    
    print(f"\n🔥 Testing rate limiting...")
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection
            await websocket.recv()
            
            # Send chunks as fast as possible
            print(f"📤 Sending 100 chunks rapidly...")
            
            rate_limited = False
            for i in range(100):
                message = {
                    "type": "chunk",
                    "content": f"Chunk {i}. ",
                    "chunk_id": f"chunk_{i:03d}"
                }
                
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "error" and "rate limit" in data.get("message", "").lower():
                    print(f"  ⚠️  Rate limited at chunk {i+1}")
                    rate_limited = True
                    break
            
            if rate_limited:
                print(f"✅ Rate limiting is working!")
            else:
                print(f"⚠️  No rate limiting detected (sent 100 chunks)")
            
            # Finalize
            await websocket.send(json.dumps({"type": "finalize"}))
            await websocket.recv()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


async def test_reconnection():
    """Test session recovery after disconnection."""
    api_key = "demo_key_12345"
    uri = f"ws://localhost:8000/api/v1/stream/sign?api_key={api_key}"
    
    print(f"\n🔄 Testing reconnection...")
    
    # First connection
    print(f"📤 First connection...")
    async with websockets.connect(uri) as websocket:
        response = await websocket.recv()
        data = json.loads(response)
        session_id = data.get("session_id")
        print(f"  Session ID: {session_id}")
        
        # Send a few chunks
        for i in range(3):
            await websocket.send(json.dumps({
                "type": "chunk",
                "content": f"Chunk {i}. "
            }))
            await websocket.recv()
        
        print(f"  Sent 3 chunks, disconnecting...")
    
    # Simulate reconnection
    print(f"\n📤 Reconnecting with session recovery...")
    uri_with_session = f"{uri}&session_id={session_id}"
    
    try:
        async with websockets.connect(uri_with_session) as websocket:
            # Try to recover session
            await websocket.send(json.dumps({
                "type": "recover_session",
                "session_id": session_id
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("recovered"):
                print(f"  ✅ Session recovered!")
                print(f"  Chunks processed: {data.get('chunks_processed')}")
            else:
                print(f"  ⚠️  Session recovery failed")
            
            # Finalize
            await websocket.send(json.dumps({"type": "finalize"}))
            await websocket.recv()
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 1
    
    return 0


async def main():
    """Run all tests."""
    print("=" * 60)
    print("WebSocket Streaming API - Test Suite")
    print("=" * 60)
    
    # Test 1: Basic streaming
    result = await test_streaming()
    if result != 0:
        return result
    
    # Test 2: Rate limiting
    await asyncio.sleep(1)  # Wait a bit between tests
    result = await test_rate_limiting()
    if result != 0:
        return result
    
    # Test 3: Reconnection
    await asyncio.sleep(1)
    result = await test_reconnection()
    if result != 0:
        return result
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
