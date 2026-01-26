"""
Synthetic benchmark for batch signing throughput.

Uses in-memory SQLite plus mocked signing to measure scheduler overhead.
"""

import argparse
import asyncio
import time
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.batch import BatchItem, BatchItemStatus, BatchRequest
from app.models.response_models import SignResponse
from app.schemas.batch import BatchItemPayload, BatchSignRequest
from app.services import batch_service as batch_service_module
from app.services.batch_service import BatchService, WorkerResult


async def run_benchmark(documents: int, worker_limit: int, simulate_ms: float, logic_only: bool) -> None:
    delay = simulate_ms / 1000
    service: BatchService

    if logic_only:
        class BenchmarkBatchService(BatchService):
            async def _process_sign_item(
                self,
                *,
                request: BatchSignRequest,
                organization: Dict[str, Any],
                item: BatchItemPayload,
                duration_start: float,
            ) -> WorkerResult:
                await asyncio.sleep(delay)
                return WorkerResult(
                    document_id=item.document_id,
                    state=BatchItemStatus.SUCCESS,
                    duration_ms=int(simulate_ms),
                )

        service = BenchmarkBatchService(worker_limit=worker_limit, max_items=documents)
    else:
        service = BatchService(worker_limit=worker_limit, max_items=documents)
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as conn:
            await conn.run_sync(BatchRequest.__table__.create)
            await conn.run_sync(BatchItem.__table__.create)

        async def fake_execute_signing(*, document_id, **_):
            await asyncio.sleep(delay)
            return SignResponse(
                success=True,
                document_id=document_id,
                signed_text="signed",
                total_sentences=1,
                verification_url="http://verify.local",
            )

        setattr(batch_service_module, "execute_signing", fake_execute_signing)
        batch_service_module.async_session_factory = session_factory

    organization = {
        "organization_id": "org_bench",
        "organization_name": "Benchmark Org",
        "api_key": "bench-key",
        "is_demo": True,
    }
    items = [BatchItemPayload(document_id=f"doc-{i}", text=f"payload {i}") for i in range(documents)]
    request = BatchSignRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key=str(uuid4()),
        items=items,
    )

    start = time.perf_counter()
    if logic_only:
        results = await service._run_workers(request=request, organization=organization, request_type=batch_service_module.BatchRequestType.SIGN)
        duration = time.perf_counter() - start
        success = all(result.state == BatchItemStatus.SUCCESS for result in results)
    else:
        async with batch_service_module.async_session_factory() as session:
            response = await service.sign_batch(
                db=session,
                request=request,
                organization=organization,
                correlation_id="bench",
            )
        duration = time.perf_counter() - start
        success = response.success

    docs_per_sec = documents / duration
    print(f"Processed {documents} docs in {duration:.3f}s ({docs_per_sec:.1f} docs/sec)")
    print("Worker limit:", worker_limit)
    print(f"Simulated latency per doc: {simulate_ms}ms")
    print("Logic only run:" if logic_only else "Full stack run:")
    print("Success:", success)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch signing benchmark")
    parser.add_argument("--documents", type=int, default=100)
    parser.add_argument("--worker-limit", type=int, default=8)
    parser.add_argument("--simulate-ms", type=float, default=10.0)
    parser.add_argument("--logic-only", action="store_true", help="Bypass database writes to measure worker throughput")
    args = parser.parse_args()
    asyncio.run(
        run_benchmark(
            documents=args.documents,
            worker_limit=args.worker_limit,
            simulate_ms=args.simulate_ms,
            logic_only=args.logic_only,
        )
    )
