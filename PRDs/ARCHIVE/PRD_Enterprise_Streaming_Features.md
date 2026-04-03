# PRD: Enterprise Streaming & Real-Time Signing Features

**Status:** Draft
**Priority:** High
**Tier:** Enterprise Only
**Target Release:** Phase 3
**Owner:** Engineering Team
**Created:** 2025-10-30

---

## 1. Executive Summary

### Overview
Implement enterprise-grade streaming support for real-time content signing, enabling integration with chat applications, Kafka streams, WebSocket connections, and Server-Sent Events (SSE). This feature will allow organizations to sign streaming LLM outputs, live chat messages, and event streams in real-time with C2PA compliance.

### Business Value
- **Revenue Impact:** Premium enterprise feature with dedicated pricing tier
- **Market Differentiation:** First C2PA-compliant streaming signing solution
- **Use Cases:**
  - Real-time LLM chat applications (ChatGPT-style interfaces)
  - Live content moderation and attribution
  - Event-driven architectures with Kafka/RabbitMQ
  - WebSocket-based collaborative editing
  - Streaming news feeds and social media

### Success Metrics
- Support 10,000+ concurrent streaming connections
- <50ms signing latency for streaming chunks
- 99.9% uptime for streaming endpoints
- Zero message loss in Kafka integration

---

## 2. Current State Analysis

### Existing Capabilities ✅
1. **SDK Streaming Support** (`enterprise_sdk/encypher_enterprise/streaming.py`)
   - `StreamingSigner` for synchronous streams
   - `AsyncStreamingSigner` for async streams
   - Sentence boundary detection
   - Buffer management

2. **Core Streaming Handler** (`encypher-ai/encypher/streaming/handlers.py`)
   - `StreamingHandler` class with metadata encoding
   - Chunk accumulation and target detection
   - First-chunk-only encoding mode
   - Integration tested in `enterprise_api`

### Missing Components ❌
1. **API Streaming Endpoints**
   - No WebSocket endpoints
   - No SSE (Server-Sent Events) support
   - No streaming-specific REST endpoints

2. **Message Queue Integration**
   - No Kafka producer/consumer
   - No RabbitMQ support
   - No Redis Streams integration

3. **Infrastructure**
   - No connection pooling for streams
   - No backpressure handling
   - No stream-specific rate limiting
   - No monitoring/observability for streams

---

## 3. Technical Requirements

### 3.1 API Endpoints

#### WebSocket Endpoints

**`WS /api/v1/stream/sign`** - Real-time signing stream
```json
// Client → Server (chunk)
{
  "type": "chunk",
  "content": "This is a streaming chunk. ",
  "chunk_id": "chunk_001",
  "session_id": "session_abc123"
}

// Server → Client (signed chunk)
{
  "type": "signed_chunk",
  "content": "signed:This is a streaming chunk. ",
  "chunk_id": "chunk_001",
  "signed": true,
  "metadata": {
    "document_id": "doc_xyz789",
    "timestamp": "2025-10-30T15:30:00Z"
  }
}

// Client → Server (finalize)
{
  "type": "finalize",
  "session_id": "session_abc123"
}

// Server → Client (complete)
{
  "type": "complete",
  "document_id": "doc_xyz789",
  "total_chunks": 15,
  "verification_url": "https://encypher.com/verify/doc_xyz789"
}
```

**`WS /api/v1/stream/chat`** - Chat application wrapper
```json
// Client → Server (chat message)
{
  "type": "message",
  "role": "user",
  "content": "What is C2PA?",
  "conversation_id": "conv_123"
}

// Server → Client (streaming response with signing)
{
  "type": "assistant_chunk",
  "content": "C2PA is a standard for content authenticity. ",
  "signed": true,
  "chunk_index": 0,
  "conversation_id": "conv_123"
}
```

#### SSE Endpoints

**`GET /api/v1/stream/events`** - Server-Sent Events for unidirectional streaming
```
event: chunk
data: {"content": "Signed chunk...", "chunk_id": "001"}

event: complete
data: {"document_id": "doc_123", "status": "signed"}
```

#### REST Endpoints

**`POST /api/v1/stream/session/create`** - Create streaming session
```json
{
  "session_type": "websocket|sse|kafka",
  "metadata": {
    "title": "Live Chat Session",
    "application": "ChatApp v1.0"
  },
  "signing_options": {
    "sign_on_sentence": true,
    "buffer_size": 1000,
    "encode_first_chunk_only": true
  }
}

// Response
{
  "success": true,
  "session_id": "session_abc123",
  "websocket_url": "wss://api.encypher.com/api/v1/stream/sign?session=session_abc123",
  "expires_at": "2025-10-30T16:30:00Z"
}
```

**`POST /api/v1/stream/session/{session_id}/close`** - Close streaming session
```json
{
  "success": true,
  "document_id": "doc_xyz789",
  "total_chunks_signed": 42,
  "session_duration_ms": 125000
}
```

### 3.2 Kafka Integration

#### Producer Configuration
```python
# Produce signed content to Kafka topic
topic: "encypher.signed.content"
partition_key: organization_id
message_format: {
  "document_id": "doc_123",
  "signed_text": "...",
  "metadata": {...},
  "timestamp": "2025-10-30T15:30:00Z"
}
```

#### Consumer Configuration
```python
# Consume unsigned content from Kafka topic
topic: "encypher.unsigned.content"
consumer_group: "encypher-signing-service"
message_format: {
  "content": "Text to sign...",
  "metadata": {...},
  "callback_topic": "client.signed.results"
}
```

#### Kafka Endpoints

**`POST /api/v1/kafka/producer/configure`** - Configure Kafka producer
```json
{
  "bootstrap_servers": ["kafka1:9092", "kafka2:9092"],
  "topic": "encypher.signed.content",
  "security_protocol": "SASL_SSL",
  "sasl_mechanism": "PLAIN",
  "sasl_username": "user",
  "sasl_password": "pass"
}
```

**`POST /api/v1/kafka/consumer/subscribe`** - Subscribe to Kafka topic for signing
```json
{
  "topics": ["client.unsigned.content"],
  "group_id": "encypher-signer-org123",
  "callback_topic": "client.signed.results",
  "auto_commit": true
}
```

### 3.3 Chat Application Wrapper

#### OpenAI-Compatible Streaming
```python
# Wrap OpenAI streaming responses
POST /api/v1/stream/chat/openai-compatible

Request:
{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": true,
  "sign_response": true
}

Response (SSE):
data: {"choices":[{"delta":{"content":"Hello! "}}],"signed":true}
data: {"choices":[{"delta":{"content":"How can I help?"}}],"signed":true}
data: [DONE]
```

#### LangChain Integration
```python
# Streaming callback handler for LangChain
from encypher_enterprise.integrations.langchain import EncypherStreamingHandler

handler = EncypherStreamingHandler(client=encypher_client)
chain.run(callbacks=[handler])
```

---

## 4. Architecture Design

### 4.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (Chat Apps, Kafka Producers, WebSocket Clients, SSE)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway / Load Balancer                │
│              (WebSocket Upgrade, SSE Support)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Streaming Service (FastAPI + WebSockets)        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  WebSocket   │  │     SSE      │  │    Kafka     │     │
│  │   Handler    │  │   Handler    │  │  Integration │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Connection Manager & Session Store            │  │
│  │  (Redis for session state, connection pooling)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Signing Core (encypher-ai)                  │
│  - StreamingHandler (existing)                              │
│  - StreamingSigner (SDK)                                     │
│  - C2PA Manifest Generation                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │    Kafka     │     │
│  │  (metadata)  │  │  (sessions)  │  │   (events)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Connection Management

**Session Store (Redis)**
```python
session_data = {
    "session_id": "session_abc123",
    "organization_id": "org_xyz",
    "connection_type": "websocket",
    "created_at": "2025-10-30T15:00:00Z",
    "last_activity": "2025-10-30T15:05:00Z",
    "chunks_processed": 42,
    "buffer_state": {...},
    "metadata": {...}
}
```

**Connection Pooling**
- Max connections per organization: 100 (configurable)
- Idle timeout: 5 minutes
- Max session duration: 1 hour
- Automatic cleanup on disconnect

### 4.3 Rate Limiting

**Streaming-Specific Limits**
| Tier | Concurrent Connections | Chunks/Second | Max Session Duration |
|------|----------------------|---------------|---------------------|
| Professional | 10 | 100 | 30 minutes |
| Enterprise | 100 | 1000 | 2 hours |
| Enterprise+ | 1000 | 10000 | Unlimited |

---

## 5. Implementation Plan

### Phase 1: Core Streaming Infrastructure (Week 1-2)

#### Task 1.1: WebSocket Endpoint Implementation
- [ ] Create `app/api/v1/endpoints/streaming.py`
- [ ] Implement WebSocket connection handler
- [ ] Add session management with Redis
- [ ] Implement connection pooling
- [ ] Add authentication middleware for WebSocket

**Files to Create:**
- `enterprise_api/app/api/v1/endpoints/streaming.py`
- `enterprise_api/app/services/streaming_service.py`
- `enterprise_api/app/core/websocket_manager.py`
- `enterprise_api/app/middleware/websocket_auth.py`

#### Task 1.2: Session Management
- [ ] Implement session creation/deletion endpoints
- [ ] Add Redis session store
- [ ] Implement session expiration
- [ ] Add session recovery on reconnect

**Files to Create:**
- `enterprise_api/app/services/session_service.py`
- `enterprise_api/app/models/session.py`

#### Task 1.3: SSE Implementation
- [ ] Create SSE endpoint
- [ ] Implement event streaming
- [ ] Add heartbeat mechanism
- [ ] Handle client disconnections

**Files to Create:**
- `enterprise_api/app/api/v1/endpoints/sse.py`
- `enterprise_api/app/services/sse_service.py`

### Phase 2: Kafka Integration (Week 3)

#### Task 2.1: Kafka Producer
- [ ] Add kafka-python dependency
- [ ] Implement producer configuration endpoint
- [ ] Create message serialization
- [ ] Add error handling and retries

**Files to Create:**
- `enterprise_api/app/integrations/kafka_producer.py`
- `enterprise_api/app/api/v1/endpoints/kafka.py`

#### Task 2.2: Kafka Consumer
- [ ] Implement consumer subscription
- [ ] Add consumer group management
- [ ] Implement callback mechanism
- [ ] Add offset management

**Files to Create:**
- `enterprise_api/app/integrations/kafka_consumer.py`
- `enterprise_api/app/services/kafka_signing_service.py`

#### Task 2.3: Kafka Monitoring
- [ ] Add consumer lag monitoring
- [ ] Implement health checks
- [ ] Add metrics collection
- [ ] Create alerting rules

### Phase 3: Chat Application Wrappers (Week 4)

#### Task 3.1: OpenAI-Compatible Endpoint
- [ ] Create OpenAI-compatible streaming endpoint
- [ ] Implement SSE response format
- [ ] Add conversation tracking
- [ ] Implement signing integration

**Files to Create:**
- `enterprise_api/app/api/v1/endpoints/chat.py`
- `enterprise_api/app/services/chat_service.py`

#### Task 3.2: LangChain Integration
- [ ] Create LangChain callback handler
- [ ] Add to SDK integrations
- [ ] Implement streaming callbacks
- [ ] Add examples

**Files to Create:**
- `enterprise_sdk/encypher_enterprise/integrations/langchain.py`
- `enterprise_sdk/examples/langchain_streaming.py`

#### Task 3.3: LlamaIndex Integration
- [ ] Create LlamaIndex callback handler
- [ ] Add streaming support
- [ ] Implement node-level signing
- [ ] Add examples

**Files to Create:**
- `enterprise_sdk/encypher_enterprise/integrations/llamaindex.py`
- `enterprise_sdk/examples/llamaindex_streaming.py`

### Phase 4: Testing & Documentation (Week 5)

#### Task 4.1: Unit Tests
- [ ] WebSocket handler tests
- [ ] SSE handler tests
- [ ] Kafka integration tests
- [ ] Session management tests
- [ ] Rate limiting tests

**Files to Create:**
- `enterprise_api/tests/test_streaming_websocket.py`
- `enterprise_api/tests/test_streaming_sse.py`
- `enterprise_api/tests/test_kafka_integration.py`
- `enterprise_api/tests/test_session_management.py`

#### Task 4.2: Integration Tests
- [ ] End-to-end WebSocket flow
- [ ] Kafka producer-consumer flow
- [ ] Chat application simulation
- [ ] Load testing (10k concurrent connections)
- [ ] Failure recovery tests

**Files to Create:**
- `enterprise_api/tests/integration/test_streaming_e2e.py`
- `enterprise_api/tests/integration/test_kafka_e2e.py`
- `enterprise_api/tests/load/test_streaming_load.py`

#### Task 4.3: Documentation
- [ ] API documentation for streaming endpoints
- [ ] Kafka integration guide
- [ ] Chat wrapper examples
- [ ] Performance tuning guide
- [ ] Troubleshooting guide

**Files to Create:**
- `docs/api_specs/STREAMING_API.md`
- `docs/guides/KAFKA_INTEGRATION.md`
- `docs/guides/CHAT_WRAPPERS.md`
- `docs/guides/STREAMING_PERFORMANCE.md`

---

## 6. Testing Strategy

### 6.1 Simulation Scenarios

#### Scenario 1: Real-Time Chat Application
```python
# Simulate ChatGPT-style streaming
async def test_chat_streaming():
    """
    Simulate a chat application with streaming responses.
    - User sends message
    - LLM streams response in chunks
    - Each chunk is signed in real-time
    - Final document is assembled and verified
    """
    async with websocket_client.connect() as ws:
        # Send user message
        await ws.send_json({
            "type": "message",
            "content": "Explain quantum computing"
        })

        # Receive streaming signed chunks
        chunks = []
        async for message in ws:
            data = json.loads(message)
            if data["type"] == "signed_chunk":
                chunks.append(data["content"])
                assert data["signed"] is True
            elif data["type"] == "complete":
                break

        # Verify complete document
        full_text = "".join(chunks)
        verify_result = await client.verify(full_text)
        assert verify_result.is_valid
```

#### Scenario 2: Kafka Stream Processing
```python
# Simulate Kafka-based event streaming
async def test_kafka_streaming():
    """
    Simulate event-driven architecture with Kafka.
    - Producer sends unsigned content to topic
    - Encypher consumes, signs, and produces to output topic
    - Consumer receives signed content
    - Verify end-to-end flow
    """
    # Configure Kafka producer
    await client.kafka_producer_configure({
        "bootstrap_servers": ["localhost:9092"],
        "topic": "signed.content"
    })

    # Subscribe consumer
    await client.kafka_consumer_subscribe({
        "topics": ["unsigned.content"],
        "callback_topic": "signed.content"
    })

    # Produce unsigned content
    producer.send("unsigned.content", {
        "content": "Breaking news article...",
        "metadata": {"source": "NewsAPI"}
    })

    # Consume signed content
    signed_message = consumer.poll(timeout=5.0)
    assert signed_message is not None
    assert "signed_text" in signed_message.value
```

#### Scenario 3: High-Concurrency Load Test
```python
# Simulate 10,000 concurrent WebSocket connections
async def test_high_concurrency():
    """
    Load test with 10k concurrent connections.
    - Establish 10k WebSocket connections
    - Each sends 100 chunks
    - Measure latency and throughput
    - Verify no message loss
    """
    connections = []
    for i in range(10000):
        ws = await websocket_client.connect()
        connections.append(ws)

    # Send chunks concurrently
    async def send_chunks(ws, conn_id):
        for chunk_id in range(100):
            await ws.send_json({
                "type": "chunk",
                "content": f"Chunk {chunk_id} from conn {conn_id}"
            })
            response = await ws.receive_json()
            assert response["signed"] is True

    await asyncio.gather(*[
        send_chunks(ws, i) for i, ws in enumerate(connections)
    ])
```

### 6.2 Performance Benchmarks

**Target Metrics:**
- WebSocket connection establishment: <50ms
- Chunk signing latency: <30ms (P95)
- Throughput: 10,000 chunks/second per instance
- Concurrent connections: 10,000+ per instance
- Memory usage: <2GB for 10k connections
- CPU usage: <70% under full load

### 6.3 Failure Scenarios

1. **Network Interruption**
   - Test WebSocket reconnection
   - Verify session recovery
   - Ensure no data loss

2. **Kafka Broker Failure**
   - Test producer retry logic
   - Verify consumer rebalancing
   - Check offset management

3. **Redis Failure**
   - Test session fallback
   - Verify graceful degradation
   - Check session recovery

4. **Rate Limit Exceeded**
   - Test throttling behavior
   - Verify error messages
   - Check connection cleanup

---

## 7. Dependencies & Infrastructure

### 7.1 New Dependencies

**Python Packages (API):**
```toml
# Add to enterprise_api/pyproject.toml
websockets = "^12.0"
kafka-python = "^2.0.2"
redis = "^5.0.0"
aioredis = "^2.0.1"
sse-starlette = "^2.0.0"
```

**Python Packages (SDK):**
```toml
# Add to enterprise_sdk/pyproject.toml
websocket-client = "^1.7.0"
kafka-python = "^2.0.2"
langchain = "^0.1.0"  # optional
llama-index = "^0.9.0"  # optional
```

### 7.2 Infrastructure Requirements

**Redis:**
- Purpose: Session store, connection state
- Memory: 4GB minimum
- Persistence: AOF enabled
- Replication: Master-slave setup

**Kafka:**
- Purpose: Event streaming, message queue
- Brokers: 3 minimum
- Partitions: 10 per topic
- Replication factor: 3

**Load Balancer:**
- WebSocket support required
- Sticky sessions enabled
- Health check endpoint: `/health/streaming`

---

## 8. Pricing & Business Model

### 8.1 Pricing Tiers

**Professional Tier:**
- 10 concurrent streaming connections
- 100 chunks/second
- WebSocket + SSE support
- **Price:** +$50/month

**Enterprise Tier:**
- 100 concurrent streaming connections
- 1,000 chunks/second
- WebSocket + SSE + Kafka
- **Price:** +$500/month

**Enterprise+ Tier:**
- 1,000+ concurrent connections
- 10,000+ chunks/second
- Dedicated Kafka cluster
- Custom integrations
- **Price:** Custom (starting at $2,000/month)

### 8.2 Usage-Based Pricing

- **Streaming chunks:** $0.001 per 1,000 chunks (after quota)
- **Kafka messages:** $0.0005 per 1,000 messages
- **Connection hours:** $0.10 per connection-hour (after quota)

---

## 9. Security Considerations

### 9.1 Authentication
- WebSocket: Token-based auth in connection upgrade
- Kafka: SASL/SCRAM authentication
- SSE: Bearer token in query params or headers

### 9.2 Authorization
- Per-organization connection limits
- Topic-level access control for Kafka
- Session-level permissions

### 9.3 Data Security
- TLS 1.3 for all WebSocket connections
- Kafka SSL/TLS encryption
- Redis encryption at rest
- No plaintext credentials in logs

### 9.4 Rate Limiting
- Connection-level rate limiting
- Chunk-level rate limiting
- Kafka message rate limiting
- DDoS protection

---

## 10. Monitoring & Observability

### 10.1 Metrics

**WebSocket Metrics:**
- Active connections count
- Connection duration
- Messages sent/received
- Errors per connection

**Kafka Metrics:**
- Producer throughput
- Consumer lag
- Message processing time
- Failed messages

**Performance Metrics:**
- Signing latency (P50, P95, P99)
- Throughput (chunks/second)
- Memory usage per connection
- CPU usage

### 10.2 Logging

**Structured Logs:**
```json
{
  "timestamp": "2025-10-30T15:30:00Z",
  "level": "INFO",
  "service": "streaming",
  "event": "chunk_signed",
  "session_id": "session_abc123",
  "organization_id": "org_xyz",
  "chunk_size": 256,
  "latency_ms": 23
}
```

### 10.3 Alerting

**Critical Alerts:**
- Connection pool exhaustion
- Kafka consumer lag > 10,000
- Signing latency > 100ms (P95)
- Error rate > 1%

---

## 11. Success Criteria

### 11.1 Launch Criteria
- [ ] All Phase 1-4 tasks completed
- [ ] 100% test coverage for streaming endpoints
- [ ] Load test passed (10k concurrent connections)
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Performance benchmarks met

### 11.2 Post-Launch Metrics (30 days)
- 50+ organizations using streaming features
- 1M+ chunks signed via streaming
- <0.1% error rate
- 99.9% uptime
- <50ms P95 latency

---

## 12. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| WebSocket connection instability | High | Medium | Implement reconnection logic, session recovery |
| Kafka broker failures | High | Low | Multi-broker setup, replication factor 3 |
| Redis session store failure | Medium | Low | Fallback to in-memory sessions, regular backups |
| High latency under load | High | Medium | Horizontal scaling, connection pooling, caching |
| DDoS attacks on WebSocket | High | Medium | Rate limiting, connection limits, DDoS protection |

---

## 13. Future Enhancements

### Phase 5 (Future)
- [ ] gRPC streaming support
- [ ] RabbitMQ integration
- [ ] Redis Streams integration
- [ ] GraphQL subscriptions
- [ ] Multi-region streaming (edge locations)
- [ ] Streaming analytics dashboard
- [ ] Custom protocol support

---

## 14. Appendix

### A. Example Use Cases

**Use Case 1: AI Chat Application**
```
Company: TechNews AI
Requirement: Sign all AI-generated articles in real-time
Solution: WebSocket streaming with sentence-level signing
Volume: 10k articles/day, 500 concurrent users
```

**Use Case 2: News Wire Service**
```
Company: GlobalNews Wire
Requirement: Sign breaking news as it's written
Solution: Kafka integration with producer/consumer
Volume: 100k articles/day, 24/7 operation
```

**Use Case 3: Legal Document Platform**
```
Company: LegalTech Pro
Requirement: Sign collaborative document edits in real-time
Solution: WebSocket with conflict resolution
Volume: 5k documents/day, 1k concurrent editors
```

### B. References
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [C2PA 2.2 Specification](https://c2pa.org/specifications/specifications/2.2/index.html)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Next Review:** 2025-11-15
