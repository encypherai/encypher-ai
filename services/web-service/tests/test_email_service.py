from types import SimpleNamespace
from uuid import uuid4

from app.services import email as email_service


def test_send_demo_notification_uses_contact_recipient_and_user_reply_to(monkeypatch):
    captured = {}

    def fake_send_email(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(email_service.email_client, "send_email", fake_send_email)

    demo_request = SimpleNamespace(
        name="Jane Doe",
        email="jane@example.com",
        organization="Acme Media",
        role="Editor",
        message="Please show me the publisher demo.",
        source="publisher-demo",
        uuid=uuid4(),
    )

    email_service.send_demo_notification(demo_request, context="publisher-demo")

    assert captured["to_email"] == "contact@encypher.com"
    assert captured["reply_to"] == "jane@example.com"
    assert "New Publisher Demo Request" in captured["subject"]
