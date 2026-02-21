"""
Streaming API Router - WebSocket and SSE Endpoints.

Provides real-time streaming endpoints for content signing.
"""

import json
import logging
import time
from typing import Any, Dict, Optional, cast
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import connection_manager
from app.database import get_db
from app.dependencies import get_current_organization, require_sign_permission, require_super_admin_dep
from app.middleware.api_rate_limiter import api_rate_limiter
from app.middleware.rate_limiter import streaming_rate_limiter
from app.middleware.websocket_auth import authenticate_websocket, require_streaming_permission
from app.models.organization import Organization
from app.models.request_models import SignRequest
from app.observability.metrics import increment
from app.schemas.streaming import StreamSignRequest
from app.services.session_service import session_service
from app.services.signing_executor import execute_signing
from app.services.streaming_service import streaming_service

logger = logging.getLogger(__name__)

router = APIRouter()


def _sse_event(event: str, payload: dict) -> str:
    """Format SSE event."""

    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


@router.post("/sign/stream", response_class=StreamingResponse)
async def stream_signing(
    stream_request: StreamSignRequest,
    request: Request,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream signing progress via SSE."""

    correlation_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    run_id = stream_request.run_id or f"run_{uuid4().hex}"
    document_id = stream_request.document_id or f"doc_{uuid4().hex[:16]}"

    async def event_stream():
        org_id = organization["organization_id"]

        start_payload = {
            "run_id": run_id,
            "document_id": document_id,
            "status": "start",
            "pct": 0,
            "correlation_id": correlation_id,
        }
        await session_service.save_stream_state(run_id, {**start_payload, "organization_id": org_id})
        yield _sse_event("start", start_payload)
        try:
            progress_payload = {
                "run_id": run_id,
                "document_id": document_id,
                "status": "progress",
                "pct": 10,
            }
            await session_service.save_stream_state(run_id, {**progress_payload, "organization_id": org_id})
            yield _sse_event("progress", progress_payload)

            sign_request = SignRequest(
                text=stream_request.text,
                document_id=document_id,
                document_title=stream_request.document_title,
                document_type=stream_request.document_type,
            )
            start_time = time.perf_counter()
            response = await execute_signing(
                request=sign_request,
                organization=organization,
                db=db,
                document_id=document_id,
            )
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            partial_payload = {
                "run_id": run_id,
                "document_id": response.document_id,
                "status": "partial",
                "pct": 90,
                "preview": response.signed_text[:512],
            }
            await session_service.save_stream_state(run_id, {**partial_payload, "organization_id": org_id})
            yield _sse_event("partial", partial_payload)

            final_payload = {
                "run_id": run_id,
                "document_id": response.document_id,
                "status": "final",
                "pct": 100,
                "signed_text": response.signed_text,
                "verification_url": response.verification_url,
                "duration_ms": duration_ms,
            }
            await session_service.save_stream_state(run_id, {**final_payload, "organization_id": org_id})
            yield _sse_event("final", final_payload)
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
            error_payload = {
                "run_id": run_id,
                "document_id": document_id,
                "status": "error",
                "code": detail.get("code", "E_STREAM_SIGN"),
                "message": detail.get("message", "Streaming signing failed"),
            }
            await session_service.save_stream_state(run_id, {**error_payload, "organization_id": org_id})
            yield _sse_event("error", error_payload)

    allowed, retry_after, remaining, limit = api_rate_limiter.check(
        organization_id=organization["organization_id"],
        scope="stream_sign",
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "E_RATE_STREAM", "message": "Streaming rate limit exceeded"},
            headers={"Retry-After": str(retry_after or 1)},
        )

    increment("stream_sign_requests")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Limit": str(limit),
    }
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)


@router.post("/sign/stream/sessions")
async def create_streaming_session(
    session_type: str = "websocket",
    metadata: Optional[dict] = None,
    signing_options: Optional[dict] = None,
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new streaming session.

    Args:
        session_type: Type of session (websocket, sse, kafka)
        metadata: Optional session metadata
        signing_options: Optional signing configuration
        organization: Authenticated organization
        db: Database session

    Returns:
        Session creation result with session_id
    """
    try:
        result = await streaming_service.create_session(
            organization_id=organization.organization_id, session_type=session_type, metadata=metadata, signing_options=signing_options
        )

        return result
    except Exception as e:
        logger.error(f"Failed to create streaming session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create streaming session")


@router.post("/sign/stream/sessions/{session_id}/close")
async def close_streaming_session(
    session_id: str, organization: Organization = Depends(get_current_organization), db: AsyncSession = Depends(get_db)
):
    """
    Close a streaming session.

    Args:
        session_id: Session identifier
        organization: Authenticated organization
        db: Database session

    Returns:
        Session closure result with stats
    """
    try:
        # Verify session belongs to organization
        session_data = await session_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        if session_data["organization_id"] != organization.organization_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        result = await streaming_service.finalize_stream(
            session_id=session_id, organization_id=organization.organization_id, private_key_encrypted=organization.private_key_encrypted
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to close streaming session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to close streaming session")


@router.websocket("/sign/stream")
async def websocket_sign_endpoint(websocket: WebSocket, session_id: Optional[str] = Query(None), api_key: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time content signing.

    Protocol:
        Client → Server:
            {"type": "chunk", "content": "text...", "chunk_id": "optional"}
            {"type": "finalize"}
            {"type": "recover_session", "session_id": "..."}

        Server → Client:
            {"type": "signed_chunk", "content": "...", "signed": true}
            {"type": "complete", "document_id": "...", "total_chunks": 42}
            {"type": "error", "message": "..."}

    Args:
        websocket: WebSocket connection
        session_id: Optional session ID for recovery
        api_key: API key for authentication
    """
    # Authenticate WebSocket connection
    try:
        organization = await authenticate_websocket(websocket, api_key)
        await require_streaming_permission(organization)
        organization_id = organization["organization_id"]
        private_key_encrypted = organization["private_key_encrypted"]
        tier = organization["tier"]
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return

    # Check connection rate limit
    allowed, error_msg = streaming_rate_limiter.check_connection_rate(organization_id, tier)
    if not allowed:
        logger.warning(f"Connection rate limit exceeded for org {organization_id}")
        await websocket.close(code=1008, reason=error_msg)
        return

    # Generate or use provided session ID
    if not session_id:
        session_result = await streaming_service.create_session(organization_id=organization_id, session_type="websocket")
        session_id = session_result["session_id"]

    try:
        # Connect WebSocket
        await connection_manager.connect(session_id=session_id, websocket=websocket, organization_id=organization_id)

        # Send connection confirmation
        await connection_manager.send_message(session_id, {"type": "connected", "session_id": session_id})

        # Message processing loop
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)

                message_type = message.get("type")

                if message_type == "chunk":
                    # Check chunk rate limit
                    allowed, error_msg = streaming_rate_limiter.check_chunk_rate(session_id, tier)
                    if not allowed:
                        await connection_manager.send_message(session_id, {"type": "error", "message": error_msg})
                        continue

                    # Process chunk
                    chunk_content = message.get("content", "")
                    chunk_id = message.get("chunk_id")

                    result = await streaming_service.process_chunk(
                        chunk=chunk_content,
                        session_id=session_id,
                        organization_id=organization_id,
                        private_key_encrypted=private_key_encrypted,
                        chunk_id=chunk_id,
                    )

                    await connection_manager.send_message(session_id, result)

                elif message_type == "finalize":
                    # Finalize stream
                    result = await streaming_service.finalize_stream(
                        session_id=session_id, organization_id=organization_id, private_key_encrypted=private_key_encrypted
                    )

                    await connection_manager.send_message(session_id, result)
                    break  # Close connection after finalization

                elif message_type == "recover_session":
                    # Recover session
                    recover_session_id = message.get("session_id")
                    result = await streaming_service.recover_session(recover_session_id)

                    await connection_manager.send_message(session_id, result)

                else:
                    # Unknown message type
                    await connection_manager.send_message(session_id, {"type": "error", "message": f"Unknown message type: {message_type}"})

            except json.JSONDecodeError:
                await connection_manager.send_message(session_id, {"type": "error", "message": "Invalid JSON"})
            except ValueError as e:
                await connection_manager.send_message(session_id, {"type": "error", "message": str(e)})
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
                await connection_manager.send_message(session_id, {"type": "error", "message": "Internal server error"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        # Cleanup
        await connection_manager.disconnect(session_id)
        await streaming_service.disconnect_session(session_id)
        streaming_rate_limiter.reset_session(session_id)


@router.websocket("/chat/stream")
async def websocket_chat_endpoint(websocket: WebSocket, api_key: Optional[str] = Query(None)):
    """
    WebSocket endpoint for chat application integration.

    Protocol:
        Client → Server:
            {"type": "message", "role": "user", "content": "..."}

        Server → Client:
            {"type": "assistant_chunk", "content": "...", "signed": true}
            {"type": "turn_complete", "total_chunks": 10}

    Args:
        websocket: WebSocket connection
        api_key: API key for authentication
    """
    # TODO: Implement chat-specific logic
    # For now, redirect to sign endpoint
    await websocket_sign_endpoint(websocket, session_id=None, api_key=api_key)


@router.get("/sign/stream/sessions/{session_id}/events")
async def sse_events_endpoint(
    session_id: str = Path(...),
    initial_only: bool = Query(False, include_in_schema=False),
    api_key: Optional[str] = Query(None),
    organization: dict = Depends(require_sign_permission),
):
    """
    Server-Sent Events (SSE) endpoint for unidirectional streaming (session scoped).

    Args:
        session_id: Session identifier
        api_key: API key for authentication

    Returns:
        StreamingResponse with SSE events
    """
    if not organization.get("streaming_enabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Streaming requires Professional or Enterprise tier",
        )

    async def event_generator():
        """Generate SSE events."""
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'session_id': session_id})}\n\n"

        if initial_only:
            return

        # Heartbeat loop
        import asyncio

        while True:
            # Send heartbeat
            yield ":heartbeat\n\n"
            await asyncio.sleep(15)

            # TODO: Implement actual event streaming
            # This would pull from a queue or Redis pub/sub

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.get("/sign/stream/stats")
async def get_streaming_stats(organization: Organization = Depends(get_current_organization)):
    """
    Get streaming statistics for organization.

    Args:
        organization: Authenticated organization

    Returns:
        Streaming statistics
    """
    active_connections = connection_manager.get_connection_count(organization.organization_id)

    return {
        "success": True,
        "organization_id": organization.organization_id,
        "active_connections": active_connections,
        "max_connections": connection_manager.max_connections_per_org,
    }


@router.get("/sign/stream/health", tags=["Admin"])
async def streaming_health_check(
    organization: dict = Depends(require_super_admin_dep),
):
    """
    Health check endpoint for streaming service.

    Returns:
        Health status of streaming components
    """
    _ = organization

    health_status: Dict[str, Any] = {"status": "healthy", "service": "streaming", "components": {}}

    # Check Redis connection
    try:
        if session_service.redis_client:
            await cast(Any, session_service.redis_client.ping())
            health_status["components"]["redis"] = {"status": "healthy", "message": "Connected"}
        else:
            health_status["components"]["redis"] = {"status": "degraded", "message": "Running in-memory mode (no Redis)"}
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["redis"] = {"status": "unhealthy", "message": f"Redis error: {str(e)}"}

    # Check connection manager
    try:
        total_connections = connection_manager.get_connection_count()
        health_status["components"]["connection_manager"] = {
            "status": "healthy",
            "active_connections": total_connections,
            "max_connections_per_org": connection_manager.max_connections_per_org,
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["connection_manager"] = {"status": "unhealthy", "message": f"Error: {str(e)}"}

    # Check rate limiter
    try:
        health_status["components"]["rate_limiter"] = {"status": "healthy", "message": "Operational"}
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["rate_limiter"] = {"status": "unhealthy", "message": f"Error: {str(e)}"}

    return health_status


@router.get("/sign/stream/runs/{run_id}")
async def get_stream_run(
    run_id: str,
    organization: dict = Depends(require_sign_permission),
):
    """Return persisted streaming run state."""

    state = await session_service.get_stream_state(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")

    state_org_id = state.get("organization_id")
    if not state_org_id or state_org_id != organization["organization_id"]:
        raise HTTPException(status_code=404, detail="Run not found")

    state_for_response = {k: v for k, v in state.items() if k != "organization_id"}
    return {"run_id": run_id, "state": state_for_response}
