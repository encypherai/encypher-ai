"""
Lightweight smoke test for the batch service.

Used in CI/local environments where pytest's Postgres dependencies are unavailable.
"""

import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.batch import BatchItem, BatchRequest
from app.models.response_models import SignResponse
from app.schemas.batch import BatchItemPayload, BatchSignRequest
from app.services import batch_service as batch_service_module
from app.services.batch_service import BatchService


async def run() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(BatchRequest.__table__.create)
        await conn.run_sync(BatchItem.__table__.create)

    async def fake_execute_signing(*, request, organization, db, document_id):
        return SignResponse(
            success=True,
            document_id=document_id,
            signed_text=f"signed::{document_id}",
            total_sentences=1,
            verification_url="http://verify.local",
        )

    batch_service_module.execute_signing = fake_execute_signing
    batch_service_module.async_session_factory = session_factory

    service = BatchService(worker_limit=2, max_items=10)
    organization = {
        "organization_id": "org_demo",
        "organization_name": "Demo",
        "api_key": "demo-key",
        "is_demo": True,
    }
    request = BatchSignRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key=str(uuid4()),
        items=[
            BatchItemPayload(document_id="doc-1", text="Sample text one"),
            BatchItemPayload(document_id="doc-2", text="Sample text two"),
        ],
    )

    async with session_factory() as session:
        result = await service.sign_batch(
            db=session,
            request=request,
            organization=organization,
            correlation_id="smoke",
        )
    print("Batch smoke success:", result.success)
    for item in result.data.results:
        print(item.document_id, item.status)


if __name__ == "__main__":
    asyncio.run(run())
