from __future__ import annotations

import re
from pathlib import Path


def test_analytics_usage_stats_schema_matches_dashboard_expectations() -> None:
    """Guardrail: analytics-service must expose the fields the dashboard expects.

    Dashboard expects:
    - total_api_calls
    - total_documents_signed
    - total_verifications
    - success_rate
    - avg_response_time_ms
    - period_start / period_end

    We keep total_keys_generated for backward compatibility, but it must be optional/default.
    """

    repo_root = Path(__file__).resolve().parents[2]
    schema_path = repo_root / "services" / "analytics-service" / "app" / "models" / "schemas.py"
    text = schema_path.read_text(encoding="utf-8")

    # Basic field presence checks.
    assert "class UsageStats" in text
    for field in [
        "total_api_calls",
        "total_documents_signed",
        "total_verifications",
        "success_rate",
        "avg_response_time_ms",
        "period_start",
        "period_end",
    ]:
        assert re.search(rf"\b{re.escape(field)}\b", text), f"Missing field: {field}"

    # total_keys_generated should be optional/defaulted (not required)
    assert re.search(r"total_keys_generated\s*:\s*int\s*=\s*0", text) or re.search(
        r"total_keys_generated\s*:\s*int\s*=\s*Field\(\s*default\s*=\s*0", text
    )
