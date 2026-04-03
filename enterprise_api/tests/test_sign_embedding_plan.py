from app.schemas.sign_schemas import SignedDocumentResult, SignOptions, UnifiedSignRequest
from app.services.unified_signing_service import execute_unified_signing


def _apply_embedding_plan(visible_text: str, plan: dict) -> str:
    chars = list(visible_text)
    operations = sorted(plan.get("operations", []), key=lambda op: op["insert_after_index"], reverse=True)
    for op in operations:
        idx = int(op["insert_after_index"])
        marker = op["marker"]
        insert_at = idx + 1
        if idx < -1:
            raise AssertionError("insert_after_index must be >= -1")
        chars[insert_at:insert_at] = list(marker)
    return "".join(chars)


async def _fake_basic_sign(*, document, **kwargs):
    return SignedDocumentResult(
        document_id=document.document_id or "doc_1",
        signed_text=f"{document.text}\ufe00",
        verification_url="https://verify.encypher.com/doc_1",
        total_segments=1,
        metadata=document.metadata,
    )


async def _fake_advanced_sign(*, document, **kwargs):
    return SignedDocumentResult(
        document_id=document.document_id or "doc_1",
        signed_text=f"{document.text}\ufe00",
        verification_url="https://verify.encypher.com/doc_1",
        total_segments=1,
        metadata=document.metadata,
    )


async def test_execute_unified_signing_returns_embedding_plan_when_requested(monkeypatch) -> None:
    source_text = "First sentence. Second sentence."
    request = UnifiedSignRequest(
        text=source_text,
        options=SignOptions(return_embedding_plan=True),
    )

    monkeypatch.setattr("app.services.unified_signing_service._execute_basic_signing", _fake_basic_sign)
    monkeypatch.setattr("app.services.unified_signing_service._execute_advanced_signing", _fake_advanced_sign)

    payload = await execute_unified_signing(
        request=request,
        organization={"organization_id": "org_test", "tier": "free"},
        core_db=None,
        content_db=None,
        correlation_id="req_test",
    )

    document = payload["data"]["document"]
    embedding_plan = document.get("embedding_plan")
    assert embedding_plan is not None
    assert embedding_plan["index_unit"] == "codepoint"
    assert isinstance(embedding_plan["operations"], list)
    assert len(embedding_plan["operations"]) > 0

    reconstructed = _apply_embedding_plan(source_text, embedding_plan)
    assert reconstructed == document["signed_text"]


async def test_execute_unified_signing_omits_embedding_plan_by_default(monkeypatch) -> None:
    request = UnifiedSignRequest(
        text="Plain response by default.",
        options=SignOptions(),
    )

    monkeypatch.setattr("app.services.unified_signing_service._execute_basic_signing", _fake_basic_sign)
    monkeypatch.setattr("app.services.unified_signing_service._execute_advanced_signing", _fake_advanced_sign)

    payload = await execute_unified_signing(
        request=request,
        organization={"organization_id": "org_test", "tier": "free"},
        core_db=None,
        content_db=None,
        correlation_id="req_test",
    )

    document = payload["data"]["document"]
    assert document.get("embedding_plan") is None
