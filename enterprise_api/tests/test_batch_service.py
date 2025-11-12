from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.batch import BatchRequest
from app.models.response_models import SignResponse, VerifyVerdict
from app.schemas.batch import BatchItemPayload, BatchSignRequest, BatchVerifyRequest
from app.services.batch_service import BatchService


@pytest.mark.asyncio
async def test_batch_sign_c2pa_persists_results(monkeypatch, async_engine):
    test_session = async_sessionmaker(async_engine, expire_on_commit=False)
    monkeypatch.setattr("app.services.batch_service.async_session_factory", test_session)

    async def fake_execute_signing(*, request, organization, db, document_id):
        return SignResponse(
            success=True,
            document_id=document_id,
            signed_text=f"signed::{document_id}",
            total_sentences=3,
            verification_url="http://local/verify",
        )

    monkeypatch.setattr("app.services.batch_service.execute_signing", fake_execute_signing)
    organization = {
        "organization_id": "org_demo",
        "organization_name": "Demo Org",
        "api_key": "demo-key",
        "is_demo": True,
    }
    request = BatchSignRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key=str(uuid4()),
        items=[
            BatchItemPayload(document_id="doc-1", text="First content", title="One"),
            BatchItemPayload(document_id="doc-2", text="Second content", title="Two"),
        ],
    )
    service = BatchService(worker_limit=2, max_items=10)

    async with test_session() as session:
        response = await service.sign_batch(
            db=session,
            request=request,
            organization=organization,
            correlation_id="cid-1",
        )
        assert response.success
        assert response.data.summary.success_count == 2
        assert all(item.status == "ok" for item in response.data.results)

        result = await session.execute(select(BatchRequest))
        batch_row = result.scalar_one()
        assert batch_row.success_count == 2


@pytest.mark.asyncio
async def test_batch_sign_idempotency_conflict(monkeypatch, async_engine):
    test_session = async_sessionmaker(async_engine, expire_on_commit=False)
    monkeypatch.setattr("app.services.batch_service.async_session_factory", test_session)

    async def fake_execute_signing(*args, **kwargs):
        return SignResponse(
            success=True,
            document_id="doc-1",
            signed_text="signed",
            total_sentences=1,
            verification_url="http://local",
        )

    monkeypatch.setattr("app.services.batch_service.execute_signing", fake_execute_signing)
    organization = {
        "organization_id": "org_demo",
        "organization_name": "Demo Org",
        "api_key": "demo-key",
        "is_demo": True,
    }
    request = BatchSignRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key="same-key",
        items=[BatchItemPayload(document_id="doc-1", text="alpha")],
    )
    service = BatchService(worker_limit=1, max_items=5)

    async with test_session() as session:
        await service.sign_batch(
            db=session,
            request=request,
            organization=organization,
            correlation_id="cid-1",
        )

    request_conflict = BatchSignRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key="same-key",
        items=[BatchItemPayload(document_id="doc-1", text="beta")],
    )

    async with test_session() as session:
        with pytest.raises(HTTPException):
            await service.sign_batch(
                db=session,
                request=request_conflict,
                organization=organization,
                correlation_id="cid-2",
            )


@pytest.mark.asyncio
async def test_batch_verify_mixed_results(monkeypatch, async_engine):
    test_session = async_sessionmaker(async_engine, expire_on_commit=False)
    monkeypatch.setattr("app.services.batch_service.async_session_factory", test_session)

    class DummyExecution:
        def __init__(self, is_valid: bool):
            self.is_valid = is_valid
            self.manifest = {}
            self.missing_signers = set()
            self.revoked_signers = set()
            self.signer_id = "org_demo"
            self.resolved_cert = None
            self.duration_ms = 5
            self.exception_message = None

    async def fake_execute_verification(*, payload_text, **_):
        return DummyExecution(is_valid="good" in payload_text)

    def fake_reason_code(*, execution):
        return "OK" if execution.is_valid else "TAMPERED"

    def fake_build_verdict(*, execution, **__):
        return VerifyVerdict(
            valid=execution.is_valid,
            tampered=not execution.is_valid,
            reason_code="OK" if execution.is_valid else "TAMPERED",
            signer_id="org_demo",
            signer_name="Demo Org",
            timestamp=None,
            details={},
        )

    monkeypatch.setattr("app.services.batch_service.execute_verification", fake_execute_verification)
    monkeypatch.setattr("app.services.batch_service.determine_reason_code", fake_reason_code)
    monkeypatch.setattr("app.services.batch_service.build_verdict", fake_build_verdict)

    organization = {
        "organization_id": "org_demo",
        "organization_name": "Demo Org",
        "api_key": "demo-key",
        "is_demo": True,
    }
    request = BatchVerifyRequest(
        mode="c2pa",
        segmentation_level="sentence",
        idempotency_key="verify-key",
        items=[
            BatchItemPayload(document_id="doc-a", text="good payload"),
            BatchItemPayload(document_id="doc-b", text="bad payload"),
        ],
    )
    service = BatchService(worker_limit=2, max_items=10)

    async with test_session() as session:
        response = await service.verify_batch(
            db=session,
            request=request,
            organization=organization,
            correlation_id="cid-verify",
        )
        assert not response.success
        statuses = {item.document_id: item.status for item in response.data.results}
        assert statuses["doc-a"] == "ok"
        assert statuses["doc-b"] == "error"
