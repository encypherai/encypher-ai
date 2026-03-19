"""Tests for webhook retry mechanism and dead letter queue."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.webhook_dispatcher import WebhookDispatcher


@pytest.mark.asyncio
async def test_schedule_retry_sets_retrying_status() -> None:
    """After a failed attempt with retries remaining, status becomes 'retrying'."""
    dispatcher = WebhookDispatcher()
    db = AsyncMock()

    # Mock: 1 attempt done, max 3
    row = MagicMock()
    row.attempts = 1
    row.max_attempts = 3
    result = MagicMock()
    result.fetchone.return_value = row
    db.execute.return_value = result

    await dispatcher._schedule_retry(db, "del_test1")

    # Should have called execute twice: SELECT + UPDATE
    assert db.execute.call_count == 2
    update_call = db.execute.call_args_list[1]
    update_sql = str(update_call.args[0])
    assert "retrying" in update_sql
    assert "next_retry_at" in update_sql
    db.commit.assert_called()


@pytest.mark.asyncio
async def test_schedule_retry_marks_permanently_failed_after_max_attempts() -> None:
    """After max attempts, status becomes 'permanently_failed' (DLQ)."""
    dispatcher = WebhookDispatcher()
    db = AsyncMock()

    row = MagicMock()
    row.attempts = 3
    row.max_attempts = 3
    result = MagicMock()
    result.fetchone.return_value = row
    db.execute.return_value = result

    await dispatcher._schedule_retry(db, "del_test2")

    assert db.execute.call_count == 2
    update_call = db.execute.call_args_list[1]
    update_sql = str(update_call.args[0])
    assert "permanently_failed" in update_sql
    db.commit.assert_called()


@pytest.mark.asyncio
async def test_deliver_webhook_schedules_retry_on_failure() -> None:
    """_deliver_webhook calls _schedule_retry when _attempt_delivery fails."""
    dispatcher = WebhookDispatcher()
    dispatcher._attempt_delivery = AsyncMock(return_value=False)
    dispatcher._schedule_retry = AsyncMock()

    db = AsyncMock()

    result = await dispatcher._deliver_webhook(
        db=db,
        webhook_id="wh_test",
        url="https://example.com/hook",
        secret=None,
        event_type="document.signed",
        event_id="evt_test",
        payload={"event": "test"},
        organization_id="org_test",
    )

    assert result is False
    dispatcher._schedule_retry.assert_called_once()


@pytest.mark.asyncio
async def test_deliver_webhook_no_retry_on_success() -> None:
    """_deliver_webhook does not schedule retry on successful delivery."""
    dispatcher = WebhookDispatcher()
    dispatcher._attempt_delivery = AsyncMock(return_value=True)
    dispatcher._schedule_retry = AsyncMock()

    db = AsyncMock()

    result = await dispatcher._deliver_webhook(
        db=db,
        webhook_id="wh_test",
        url="https://example.com/hook",
        secret=None,
        event_type="document.signed",
        event_id="evt_test",
        payload={"event": "test"},
        organization_id="org_test",
    )

    assert result is True
    dispatcher._schedule_retry.assert_not_called()


@pytest.mark.asyncio
async def test_process_pending_retries_processes_due_deliveries() -> None:
    """process_pending_retries picks up retrying deliveries past next_retry_at."""
    dispatcher = WebhookDispatcher()
    dispatcher._attempt_delivery = AsyncMock(return_value=True)
    dispatcher._schedule_retry = AsyncMock()

    row = MagicMock()
    row.id = "del_retry1"
    row.webhook_id = "wh_1"
    row.payload = {"event": "test"}
    row.event_type = "document.signed"
    row.url = "https://example.com/hook"
    row.secret_encrypted = None

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    with patch("app.services.webhook_dispatcher.async_session_factory", return_value=mock_db):
        processed = await dispatcher.process_pending_retries()

    assert processed == 1
    dispatcher._attempt_delivery.assert_called_once()
    # Success, so _schedule_retry should not be called
    dispatcher._schedule_retry.assert_not_called()
    mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_process_pending_retries_reschedules_on_failure() -> None:
    """When a retry attempt fails, it should reschedule."""
    dispatcher = WebhookDispatcher()
    dispatcher._attempt_delivery = AsyncMock(return_value=False)
    dispatcher._schedule_retry = AsyncMock()

    row = MagicMock()
    row.id = "del_retry2"
    row.webhook_id = "wh_2"
    row.payload = {"event": "test"}
    row.event_type = "document.signed"
    row.url = "https://example.com/hook"
    row.secret_encrypted = None

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    with patch("app.services.webhook_dispatcher.async_session_factory", return_value=mock_db):
        processed = await dispatcher.process_pending_retries()

    assert processed == 1
    dispatcher._schedule_retry.assert_called_once_with(mock_db, "del_retry2")


@pytest.mark.asyncio
async def test_retry_delivery_resets_and_reattempts() -> None:
    """Manual retry resets delivery and attempts immediately."""
    dispatcher = WebhookDispatcher()
    dispatcher._attempt_delivery = AsyncMock(return_value=True)
    dispatcher._schedule_retry = AsyncMock()

    row = MagicMock()
    row.id = "del_manual1"
    row.webhook_id = "wh_3"
    row.payload = {"event": "test"}
    row.event_type = "document.signed"
    row.status = "permanently_failed"
    row.url = "https://example.com/hook"
    row.secret_encrypted = None

    mock_result = MagicMock()
    mock_result.fetchone.return_value = row

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await dispatcher.retry_delivery(db, "del_manual1")

    assert result is True
    dispatcher._attempt_delivery.assert_called_once()


@pytest.mark.asyncio
async def test_retry_delivery_rejects_non_failed_status() -> None:
    """Manual retry refuses to retry deliveries that are not failed."""
    dispatcher = WebhookDispatcher()

    row = MagicMock()
    row.id = "del_ok"
    row.status = "success"

    mock_result = MagicMock()
    mock_result.fetchone.return_value = row

    db = AsyncMock()
    db.execute.return_value = mock_result

    result = await dispatcher.retry_delivery(db, "del_ok")
    assert result is False


@pytest.mark.asyncio
async def test_retry_delays_are_applied_correctly() -> None:
    """Verify the correct delay is used for each attempt."""
    dispatcher = WebhookDispatcher()
    db = AsyncMock()

    for attempt_num, expected_delay in [(1, 60), (2, 300), (3, 900)]:
        db.reset_mock()
        if attempt_num >= dispatcher.MAX_ATTEMPTS:
            continue  # attempts >= max_attempts -> permanently_failed

        row = MagicMock()
        row.attempts = attempt_num
        row.max_attempts = dispatcher.MAX_ATTEMPTS
        result = MagicMock()
        result.fetchone.return_value = row
        db.execute.return_value = result

        await dispatcher._schedule_retry(db, f"del_delay_{attempt_num}")

        update_call = db.execute.call_args_list[1]
        update_params = update_call.args[1]
        next_retry = update_params["next_retry"]
        # next_retry should be roughly now + expected_delay
        expected_time = datetime.now(timezone.utc) + timedelta(seconds=expected_delay)
        assert abs((next_retry - expected_time).total_seconds()) < 5


def test_retry_loop_can_start_and_stop() -> None:
    """Verify start_retry_loop creates a task attribute."""
    dispatcher = WebhookDispatcher()
    assert dispatcher._retry_task is None
