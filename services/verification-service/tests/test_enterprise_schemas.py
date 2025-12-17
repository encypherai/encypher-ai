import pytest
from pydantic import ValidationError

from app.models.enterprise_schemas import ErrorDetail, VerifyRequest, VerifyResponse, VerifyVerdict


def test_verify_request_requires_non_empty_text() -> None:
    with pytest.raises(ValidationError):
        VerifyRequest(text="")


def test_verify_verdict_details_defaults_to_dict() -> None:
    verdict = VerifyVerdict(valid=True, tampered=False, reason_code="OK")
    assert verdict.details == {}


def test_verify_response_success_roundtrip() -> None:
    verdict = VerifyVerdict(
        valid=True,
        tampered=False,
        reason_code="OK",
        signer_id="org_demo",
        signer_name="Demo Organization",
        timestamp=None,
        details={"manifest": {"data": "value"}},
    )
    payload = VerifyResponse(
        success=True,
        correlation_id="req-123",
        data=verdict,
        error=None,
    )

    assert payload.data is not None
    assert payload.data.valid is True
    assert payload.data.details["manifest"] == {"data": "value"}
    assert payload.correlation_id == "req-123"


def test_verify_response_error_roundtrip() -> None:
    payload = VerifyResponse(
        success=False,
        correlation_id="req-456",
        data=None,
        error=ErrorDetail(code="ERR_VERIFY", message="boom", hint="fix"),
    )

    dumped = payload.model_dump()
    assert dumped["success"] is False
    assert dumped["data"] is None
    assert dumped["error"]["code"] == "ERR_VERIFY"
