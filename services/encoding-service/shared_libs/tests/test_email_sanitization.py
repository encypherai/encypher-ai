"""Tests for sanitizing user-provided names in emails."""

from typing import Any, Dict, Optional

import pytest

from encypher_commercial_shared.email import EmailConfig, send_verification_email
from encypher_commercial_shared.email import emails as email_module


class _EmailCapture:
    def __init__(self) -> None:
        self.plain: Optional[str] = None
        self.html: Optional[str] = None
        self.context: Optional[Dict[str, Any]] = None


@pytest.fixture()
def email_capture(monkeypatch: pytest.MonkeyPatch) -> _EmailCapture:
    capture = _EmailCapture()

    def _render_template_stub(_template_name: str, **context: Any) -> str:
        capture.context = context
        return "<html></html>"

    def _send_email_stub(*, html_content: str, plain_content: str, **_kwargs: Any) -> bool:
        capture.html = html_content
        capture.plain = plain_content
        return True

    monkeypatch.setattr(email_module, "render_template", _render_template_stub)
    monkeypatch.setattr(email_module, "send_email", _send_email_stub)
    return capture


def test_verification_email_strips_html_name(email_capture: _EmailCapture) -> None:
    config = EmailConfig(frontend_url="https://example.test")

    assert (
        send_verification_email(
            config=config,
            to_email="user@example.com",
            user_name="<b>Jane Doe</b>",
            verification_token="token",
        )
        is True
    )

    assert email_capture.context is not None
    assert email_capture.context["user_name"] == "Jane Doe"
    assert email_capture.plain is not None
    assert "Hi Jane Doe," in email_capture.plain
    assert "<b>" not in email_capture.plain


def test_verification_email_drops_url_name(email_capture: _EmailCapture) -> None:
    config = EmailConfig(frontend_url="https://example.test")

    assert (
        send_verification_email(
            config=config,
            to_email="user@example.com",
            user_name="Visit https://evil.test now",
            verification_token="token",
        )
        is True
    )

    assert email_capture.context is not None
    assert email_capture.context["user_name"] is None
    assert email_capture.plain is not None
    assert "https://evil.test" not in email_capture.plain
    assert "Hi," in email_capture.plain
