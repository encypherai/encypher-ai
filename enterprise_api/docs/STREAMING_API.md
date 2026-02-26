# Streaming API

**Status:** Current implementation

---

## Overview

Enterprise API exposes two streaming patterns for signing workflows:

1. **SSE run-based signing** (`POST /api/v1/sign/stream`) for one-shot stream progress + final signed output.
2. **Session-based streaming** (WebSocket + session SSE) for incremental chunk processing and reconnection/recovery.

Both patterns require authenticated API access and sign permissions.

---

## 1) Stream Signing via SSE (run-based)

### Endpoint

- `POST /api/v1/sign/stream`

### Request

```json
{
  "text": "Content to sign",
  "document_id": "doc_optional",
  "document_title": "Optional title",
  "document_type": "article",
  "run_id": "run_optional_for_idempotent_retry"
}
```

### Event contract

The endpoint responds as `text/event-stream` and emits these events in order:

- `event: start`
- `event: progress`
- `event: partial`
- `event: final`

On failures, it emits `event: error`.

### Example SSE stream

```text
event: start
data: {"run_id":"run_123","document_id":"doc_123","status":"start","pct":0,"correlation_id":"req_abc"}

event: progress
data: {"run_id":"run_123","document_id":"doc_123","status":"progress","pct":10}

event: partial
data: {"run_id":"run_123","document_id":"doc_123","status":"partial","pct":90,"preview":"Signed content preview..."}

event: final
data: {"run_id":"run_123","document_id":"doc_123","status":"final","pct":100,"signed_text":"...","verification_url":"https://verify.encypherai.com/doc_123","duration_ms":84}
```

### Run-state lookup

- `GET /api/v1/sign/stream/runs/{run_id}`

Returns the most recent persisted state for recovery/resume UX.

```json
{
  "run_id": "run_123",
  "state": {
    "status": "final",
    "document_id": "doc_123",
    "pct": 100,
    "signed_text": "..."
  }
}
```

---

## 2) Session-Based Streaming

### Create session

- `POST /api/v1/sign/stream/sessions`
- `session_type` is accepted as query parameter (default: `websocket`)

Example request body:

```json
{
  "metadata": {"title": "Chat Session"},
  "signing_options": {
    "encode_first_chunk_only": true,
    "custom_metadata": {}
  }
}
```

Example response:

```json
{
  "success": true,
  "session_id": "session_abc123",
  "session_type": "websocket",
  "created_at": "2026-02-25T21:00:00Z",
  "expires_at": "2026-02-25T22:00:00Z",
  "signing_options": {
    "encode_first_chunk_only": true,
    "custom_metadata": {}
  }
}
```

### WebSocket endpoint

- `WS /api/v1/sign/stream?api_key=YOUR_API_KEY`
- Optional reconnect hint: `session_id` query parameter

Client -> server messages:

```json
{"type": "chunk", "content": "This is a streaming chunk.", "chunk_id": "chunk_001"}
{"type": "finalize"}
{"type": "recover_session", "session_id": "session_abc123"}
```

Server -> client messages:

```json
{"type": "connected", "session_id": "session_abc123"}
{"type": "signed_chunk", "chunk_id": "chunk_001", "content": "signed:...", "signed": true, "session_id": "session_abc123", "timestamp": "2026-02-25T21:00:00Z"}
{"type": "complete", "success": true, "session_id": "session_abc123", "document_id": "doc_xyz789", "total_chunks": 42, "duration_seconds": 12.4, "verification_url": "https://encypherai.com/verify/doc_xyz789"}
{"type": "error", "message": "Error description"}
```

### Session SSE mirror endpoint

- `GET /api/v1/sign/stream/sessions/{session_id}/events?api_key=YOUR_API_KEY`

This endpoint emits:

- `event: connected`
- status events from persisted stream state (`event: start`, `event: progress`, `event: partial`, `event: final`, or `event: error`)
- `event: done` when terminal state is reached
- periodic `:heartbeat`

Example:

```text
event: connected
data: {"session_id":"session_abc123"}

event: start
data: {"run_id":"run_123","status":"start","pct":0}

event: progress
data: {"run_id":"run_123","status":"progress","pct":10}

event: final
data: {"run_id":"run_123","status":"final","pct":100,"document_id":"doc_123"}

event: done
data: {"session_id":"session_abc123"}
```

### Close session

- `POST /api/v1/sign/stream/sessions/{session_id}/close`

Finalizes the session and returns completion metadata.

---

## 3) Streaming stats and health

- `GET /api/v1/sign/stream/stats` (organization-scoped)
- `GET /api/v1/sign/stream/health` (super-admin)

Stats response shape:

```json
{
  "success": true,
  "organization_id": "org_xyz",
  "active_connections": 5,
  "max_connections": 100
}
```

---

## 4) OpenAI-compatible chat streaming

- `POST /api/v1/chat/completions`

Use:

- `stream=true`
- `sign_response=true`

When streaming, payload chunks are OpenAI-style SSE records (`data: {...}` + `data: [DONE]`) and include Encypher metadata:

```json
{
  "object": "chat.completion.chunk",
  "choices": [{"delta": {"content": "..."}, "finish_reason": null}],
  "encypher": {"signed": true, "session_id": "session_abc123"}
}
```

Also available: `WS /api/v1/chat/stream` for chat-specific WebSocket protocol (`message` -> `assistant_chunk` / `turn_complete`).

---

## Error handling notes

- Authentication/authorization failures return HTTP 4xx (or WebSocket close code 1008).
- Stream-sign SSE failures emit `event: error` with machine-friendly error code/message payload.
- Session endpoints return `404` for missing runs/sessions and `403/404` for unauthorized cross-org access.

---

## Related docs

- `docs/API.md` (canonical endpoint catalog)
- `docs/QUICKSTART.md` (integration quick start)
- `docs/VERIFICATION_TRUST_MODEL.md` (verify semantics)
