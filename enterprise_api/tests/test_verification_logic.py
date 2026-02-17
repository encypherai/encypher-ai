from types import SimpleNamespace

from app.services.verification_logic import VerificationExecution, build_verdict


def _make_execution(*, signer_id: str | None, manifest: dict, resolved_cert=None) -> VerificationExecution:
    return VerificationExecution(
        is_valid=True,
        signer_id=signer_id,
        manifest=manifest,
        missing_signers=set(),
        revoked_signers=set(),
        resolved_cert=resolved_cert,
        duration_ms=3,
        exception_message=None,
    )


def test_build_verdict_prefers_manifest_custom_publisher_name_when_cert_missing() -> None:
    execution = _make_execution(
        signer_id="org_demo",
        manifest={"custom_metadata": {"publisher_name": "Encypher Newsroom"}},
    )

    verdict = build_verdict(execution=execution, reason_code="OK", payload_bytes=128)

    assert verdict.signer_id == "org_demo"
    assert verdict.signer_name == "Encypher Newsroom"


def test_build_verdict_reads_signer_name_from_nested_manifest_data() -> None:
    execution = _make_execution(
        signer_id="org_demo",
        manifest={"manifest_data": {"custom_metadata": {"publisher_name": "Manifest Publisher"}}},
    )

    verdict = build_verdict(execution=execution, reason_code="OK", payload_bytes=64)

    assert verdict.signer_name == "Manifest Publisher"


def test_build_verdict_prefers_resolved_certificate_name_over_manifest() -> None:
    resolved_cert = SimpleNamespace(
        organization_name="Verified Publisher",
        status=SimpleNamespace(value="active"),
        certificate_rotated_at=None,
    )
    execution = _make_execution(
        signer_id="org_demo",
        manifest={"custom_metadata": {"publisher_name": "Manifest Publisher"}},
        resolved_cert=resolved_cert,
    )

    verdict = build_verdict(execution=execution, reason_code="OK", payload_bytes=64)

    assert verdict.signer_name == "Verified Publisher"


def test_build_verdict_falls_back_to_signer_id_without_identity_metadata() -> None:
    execution = _make_execution(
        signer_id="org_demo",
        manifest={},
    )

    verdict = build_verdict(execution=execution, reason_code="OK", payload_bytes=32)

    assert verdict.signer_name == "org_demo"
