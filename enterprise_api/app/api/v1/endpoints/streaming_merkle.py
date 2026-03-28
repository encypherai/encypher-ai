"""
Streaming Merkle Tree API Endpoints (TEAM_044 - Patent FIG. 5).

These endpoints enable real-time Merkle tree construction for streaming
content signing, ideal for LLM output where content is generated incrementally.
"""

import logging
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.schemas.streaming import (
    StreamMerkleFinalizeRequest,
    StreamMerkleFinalizeResponse,
    StreamMerkleSegmentRequest,
    StreamMerkleSegmentResponse,
    StreamMerkleStartRequest,
    StreamMerkleStartResponse,
    StreamMerkleStatusRequest,
    StreamMerkleStatusResponse,
)
from app.services.streaming_merkle_service import streaming_merkle_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream/merkle", tags=["Streaming Merkle"])


@router.post("/start", response_model=StreamMerkleStartResponse)
async def start_streaming_merkle_session(
    request: StreamMerkleStartRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> StreamMerkleStartResponse:
    """
    Start a new streaming Merkle tree construction session.

    This initiates a session that allows segments to be added incrementally,
    ideal for real-time LLM output signing where content is generated token-by-token.

    **Tier Requirement:** Professional+

    Patent Reference: FIG. 5 - Streaming Merkle Tree Construction
    """
    organization_id = organization["organization_id"]

    # TEAM_145: Streaming Merkle tree available to all tiers (free/enterprise/strategic_partner)

    try:
        session = await streaming_merkle_service.start_session(
            document_id=request.document_id,
            organization_id=organization_id,
            segmentation_level=request.segmentation_level,
            metadata=request.metadata,
            buffer_size=request.buffer_size,
            timeout_seconds=request.auto_finalize_timeout_seconds,
        )

        logger.info(f"Started streaming Merkle session {session.session_id} for org {organization_id}, doc {request.document_id}")

        return StreamMerkleStartResponse(
            success=True,
            session_id=session.session_id,
            document_id=session.document_id,
            expires_at=session.expires_at,
            buffer_size=session.buffer_size,
            message="Streaming session started. Add segments using /stream/merkle/segment",
        )

    except Exception as e:
        logger.error(f"Failed to start streaming session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "SESSION_START_FAILED", "message": str(e)},
        )


@router.post("/segment", response_model=StreamMerkleSegmentResponse)
async def add_segment_to_session(
    request: StreamMerkleSegmentRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> StreamMerkleSegmentResponse:
    """
    Add a segment to an active streaming Merkle session.

    Segments are buffered and combined into the Merkle tree incrementally.
    The tree is constructed using a bounded buffer approach for memory efficiency.

    Set `is_final=true` to finalize the session after adding this segment.
    """
    try:
        session, segment_hash = await streaming_merkle_service.add_segment(
            session_id=request.session_id,
            segment_text=request.segment_text,
            segment_index=request.segment_index,
            flush_buffer=request.flush_buffer,
        )

        # If this is the final segment, finalize the session
        if request.is_final:
            from app.services.embedding_service import EmbeddingService
            from app.utils.crypto_utils import get_demo_private_key, load_organization_private_key

            organization_id = organization["organization_id"]
            is_demo = organization.get("is_demo", False)
            cert_chain_pem = None

            if is_demo or organization_id.startswith("user_"):
                private_key = get_demo_private_key()
            else:
                private_key = await load_organization_private_key(organization_id, db)
                try:
                    from sqlalchemy import text as sa_text

                    row = await db.execute(
                        sa_text("SELECT certificate_pem, certificate_chain FROM organizations WHERE id = :org_id"),
                        {"org_id": organization_id},
                    )
                    cert_row = row.one_or_none()
                    if cert_row:
                        combined = ((cert_row[0] or "").strip() + "\n" + (cert_row[1] or "").strip()).strip()
                        cert_chain_pem = combined if combined else None
                except Exception as exc:
                    logger.warning("Failed to load cert chain for org %s: %s", organization_id, exc)

            embedding_service = EmbeddingService(private_key, organization_id, cert_chain_pem=cert_chain_pem)

            session, root_hash, _ = await streaming_merkle_service.finalize_session(
                session_id=request.session_id,
                db=db,
                embedding_service=embedding_service,
                embed_manifest=False,  # Don't embed on segment add
            )

            return StreamMerkleSegmentResponse(
                success=True,
                session_id=session.session_id,
                segment_index=session.total_segments - 1,
                segment_hash=segment_hash,
                buffer_count=0,
                total_segments=session.total_segments,
                intermediate_root=root_hash,
                message=f"Final segment added. Session finalized with root: {root_hash[:16]}...",
            )

        return StreamMerkleSegmentResponse(
            success=True,
            session_id=session.session_id,
            segment_index=session.total_segments - 1,
            segment_hash=segment_hash,
            buffer_count=session.buffer_count,
            total_segments=session.total_segments,
            intermediate_root=session.intermediate_root,
            message=f"Segment {session.total_segments - 1} added successfully",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SEGMENT_ADD_FAILED", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Failed to add segment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "SEGMENT_ADD_FAILED", "message": str(e)},
        )


@router.post("/finalize", response_model=StreamMerkleFinalizeResponse)
async def finalize_streaming_session(
    request: StreamMerkleFinalizeRequest,
    organization: Dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> StreamMerkleFinalizeResponse:
    """
    Finalize a streaming Merkle session and compute the final root.

    This completes the tree construction, computes the final root hash,
    and optionally embeds a C2PA manifest into the full document.
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    try:
        # Load private key for embedding
        from app.services.embedding_service import EmbeddingService
        from app.utils.crypto_utils import get_demo_private_key, load_organization_private_key

        is_demo = organization.get("is_demo", False)
        cert_chain_pem = None

        if is_demo or organization_id.startswith("user_"):
            private_key = get_demo_private_key()
        else:
            private_key = await load_organization_private_key(organization_id, db)
            try:
                from sqlalchemy import text as sa_text

                row = await db.execute(
                    sa_text("SELECT certificate_pem, certificate_chain FROM organizations WHERE id = :org_id"),
                    {"org_id": organization_id},
                )
                cert_row = row.one_or_none()
                if cert_row:
                    combined = ((cert_row[0] or "").strip() + "\n" + (cert_row[1] or "").strip()).strip()
                    cert_chain_pem = combined if combined else None
            except Exception as exc:
                logger.warning("Failed to load cert chain for org %s: %s", organization_id, exc)

        embedding_service = EmbeddingService(private_key, organization_id, cert_chain_pem=cert_chain_pem)

        session, root_hash, embedded_content = await streaming_merkle_service.finalize_session(
            session_id=request.session_id,
            db=db,
            embedding_service=embedding_service,
            embed_manifest=request.embed_manifest,
            manifest_mode=request.manifest_mode,
            action=request.action,
        )

        # Calculate tree depth
        tree_depth = 0
        n = session.total_segments
        while n > 1:
            tree_depth += 1
            n = (n + 1) // 2

        # Extract instance_id if manifest was embedded
        instance_id = None
        if request.embed_manifest and embedded_content:
            try:
                from encypher.core.unicode_metadata import UnicodeMetadata

                extracted = UnicodeMetadata.extract_metadata(embedded_content)
                if extracted:
                    instance_id = extracted.get("instance_id")
            except Exception:
                pass

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Finalized streaming session {request.session_id}: "
            f"root={root_hash[:16]}..., segments={session.total_segments}, "
            f"time={processing_time_ms:.2f}ms"
        )

        return StreamMerkleFinalizeResponse(
            success=True,
            session_id=session.session_id,
            document_id=session.document_id,
            root_hash=root_hash,
            tree_depth=tree_depth,
            total_segments=session.total_segments,
            embedded_content=embedded_content if request.embed_manifest else None,
            instance_id=instance_id,
            processing_time_ms=round(processing_time_ms, 2),
            message=f"Session finalized successfully with {session.total_segments} segments",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "FINALIZE_FAILED", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Failed to finalize session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "FINALIZE_FAILED", "message": str(e)},
        )


@router.post("/status", response_model=StreamMerkleStatusResponse)
async def get_session_status(
    request: StreamMerkleStatusRequest,
    organization: Dict = Depends(get_current_organization),
) -> StreamMerkleStatusResponse:
    """
    Check the status of a streaming Merkle session.
    """
    session = await streaming_merkle_service.get_session(request.session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": f"Session {request.session_id} not found"},
        )

    # Verify organization owns this session
    organization_id = organization["organization_id"]
    if session.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCESS_DENIED", "message": "Session belongs to different organization"},
        )

    return StreamMerkleStatusResponse(
        success=True,
        session_id=session.session_id,
        document_id=session.document_id,
        status=session.status,
        total_segments=session.total_segments,
        buffer_count=session.buffer_count,
        intermediate_root=session.intermediate_root,
        created_at=session.created_at,
        expires_at=session.expires_at,
        last_activity=session.last_activity,
    )
