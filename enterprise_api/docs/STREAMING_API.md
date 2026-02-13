# Streaming API Documentation

**Status:** Phase 1 Implementation (Complete)  
**Version:** 1.0.0-preview  
**Last Updated:** 2025-10-30

---

## Overview

The Streaming API provides real-time content signing capabilities for streaming LLM outputs, chat applications, and event-driven architectures. Built on WebSocket and Server-Sent Events (SSE) protocols with Redis-backed session management.

---

## Features

### Phase 1 (Current) ✅
- ✅ WebSocket connection management
- ✅ Session management with Redis
- ✅ Connection pooling per organization
- ✅ Real-time chunk signing
- ✅ Session recovery on reconnection
- ✅ Basic authentication support

### Phase 2 (Planned)
- ⏳ Kafka producer/consumer integration
- ⏳ Message queue support
- ⏳ Advanced monitoring

### Phase 3 (Planned)
- ✅ OpenAI-compatible streaming endpoint (`POST /api/v1/chat/completions` with `stream=true`)
- ⏳ LangChain integration
- ⏳ LlamaIndex integration

---

## Architecture

```
Client (WebSocket)
    ↓
ConnectionManager
    ↓
StreamingService → SessionService (Redis)
    ↓
encypher-ai StreamingHandler
    ↓
Signed Content
```

---

## API Endpoints

### 1. Create Streaming Session

**POST** `/api/v1/sign/stream/sessions`

Create a new streaming session.

**Request:**
```json
{
  "session_type": "websocket",
  "metadata": {
    "title": "Chat Session"
  },
  "signing_options": {
    "encode_first_chunk_only": true,
    "custom_metadata": {}
  }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "session_abc123",
  "session_type": "websocket",
  "created_at": "2025-10-30T15:00:00Z",
  "expires_at": "2025-10-30T16:00:00Z",
  "signing_options": {}
}
```

### 2. WebSocket Streaming

**WS** `/api/v1/sign/stream?api_key=YOUR_API_KEY`

Real-time content signing via WebSocket.

**Optional Chat Wrapper:** `WS /api/v1/chat/stream` (same protocol; optimized for chat clients)

**Client → Server Messages:**

```json
// Send chunk
{
  "type": "chunk",
  "content": "This is a streaming chunk. ",
  "chunk_id": "chunk_001"
}

// Finalize stream
{
  "type": "finalize"
}

// Recover session
{
  "type": "recover_session",
  "session_id": "session_abc123"
}
```

**Server → Client Messages:**

```json
// Connection confirmed
{
  "type": "connected",
  "session_id": "session_abc123"
}

// Signed chunk
{
  "type": "signed_chunk",
  "chunk_id": "chunk_001",
  "content": "signed:This is a streaming chunk. ",
  "signed": true,
  "session_id": "session_abc123",
  "timestamp": "2025-10-30T15:00:00Z"
}

// Stream complete
{
  "type": "complete",
  "success": true,
  "session_id": "session_abc123",
  "document_id": "doc_xyz789",
  "total_chunks": 42,
  "duration_seconds": 125.5,
  "verification_url": "https://encypherai.com/verify/doc_xyz789"
}

// Error
{
  "type": "error",
  "message": "Error description"
}
```

### 3. Close Session

**POST** `/api/v1/sign/stream/sessions/{session_id}/close`

Close a streaming session and get final statistics.

**Response:**
```json
{
  "type": "complete",
  "success": true,
  "session_id": "session_abc123",
  "document_id": "doc_xyz789",
  "total_chunks": 42,
  "duration_seconds": 125.5,
  "verification_url": "https://encypherai.com/verify/doc_xyz789"
}
```

### 4. Server-Sent Events (SSE)

**GET** `/api/v1/sign/stream/sessions/{session_id}/events?api_key=YOUR_API_KEY`

Unidirectional event streaming via SSE.

**Response Stream:**
```
event: connected
data: {"session_id": "session_abc123"}

:heartbeat

event: chunk
data: {"content": "Signed chunk...", "chunk_id": "001"}

event: complete
data: {"document_id": "doc_123", "status": "signed"}
```

### 5. Streaming Statistics

**GET** `/api/v1/sign/stream/stats`

Get streaming statistics for your organization.

**Response:**
```json
{
  "success": true,
  "organization_id": "org_xyz",
  "active_connections": 5,
  "max_connections": 100
}
```

### 6. OpenAI-Compatible Chat Completions (SSE)

**POST** `/api/v1/chat/completions`

Provide `stream=true` and `sign_response=true` to receive OpenAI-compatible SSE chunks with Encypher signing metadata.

---

## Usage Examples

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def stream_content():
    uri = "ws://localhost:8000/api/v1/sign/stream?api_key=YOUR_KEY"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        response = await websocket.recv()
        print(f"Connected: {response}")
        
        # Send chunks
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
            
            # Receive signed chunk
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Signed: {data['signed']}")
        
        # Finalize
        await websocket.send(json.dumps({"type": "finalize"}))
        final = await websocket.recv()
        print(f"Complete: {final}")

asyncio.run(stream_content())
```

### JavaScript WebSocket Client

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/sign/stream?api_key=YOUR_KEY');

ws.onopen = () => {
    console.log('Connected');
    
    // Send chunk
    ws.send(JSON.stringify({
        type: 'chunk',
        content: 'This is a test chunk. ',
        chunk_id: 'chunk_001'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    if (data.type === 'signed_chunk') {
        console.log('Signed content:', data.content);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

---

## Configuration

### Environment Variables

```bash
# Redis for session management
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/encypher

# Encryption keys
KEY_ENCRYPTION_KEY=your_hex_key
ENCRYPTION_NONCE=your_hex_nonce

# SSL.com
SSL_COM_API_KEY=your_ssl_com_key
```

### Connection Limits

| Tier | Max Concurrent Connections | Chunks/Second |
|------|---------------------------|---------------|
| Professional | 10 | 100 |
| Enterprise | 100 | 1,000 |
| Enterprise+ | 1,000+ | 10,000+ |

---

## Session Management

### Session Lifecycle

1. **Create Session** - Initialize with `POST /sign/stream/sessions`
2. **Connect** - Establish WebSocket connection
3. **Stream** - Send chunks and receive signed content
4. **Finalize** - Close stream with `{"type": "finalize"}`
5. **Cleanup** - Session auto-expires after TTL (default: 1 hour)

### Session Recovery

If connection drops, reconnect and send:

```json
{
  "type": "recover_session",
  "session_id": "session_abc123"
}
```

The session state (buffer, chunks processed) will be restored.

---

## Error Handling

### Common Errors

**Session Not Found:**
```json
{
  "type": "error",
  "message": "Session not found or expired: session_abc123"
}
```

**Connection Limit Exceeded:**
```json
{
  "type": "error",
  "message": "Maximum connections exceeded for organization. Limit: 100"
}
```

**Invalid JSON:**
```json
{
  "type": "error",
  "message": "Invalid JSON"
}
```

---

## Testing

### Run Tests

```bash
# Unit tests
uv run pytest tests/test_streaming_basic.py -v

# Integration tests (requires Redis)
uv run pytest tests/integration/test_streaming_e2e.py -v
```

### Manual Testing with wscat

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c "ws://localhost:8000/api/v1/sign/stream?api_key=test"

# Send message
{"type": "chunk", "content": "Test chunk. "}
```

---

## Performance

### Benchmarks (Target)

- Connection establishment: <50ms
- Chunk signing latency: <30ms (P95)
- Throughput: 10,000 chunks/second per instance
- Concurrent connections: 10,000+ per instance

---

## Security

### Authentication

- API key required in query parameter or header
- Per-organization connection limits
- Session-level access control

### Data Security

- TLS 1.3 for all WebSocket connections
- Redis encryption at rest
- No plaintext credentials in logs

---

## Monitoring

### Metrics

- Active connections per organization
- Chunks processed per session
- Session duration
- Error rates

### Logging

All streaming events are logged with structured format:

```json
{
  "timestamp": "2025-10-30T15:00:00Z",
  "level": "INFO",
  "service": "streaming",
  "event": "chunk_signed",
  "session_id": "session_abc123",
  "organization_id": "org_xyz"
}
```

---

## Roadmap

### Phase 2 (Kafka Integration)
- Kafka producer/consumer endpoints
- Message queue support
- High-throughput event processing

### Phase 3 (Chat Wrappers)
- OpenAI-compatible streaming
- LangChain callback handler
- LlamaIndex integration

---

## Support

For issues or questions:
- Email: api@encypherai.com
- Documentation: https://docs.encypherai.com/streaming
- Status: https://verify.encypherai.com/status

---

**Related Documents:**
- [PRD: Enterprise Streaming Features](../../PRDs/CURRENT/PRD_Enterprise_Streaming_Features.md)
- [Testing Plan](../../docs/implementation_plans/STREAMING_TESTING_PLAN.md)
- [Implementation Summary](../../STREAMING_FEATURES_SUMMARY.md)
