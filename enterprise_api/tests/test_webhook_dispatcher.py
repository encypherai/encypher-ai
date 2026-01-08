import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.webhook_dispatcher import WebhookDispatcher


@pytest.mark.asyncio
async def test_webhook_dispatcher_client_disables_redirects() -> None:
    dispatcher = WebhookDispatcher()

    client = MagicMock()
    client.is_closed = False

    with patch("app.services.webhook_dispatcher.httpx.AsyncClient", return_value=client) as ctor:
        await dispatcher.get_client()

    assert ctor.call_count == 1
    assert ctor.call_args.kwargs["follow_redirects"] is False


@pytest.mark.asyncio
async def test_webhook_dispatcher_rejects_untrusted_url() -> None:
    dispatcher = WebhookDispatcher()
    dispatcher.get_client = AsyncMock()
    dispatcher._record_failure = AsyncMock()

    db = AsyncMock()

    with patch("app.services.webhook_dispatcher.validate_https_public_url", side_effect=ValueError("untrusted")):
        ok = await dispatcher._attempt_delivery(
            db=db,
            delivery_id="del_test",
            webhook_id="wh_test",
            url="https://127.0.0.1/webhook",
            secret_hash=None,
            payload_json="{}",
            event_type="document.signed",
        )

    assert ok is False
    dispatcher.get_client.assert_not_called()
    dispatcher._record_failure.assert_called_once()
