"""
Batch processing service for bulk signing and verification.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory
from app.models.batch import (
    DEFAULT_RETENTION_DAYS,
    BatchItem,
    BatchItemStatus,
    BatchRequest,
    BatchRequestType,
    BatchStatus,
)
from app.models.request_models import SignRequest
from app.schemas.batch import (
    BatchItemPayload,
    BatchItemResult,
    BatchResponseData,
    BatchResponseEnvelope,
    BatchSignRequest,
    BatchSummary,
    BatchVerifyRequest,
)
from app.observability.metrics import increment
from app.schemas.embeddings import EncodeWithEmbeddingsRequest
from app.services.embedding_executor import encode_document_with_embeddings
from app.services.idempotency_service import idempotency_service
from app.services.signing_executor import execute_signing
from app.services.verification_logic import build_verdict, determine_reason_code, execute_verification

logger = logging.getLogger(__name__)


@dataclass
class WorkerResult:
    """Container for per-item worker output."""

    document_id: str
    state: BatchItemStatus
    signed_text: Optional[str] = None
    embedded_content: Optional[str] = None
    verdict_payload: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    statistics: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0

    def api_status(self) -> str:
        if self.state == BatchItemStatus.SUCCESS:
            return "ok"
        if self.state == BatchItemStatus.SKIPPED:
            return "skipped"
        return "error"


class BatchService:
    """Coordinates batch request lifecycle."""

    def __init__(self, worker_limit: int = 8, max_items: int = 100):
        self.worker_limit = worker_limit
        self.max_items = max_items

    async def sign_batch(
        self,
        *,
        db: AsyncSession,
        request: BatchSignRequest,
        organization: Dict[str, Any],
        correlation_id: str,
    ) -> BatchResponseEnvelope:
        """Process batch signing."""

        return await self._process_batch(
            db=db,
            request=request,
            organization=organization,
            correlation_id=correlation_id,
            request_type=BatchRequestType.SIGN,
        )

    async def verify_batch(
        self,
        *,
        db: AsyncSession,
        request: BatchVerifyRequest,
        organization: Dict[str, Any],
        correlation_id: str,
    ) -> BatchResponseEnvelope:
        """Process batch verification."""

        return await self._process_batch(
            db=db,
            request=request,
            organization=organization,
            correlation_id=correlation_id,
            request_type=BatchRequestType.VERIFY,
        )

    async def _process_batch(
        self,
        *,
        db: AsyncSession,
        request: BatchSignRequest | BatchVerifyRequest,
        organization: Dict[str, Any],
        correlation_id: str,
        request_type: BatchRequestType,
    ) -> BatchResponseEnvelope:
        if len(request.items) > self.max_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "E_BATCH_TOO_LARGE",
                    "message": f"Batch size exceeds {self.max_items} items",
                },
            )

        organization_id = organization["organization_id"]
        payload_hash = self._hash_payload(request)

        existing = await self._get_existing_batch(
            db=db,
            organization_id=organization_id,
            idempotency_key=request.idempotency_key,
        )
        if existing:
            if existing.payload_hash != payload_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "E_IDEMPOTENCY_MISMATCH",
                        "message": "Idempotency key already used with different payload",
                    },
                )
            return await self._build_response_from_existing(
                db=db,
                batch_request=existing,
                correlation_id=correlation_id,
            )

        scope = f"{request_type.value}:{organization_id}"
        cache_ok = await idempotency_service.register(
            scope=scope,
            idem_key=request.idempotency_key,
            payload_hash=payload_hash,
            ttl_seconds=DEFAULT_RETENTION_DAYS * 24 * 3600,
        )
        if not cache_ok:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "E_IDEMPOTENT_REPLAY",
                    "message": "Idempotency key rejected by cache",
                },
            )

        batch_request = BatchRequest(
            organization_id=organization_id,
            api_key=organization.get("api_key", ""),
            request_type=request_type,
            mode=request.mode,
            segmentation_level=getattr(request, "segmentation_level", None),
            idempotency_key=request.idempotency_key,
            payload_hash=payload_hash,
            status=BatchStatus.PENDING,
            item_count=len(request.items),
            request_metadata={"fail_fast": request.fail_fast},
            expires_at=BatchRequest.default_expiry(),
        )
        db.add(batch_request)
        await db.flush()
        batch_request.started_at = datetime.now(timezone.utc)

        started_at = time.perf_counter()
        worker_results = await self._run_workers(request=request, organization=organization, request_type=request_type)
        duration_ms = int((time.perf_counter() - started_at) * 1000)

        success_count = sum(1 for result in worker_results if result.state == BatchItemStatus.SUCCESS)
        failure_count = sum(1 for result in worker_results if result.state == BatchItemStatus.FAILED)

        batch_request.success_count = success_count
        batch_request.failure_count = failure_count
        batch_request.completed_at = datetime.now(timezone.utc)
        batch_request.status = (
            BatchStatus.COMPLETED if failure_count == 0 else BatchStatus.FAILED
        )

        await self._persist_results(db=db, batch_request=batch_request, results=worker_results)
        await db.commit()

        summary = BatchSummary(
            total_items=len(worker_results),
            success_count=success_count,
            failure_count=failure_count,
            mode=request.mode,
            status=batch_request.status.value,
            duration_ms=duration_ms,
            started_at=batch_request.started_at.isoformat() if batch_request.started_at else None,
            completed_at=batch_request.completed_at.isoformat() if batch_request.completed_at else None,
        )

        data = BatchResponseData(
            results=[self._to_item_result(result) for result in worker_results],
            summary=summary,
        )

        metric_name = "batch_sign_requests" if request_type == BatchRequestType.SIGN else "batch_verify_requests"
        increment(metric_name)

        return BatchResponseEnvelope(
            success=failure_count == 0,
            batch_id=batch_request.id,
            data=data,
            error=None,
            correlation_id=correlation_id,
        )

    async def _get_existing_batch(
        self,
        *,
        db: AsyncSession,
        organization_id: str,
        idempotency_key: str,
    ) -> Optional[BatchRequest]:
        stmt = select(BatchRequest).where(
            BatchRequest.organization_id == organization_id,
            BatchRequest.idempotency_key == idempotency_key,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _build_response_from_existing(
        self,
        *,
        db: AsyncSession,
        batch_request: BatchRequest,
        correlation_id: str,
    ) -> BatchResponseEnvelope:
        stmt = (
            select(BatchItem)
            .where(BatchItem.batch_request_id == batch_request.id)
            .order_by(BatchItem.created_at)
        )
        items_result = await db.execute(stmt)
        items = list(items_result.scalars().all())
        worker_results = [self._from_batch_item(item) for item in items]

        summary = BatchSummary(
            total_items=batch_request.item_count,
            success_count=batch_request.success_count,
            failure_count=batch_request.failure_count,
            mode=batch_request.mode,
            status=batch_request.status.value,
            duration_ms=0,
            started_at=batch_request.started_at.isoformat() if batch_request.started_at else None,
            completed_at=batch_request.completed_at.isoformat() if batch_request.completed_at else None,
        )
        data = BatchResponseData(
            results=[self._to_item_result(result) for result in worker_results],
            summary=summary,
        )
        return BatchResponseEnvelope(
            success=batch_request.failure_count == 0,
            batch_id=batch_request.id,
            data=data,
            error=None,
            correlation_id=correlation_id,
        )

    async def _run_workers(
        self,
        *,
        request: BatchSignRequest | BatchVerifyRequest,
        organization: Dict[str, Any],
        request_type: BatchRequestType,
    ) -> List[WorkerResult]:
        semaphore = asyncio.Semaphore(self.worker_limit)
        tasks = []
        pending_meta = {}

        for item in request.items:
            task = asyncio.create_task(
                self._run_single_item(
                    semaphore=semaphore,
                    request=request,
                    organization=organization,
                    request_type=request_type,
                    item=item,
                )
            )
            tasks.append(task)
            pending_meta[task] = item

        results: List[WorkerResult] = []
        pending = set(tasks)
        try:
            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for completed in done:
                    result = await completed
                    results.append(result)
                    pending_meta.pop(completed, None)
                    if request.fail_fast and result.state == BatchItemStatus.FAILED:
                        for task in pending:
                            task.cancel()
                        if pending:
                            await asyncio.gather(*pending, return_exceptions=True)
                        pending.clear()
                        break
        finally:
            skipped_items = [pending_meta[task] for task in pending_meta]
            for item in skipped_items:
                results.append(
                    WorkerResult(
                        document_id=item.document_id,
                        state=BatchItemStatus.SKIPPED,
                        statistics={},
                    )
                )

        return results

    async def _run_single_item(
        self,
        *,
        semaphore: asyncio.Semaphore,
        request: BatchSignRequest | BatchVerifyRequest,
        organization: Dict[str, Any],
        request_type: BatchRequestType,
        item: BatchItemPayload,
    ) -> WorkerResult:
        async with semaphore:
            start = time.perf_counter()
            try:
                if request_type == BatchRequestType.SIGN:
                    return await self._process_sign_item(
                        request=request,
                        organization=organization,
                        item=item,
                        duration_start=start,
                    )
                return await self._process_verify_item(
                    item=item,
                    duration_start=start,
                )
            except HTTPException as exc:
                duration_ms = int((time.perf_counter() - start) * 1000)
                detail = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
                code = detail.get("code", "E_BATCH_ITEM")
                message = detail.get("message", "Batch item failed")
                return WorkerResult(
                    document_id=item.document_id,
                    state=BatchItemStatus.FAILED,
                    error_code=code,
                    error_message=message,
                    statistics={"duration_ms": duration_ms},
                    duration_ms=duration_ms,
                )
            except Exception as exc:  # pragma: no cover - defensive
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.error("Batch item failed: %s", exc, exc_info=True)
                return WorkerResult(
                    document_id=item.document_id,
                    state=BatchItemStatus.FAILED,
                    error_code="E_BATCH_ITEM",
                    error_message=str(exc),
                    statistics={"duration_ms": duration_ms},
                    duration_ms=duration_ms,
                )

    async def _process_sign_item(
        self,
        *,
        request: BatchSignRequest,
        organization: Dict[str, Any],
        item: BatchItemPayload,
        duration_start: float,
    ) -> WorkerResult:
        async with async_session_factory() as worker_session:
            if request.mode == "c2pa":
                sign_request = SignRequest(
                    text=item.text,
                    document_id=item.document_id,
                    document_title=item.title or item.document_id,
                )
                response = await execute_signing(
                    request=sign_request,
                    organization=organization,
                    db=worker_session,
                    document_id=item.document_id,
                )
                duration_ms = int((time.perf_counter() - duration_start) * 1000)
                stats = {"total_sentences": response.total_sentences, "duration_ms": duration_ms}
                return WorkerResult(
                    document_id=response.document_id,
                    state=BatchItemStatus.SUCCESS,
                    signed_text=response.signed_text,
                    statistics=stats,
                    duration_ms=duration_ms,
                )

            embed_request = EncodeWithEmbeddingsRequest(
                document_id=item.document_id,
                text=item.text,
                segmentation_level=request.segmentation_level or "sentence",
                metadata=item.metadata,
            )
            response = await encode_document_with_embeddings(
                request=embed_request,
                organization=organization,
                db=worker_session,
            )
            duration_ms = int((time.perf_counter() - duration_start) * 1000)
            stats = dict(response.statistics or {})
            stats["duration_ms"] = duration_ms
            return WorkerResult(
                document_id=response.document_id,
                state=BatchItemStatus.SUCCESS,
                embedded_content=response.embedded_content,
                statistics=stats,
                duration_ms=duration_ms,
            )

    async def _process_verify_item(
        self,
        *,
        item: BatchItemPayload,
        duration_start: float,
    ) -> WorkerResult:
        async with async_session_factory() as worker_session:
            execution = await execute_verification(payload_text=item.text, db=worker_session)
            reason_code = determine_reason_code(execution=execution)
            payload_bytes = len(item.text.encode("utf-8"))
            verdict = build_verdict(
                execution=execution,
                reason_code=reason_code,
                payload_bytes=payload_bytes,
            )
            duration_ms = int((time.perf_counter() - duration_start) * 1000)
            state = BatchItemStatus.SUCCESS if verdict.valid else BatchItemStatus.FAILED
            error_code = None if verdict.valid else "E_VERIFY_TAMPERED"
            error_message = None if verdict.valid else verdict.reason_code
            return WorkerResult(
                document_id=item.document_id,
                state=state,
                verdict_payload=verdict.model_dump(),
                error_code=error_code,
                error_message=error_message,
                statistics={"duration_ms": duration_ms},
                duration_ms=duration_ms,
            )

    async def _persist_results(
        self,
        *,
        db: AsyncSession,
        batch_request: BatchRequest,
        results: Sequence[WorkerResult],
    ) -> None:
        for result in results:
            db.add(
                BatchItem(
                    batch_request_id=batch_request.id,
                    document_id=result.document_id,
                    status=result.state,
                    mode=batch_request.mode,
                    duration_ms=result.duration_ms,
                    error_code=result.error_code,
                    error_message=result.error_message,
                    statistics=result.statistics,
                    result_payload={
                        "signed_text": result.signed_text,
                        "embedded_content": result.embedded_content,
                        "verdict": result.verdict_payload,
                    },
                )
            )

    def _hash_payload(self, request: BatchSignRequest | BatchVerifyRequest) -> str:
        normalized = {
            "mode": request.mode,
            "segmentation_level": getattr(request, "segmentation_level", None),
            "items": [
                {
                    "document_id": item.document_id,
                    "text_hash": hashlib.sha256(item.text.encode("utf-8")).hexdigest(),
                    "title": item.title,
                    "metadata": item.metadata,
                }
                for item in request.items
            ],
        }
        serialized = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _to_item_result(self, result: WorkerResult) -> BatchItemResult:
        verdict = None
        if result.verdict_payload:
            verdict = build_verdict_from_payload(result.verdict_payload)
        stats = dict(result.statistics)
        if "duration_ms" not in stats:
            stats["duration_ms"] = result.duration_ms
        return BatchItemResult(
            document_id=result.document_id,
            status=result.api_status(),
            signed_text=result.signed_text,
            embedded_content=result.embedded_content,
            verdict=verdict,
            error_code=result.error_code,
            error_message=result.error_message,
            statistics=stats,
        )

    def _from_batch_item(self, item: BatchItem) -> WorkerResult:
        payload = item.result_payload or {}
        return WorkerResult(
            document_id=item.document_id,
            state=item.status,
            signed_text=payload.get("signed_text"),
            embedded_content=payload.get("embedded_content"),
            verdict_payload=payload.get("verdict"),
            error_code=item.error_code,
            error_message=item.error_message,
            statistics=item.statistics or {},
            duration_ms=item.duration_ms or (item.statistics or {}).get("duration_ms", 0),
        )


def build_verdict_from_payload(payload: Dict[str, Any]) -> Optional[Any]:
    """Reconstruct VerifyVerdict without importing Pydantic at module load time."""

    from app.models.response_models import VerifyVerdict

    return VerifyVerdict(**payload)


batch_service = BatchService(
    worker_limit=getattr(settings, "batch_worker_limit", 8),
    max_items=getattr(settings, "batch_max_items", 100),
)
