from __future__ import annotations

from pathlib import Path

def _enterprise_api_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


_CUSTOMER_DOCS: tuple[Path, ...] = (
    _enterprise_api_root() / "README.md",
    _enterprise_api_root() / "docs" / "API.md",
    _enterprise_api_root() / "docs" / "QUICKSTART.md",
)


def test_customer_docs_do_not_include_restricted_implementation_details() -> None:
    forbidden_substrings = [
        # Implementation / trade-secret sensitive details
        "unicode variation selectors",
        "u+feff",
        "c2patxt",
        "nfc-normal",
        "nfc normal",
        "exclusions",
        "c2pa.hash.data",
        "wrapper header",
        "jumbf",
        "manifest length",
        "private credential store",
        "trust anchor type",
        # IP / claims marketing language that shouldn't be in customer docs
        "patent-pending",
        "patent pending",
        "claims filed",
        "83 claims",
    ]

    offending: list[tuple[str, str]] = []
    for path in _CUSTOMER_DOCS:
        text = _read_text(path)
        lowered = text.lower()
        for needle in forbidden_substrings:
            if needle in lowered:
                offending.append((path.name, needle))

    assert offending == [], (
        "Restricted wording found in customer-facing docs. "
        "Replace with customer-safe language and keep implementation SSOT internal.\n\n"
        + "\n".join(f"- {doc}: contains '{needle}'" for doc, needle in offending)
    )


def test_customer_docs_do_not_hardcode_tier_quota_numbers() -> None:
    quota_markers = [
        "requests/month",
        "requests per month",
        "monthly_quota",
        "quota_remaining",
    ]

    offending: list[tuple[str, str]] = []

    for path in _CUSTOMER_DOCS:
        text = _read_text(path)
        lowered = text.lower()

        for marker in quota_markers:
            if marker in lowered:
                offending.append((path.name, marker))

        # If a doc discusses quotas/rate limiting, it should point customers to the
        # authoritative quota endpoint rather than embedding tier numbers.
        if any(m in lowered for m in ("requests/month", "requests per month", "rate limit", "quota")):
            if "/api/v1/account/quota" not in lowered and "/account/quota" not in lowered:
                offending.append((path.name, "missing /api/v1/account/quota reference"))

    assert offending == [], (
        "Tier/quota drift risk detected in customer-facing docs. "
        "Avoid hard-coded quota numbers; point customers to /api/v1/account/quota instead.\n\n"
        + "\n".join(f"- {doc}: {detail}" for doc, detail in offending)
    )
