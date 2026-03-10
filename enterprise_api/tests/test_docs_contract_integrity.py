from __future__ import annotations

from pathlib import Path

_DOC_ROOT = Path(__file__).resolve().parents[1] / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_required_contract_docs_exist() -> None:
    required = (
        _DOC_ROOT / "MERKLE_ASSERTION_SCHEMA.md",
        _DOC_ROOT / "VERIFICATION_TRUST_MODEL.md",
    )
    missing = [str(path.relative_to(_DOC_ROOT)) for path in required if not path.exists()]
    assert not missing, "Missing required contract docs:\n" + "\n".join(f"- {name}" for name in missing)


def test_merkle_assertion_contract_doc_has_required_fields() -> None:
    text = _read(_DOC_ROOT / "MERKLE_ASSERTION_SCHEMA.md")
    lowered = text.lower()

    required_tokens = [
        "com.encypher.merkle.v1",
        "root_hash",
        "root_id",
        "segmentation_level",
        "total_segments",
        "version",
    ]
    missing = [token for token in required_tokens if token not in lowered]
    assert not missing, "MERKLE_ASSERTION_SCHEMA.md is missing required contract fields:\n" + "\n".join(f"- {token}" for token in missing)


def test_verification_trust_model_doc_covers_primary_and_fallback_paths() -> None:
    text = _read(_DOC_ROOT / "VERIFICATION_TRUST_MODEL.md")
    lowered = text.lower()

    required_topics = [
        "c2pa",
        "primary",
        "fallback",
        "micro",
        "legacy_safe",
        "reason_code",
        "untrusted_signer",
        "doc_revoked",
    ]
    missing = [topic for topic in required_topics if topic not in lowered]
    assert not missing, "VERIFICATION_TRUST_MODEL.md is missing required trust model topics:\n" + "\n".join(f"- {topic}" for topic in missing)


def test_customer_docs_no_removed_endpoint_or_old_webhook_event_refs() -> None:
    customer_docs = (
        _DOC_ROOT / "API.md",
        _DOC_ROOT / "QUICKSTART.md",
        _DOC_ROOT / "STREAMING_API.md",
        _DOC_ROOT / "THREAT_MODEL.md",
        _DOC_ROOT / "PERFORMANCE_SCALE.md",
    )

    forbidden = [
        "/sign/advanced",
        "certificate.issued",
        "verification.tamper_detected",
    ]

    offending: list[tuple[str, str]] = []
    for path in customer_docs:
        text = _read(path).lower()
        for needle in forbidden:
            if needle in text:
                offending.append((path.name, needle))

    assert not offending, "Stale endpoint/event references detected in customer-facing docs:\n" + "\n".join(
        f"- {name}: {needle}" for name, needle in offending
    )


def test_streaming_doc_covers_stream_sign_sse_contract() -> None:
    text = _read(_DOC_ROOT / "STREAMING_API.md")
    lowered = text.lower()

    required_tokens = [
        "/api/v1/sign/stream",
        "/api/v1/sign/stream/runs/{run_id}",
        "event: start",
        "event: progress",
        "event: partial",
        "event: final",
        "event: done",
    ]

    missing = [token for token in required_tokens if token not in lowered]
    assert not missing, "STREAMING_API.md is missing required stream-sign SSE contract references:\n" + "\n".join(f"- {token}" for token in missing)
