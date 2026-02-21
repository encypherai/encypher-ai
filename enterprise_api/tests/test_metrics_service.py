import json
import pytest

from app.services.metrics_service import MetricEvent, MetricType, classify_bot


def test_metric_event_to_dict_serializes_metadata_as_json_string() -> None:
    event = MetricEvent(
        metric_type=MetricType.API_CALL,
        organization_id="org_demo",
        endpoint="/api/v1/sign",
        method="POST",
        status_code=500,
        metadata={
            "request_id": "req_123",
            "api_key_prefix": "ency_abc123",
            "error_code": "E_INTERNAL",
            "error_message": "Signing failed",
        },
    )

    payload = event.to_dict()

    assert isinstance(payload.get("metadata"), str)
    parsed = json.loads(payload["metadata"])
    assert parsed["request_id"] == "req_123"
    assert parsed["api_key_prefix"] == "ency_abc123"
    assert parsed["error_code"] == "E_INTERNAL"
    assert parsed["error_message"] == "Signing failed"


# ---------------------------------------------------------------------------
# TEAM_218: New MetricType values
# ---------------------------------------------------------------------------

def test_rights_metric_types_exist() -> None:
    """RSL/rights MetricType values added in TEAM_218 must be present."""
    assert MetricType.RSL_FETCH == "rsl_fetch"
    assert MetricType.RIGHTS_RESOLUTION == "rights_resolution"
    assert MetricType.ROBOTS_TXT_FETCH == "robots_txt_fetch"
    assert MetricType.NOTICE_DELIVERED == "notice_delivered"
    assert MetricType.LICENSING_REQUEST == "licensing_request"


def test_metric_event_accepts_rsl_fetch_type() -> None:
    event = MetricEvent(
        metric_type=MetricType.RSL_FETCH,
        organization_id="org_pub",
        endpoint="/api/v1/public/rights/organization/org_pub/rsl",
        metadata={"bot_category": "gptbot", "user_agent": "GPTBot/1.0"},
    )
    d = event.to_dict()
    assert d["metric_type"] == "rsl_fetch"
    assert d["organization_id"] == "org_pub"


# ---------------------------------------------------------------------------
# TEAM_218: classify_bot()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ua,expected", [
    ("Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)", "gptbot"),
    ("Claude-Web/1.0 (compatible; ClaudeBot/1.0)", "claudebot"),
    ("anthropic-ai/1.0", "claudebot"),
    ("Google-Extended/1.0", "google-extended"),
    ("GoogleOther/1.0", "google-extended"),
    ("PerplexityBot/1.0", "perplexitybot"),
    ("Bytespider; +https://bytedance.com", "bytespider"),
    ("Meta-ExternalAgent/1.0", "meta"),
    ("facebookexternalhit/1.1", "meta"),
    ("CCBot/2.0", "ccbot"),
    ("python-httpx/0.27.0", "python-sdk"),
    ("python-requests/2.31.0", "python-sdk"),
    ("curl/8.5.0", "curl"),
    ("Googlebot/2.1 (+http://www.google.com/bot.html)", "googlebot"),
    ("Bingbot/2.0", "bingbot"),
    ("msnbot/2.0", "bingbot"),
    ("MyCustomBrowser/3.0", "unknown"),
    ("", "unknown"),
])
def test_classify_bot(ua: str, expected: str) -> None:
    assert classify_bot(ua) == expected


def test_classify_bot_case_insensitive() -> None:
    """UA matching must be case-insensitive."""
    assert classify_bot("GPTBOT/1.0") == "gptbot"
    assert classify_bot("claudebot/1.0") == "claudebot"
    assert classify_bot("ANTHROPIC-AI/1.0") == "claudebot"
