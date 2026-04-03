# Streaming API Implementation

**Status:** Phase 1 Complete (90%)
**Version:** 1.0.0-preview
**Branch:** `feature/enterprise-streaming-api`

---

## Overview

The Streaming API provides real-time WebSocket-based content signing for streaming LLM outputs, chat applications, and event-driven architectures. Built with FastAPI, Redis, and the encypher-ai StreamingHandler.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Application                       │
│              (WebSocket, SSE, or Kafka)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  WebSocket Authentication                    │
│         (app/middleware/websocket_auth.py)                  │
│  - API key validation                                       │
│  - Organization verification                                │
│  - Tier-based permission checks                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Rate Limiting                             │
│         (app/middleware/rate_limiter.py)                    │
│  - Connection rate limits (per org)                        │
│  - Chunk rate limits (per session)                         │
│  - Tier-based limits                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Connection Manager                          │
│         (app/core/websocket_manager.py)                     │
│  - WebSocket connection pooling                            │
│  - Per-organization connection limits                      │
│  - Broadcast capabilities                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Session Service                             │
│         (app/services/session_service.py)                   │
│  - Redis-backed session persistence                        │
│  - Session TTL and expiration                              │
│  - Session recovery for reconnection                       │
│  - Buffer state management                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Streaming Service                           │
│         (app/services/streaming_service.py)                 │
│  - Integration with encypher-ai StreamingHandler          │
│  - Real-time chunk processing                              │
│  - Stream finalization                                      │
│  - Organization key management                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              encypher-ai StreamingHandler                    │
│  - C2PA-compliant metadata encoding                        │
│  - Chunk accumulation                                       │
│  - Cryptographic signing                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. WebSocket Connection Manager
**File:** `app/core/websocket_manager.py`

**Responsibilities:**
- Manage active WebSocket connections
- Enforce per-organization connection limits
- Track connection metadata
- Provide broadcast capabilities
- Handle connection cleanup

**Key Methods:**
- `connect(session_id, websocket, organization_id)` - Register new connection
- `disconnect(session_id)` - Cleanup connection
- `send_message(session_id, message)` - Send JSON message
- `get_connection_count(organization_id)` - Get active connection count

### 2. Session Service
**File:** `app/services/session_service.py`

**Responsibilities:**
- Persist session state in Redis
- Manage session lifecycle (create, update, delete)
- Handle session expiration via TTL
- Support session recovery after disconnection
- Track buffer state for streaming

**Key Methods:**
- `create_session(organization_id, session_type, metadata)` - Create new session
- `get_session(session_id)` - Retrieve session data
- `update_session(session_id, updates)` - Update session
- `close_session(session_id)` - Close and get final stats
- `recover_session(session_id)` - Recover for reconnection

**Redis Schema:**
```
Key: encypher:session:{session_id}
TTL: 3600 seconds (1 hour)
Value: {
  "session_id": "session_abc123",
  "organization_id": "org_xyz",
  "session_type": "websocket",
  "created_at": "2025-10-30T15:00:00Z",
  "last_activity": "2025-10-30T15:05:00Z",
  "expires_at": "2025-10-30T16:00:00Z",
  "chunks_processed": 42,
  "buffer_state": {
    "accumulated_text": "...",
    "is_accumulating": false,
    "has_encoded": true
  },
  "metadata": {},
  "status": "active"
}
```

### 3. Streaming Service
**File:** `app/services/streaming_service.py`

**Responsibilities:**
- Process streaming chunks with encypher-ai
- Manage signing operations
- Coordinate with session service
- Handle stream finalization

**Key Methods:**
- `create_session(...)` - Create streaming session
- `process_chunk(chunk, session_id, ...)` - Process and sign chunk
- `finalize_stream(session_id, ...)` - Finalize and get document ID
- `recover_session(session_id)` - Recover session state

### 4. WebSocket Authentication
**File:** `app/middleware/websocket_auth.py`

**Responsibilities:**
- Validate API keys for WebSocket connections
- Verify organization permissions
- Check tier-based access
- Support demo key bypass

**Key Functions:**
- `authenticate_websocket(websocket, api_key)` - Authenticate connection
- `require_streaming_permission(organization)` - Verify streaming access

**Tier Requirements:**
- Professional, Enterprise, or Demo tier required
- `can_sign` permission required

### 5. Rate Limiting
**File:** `app/middleware/rate_limiter.py`

**Responsibilities:**
- Enforce connection rate limits per organization
- Enforce chunk rate limits per session
- Implement sliding window algorithm
- Provide tier-based limits

**Rate Limits:**
| Tier | Connections/min | Chunks/sec |
|------|----------------|------------|
| Basic | 5 | 10 |
| Professional | 20 | 100 |
| Enterprise | 100 | 1,000 |
| Demo | 10 | 50 |

**Key Methods:**
- `check_connection_rate(organization_id, tier)` - Check connection limit
- `check_chunk_rate(session_id, tier)` - Check chunk limit
- `reset_session(session_id)` - Reset session limits

---

## API Endpoints

### WebSocket Endpoints

#### `WS /api/v1/sign/stream`
Real-time content signing via WebSocket.

**Query Parameters:**
- `api_key` (required) - API key for authentication
- `session_id` (optional) - Session ID for recovery

**Message Protocol:**

**Client → Server:**
```json
// Send chunk
{
  "type": "chunk",
  "content": "Text to sign. ",
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

**Server → Client:**
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
  "content": "signed:Text to sign. ",
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
  "verification_url": "https://encypher.com/verify/doc_xyz789"
}

// Error
{
  "type": "error",
  "message": "Error description"
}
```

#### `WS /api/v1/chat/stream`
Chat application wrapper (currently redirects to `/sign/stream`).

### REST Endpoints

#### `POST /api/v1/sign/stream/sessions`
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

#### `POST /api/v1/sign/stream/sessions/{session_id}/close`
Close a streaming session.

**Response:**
```json
{
  "type": "complete",
  "success": true,
  "session_id": "session_abc123",
  "document_id": "doc_xyz789",
  "total_chunks": 42,
  "duration_seconds": 125.5,
  "verification_url": "https://encypher.com/verify/doc_xyz789"
}
```

#### `GET /api/v1/sign/stream/stats`
Get streaming statistics for organization.

**Response:**
```json
{
  "success": true,
  "organization_id": "org_xyz",
  "active_connections": 5,
  "max_connections": 100
}
```

### SSE Endpoint

#### `GET /api/v1/sign/stream/sessions/{session_id}/events`
Server-Sent Events for unidirectional streaming (session scoped).

**Path Parameters:**
- `session_id` (required) - Session identifier

**Query Parameters:**
- `api_key` (optional) - API key for authentication

---

## Testing

### Unit Tests
**File:** `tests/test_streaming_basic.py`

Tests for core components:
- ConnectionManager initialization and methods
- SessionService session key generation

### Integration Tests
**File:** `tests/integration/test_streaming_e2e.py`

Comprehensive E2E tests:
- WebSocket connection establishment
- Chunk processing and signing
- Stream finalization
- Authentication (valid/invalid keys)
- Rate limiting (connection and chunk)
- Session recovery
- Error handling
- Concurrent connections
- Performance benchmarks

**Run Tests:**
```bash
# All streaming tests
uv run pytest tests/ -k streaming -v

# Integration tests only
uv run pytest tests/integration/test_streaming_e2e.py -v

# Specific test class
uv run pytest tests/integration/test_streaming_e2e.py::TestWebSocketBasicFlow -v
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

# Demo API key (optional)
DEMO_API_KEY=demo_key_12345
```

### Connection Limits

Configure in `app/core/websocket_manager.py`:
```python
connection_manager = ConnectionManager(max_connections_per_org=100)
```

### Rate Limits

Configure in `app/middleware/rate_limiter.py`:
```python
TIER_LIMITS = {
    "professional": {"connections_per_minute": 20, "chunks_per_second": 100},
    "enterprise": {"connections_per_minute": 100, "chunks_per_second": 1000},
}
```

---

## Error Handling

### Common Errors

**Authentication Failed:**
- Code: 1008 (Policy Violation)
- Reason: "API key required" / "Invalid API key"

**Rate Limit Exceeded:**
- Code: 1008
- Reason: "Connection rate limit exceeded" / "Chunk rate limit exceeded"

**Session Errors:**
- Type: "error"
- Message: "Session not found or expired"

**Invalid Message:**
- Type: "error"
- Message: "Invalid JSON" / "Unknown message type"

---

## Performance

### Benchmarks (Target)

- Connection establishment: <50ms
- Chunk signing latency: <30ms (P95)
- Throughput: 10,000 chunks/second per instance
- Concurrent connections: 10,000+ per instance
- Memory usage: <2GB for 10k connections

### Current Performance

- Tested with 5 concurrent connections
- Tested with 50+ chunks per session
- Rate limiting verified at tier limits

---

## Security

### Authentication
- API key required for all connections
- Organization verification
- Tier-based permission checks

### Rate Limiting
- Connection limits prevent DDoS
- Chunk limits prevent abuse
- Sliding window algorithm

### Data Security
- TLS 1.3 for WebSocket connections (in production)
- Redis encryption at rest
- No plaintext credentials in logs
- Private keys encrypted in database

---

## Monitoring

### Metrics to Track

- Active connections per organization
- Chunks processed per session
- Session duration
- Error rates
- Rate limit hits
- Connection establishment time
- Chunk processing latency

### Logging

Structured logs with:
- Timestamp
- Log level
- Service name
- Event type
- Session ID
- Organization ID

---

## Future Enhancements

### Phase 2: Kafka Integration
- Kafka producer/consumer endpoints
- Message queue support
- High-throughput event processing

### Phase 3: Chat Wrappers
- OpenAI-compatible streaming endpoint
- LangChain callback handler
- LlamaIndex integration

### Phase 4: Production Readiness
- Prometheus metrics
- Grafana dashboards
- Load testing (10k+ connections)
- Production deployment

---

## Troubleshooting

### Redis Connection Failed
```
WARNING: Failed to connect to Redis. Running without session persistence.
```
**Solution:** Ensure Redis is running and `REDIS_URL` is correct.

### WebSocket Connection Refused
**Possible Causes:**
- Invalid API key
- Rate limit exceeded
- Insufficient tier

**Solution:** Check API key, wait for rate limit reset, or upgrade tier.

### Session Not Found
**Possible Causes:**
- Session expired (TTL exceeded)
- Session was closed
- Redis connection lost

**Solution:** Create new session or check Redis connectivity.

---

## Related Documentation

- [PRD: Enterprise Streaming Features](../../../PRDs/CURRENT/PRD_Enterprise_Streaming_Features.md)
- [Progress Tracker](../../../PRDs/CURRENT/STREAMING_PROGRESS.md)
- [API Documentation](../../docs/STREAMING_API.md)
- [Testing Plan](../../../docs/implementation_plans/STREAMING_TESTING_PLAN.md)

---

**Last Updated:** 2025-10-30
**Maintainer:** Engineering Team
**Status:** Phase 1 Complete (90%)
