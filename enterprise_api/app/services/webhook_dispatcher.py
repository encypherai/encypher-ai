"""
Webhook dispatcher service for sending event notifications.

Handles queuing, delivery, and retry logic for webhook events.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.utils.crypto_utils import decrypt_sensitive_value
from app.utils.outbound_url import validate_https_public_url

logger = logging.getLogger(__name__)


class WebhookDispatcher:
    """
    Service for dispatching webhook events to registered endpoints.

    Features:
    - Async event delivery
    - HMAC signature verification
    - Automatic retries with exponential backoff
    - Delivery logging
    """

    RETRY_DELAYS = [60, 300, 900]  # 1 min, 5 min, 15 min
    TIMEOUT_SECONDS = 10
    MAX_ATTEMPTS = 3
    RETRY_POLL_INTERVAL = 30  # seconds between retry sweeps

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._retry_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.TIMEOUT_SECONDS),
                follow_redirects=False,
            )
        return self._client

    async def close(self):
        """Close HTTP client and stop retry loop."""
        await self.stop_retry_loop()
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def start_retry_loop(self) -> None:
        """Start the background retry processing loop."""
        if self._retry_task is None or self._retry_task.done():
            self._retry_task = asyncio.create_task(self._retry_loop())
            logger.info("Webhook retry loop started")

    async def stop_retry_loop(self) -> None:
        """Stop the background retry processing loop."""
        if self._retry_task and not self._retry_task.done():
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
            self._retry_task = None
            logger.info("Webhook retry loop stopped")

    async def _retry_loop(self) -> None:
        """Background loop that periodically processes pending retries."""
        while True:
            try:
                await asyncio.sleep(self.RETRY_POLL_INTERVAL)
                await self.process_pending_retries()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Webhook retry loop error: {e}")
                await asyncio.sleep(self.RETRY_POLL_INTERVAL)

    def generate_signature(self, payload: str, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        Args:
            payload: JSON string payload
            secret: Shared secret

        Returns:
            Hex-encoded signature
        """
        return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def build_headers(
        self,
        *,
        event_type: str,
        delivery_id: str,
        payload_json: str,
        secret: Optional[str] = None,
    ) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Encypher-Webhook/1.0",
            "X-Encypher-Event": event_type,
            "X-Encypher-Delivery": delivery_id,
        }

        if secret:
            timestamp = datetime.now(timezone.utc).isoformat()
            signature = self.generate_signature(f"{timestamp}.{payload_json}", secret)
            headers["X-Encypher-Timestamp"] = timestamp
            headers["X-Encypher-Signature"] = f"sha256={signature}"

        return headers

    async def dispatch_event(
        self,
        event_type: str,
        organization_id: str,
        data: Dict[str, Any],
        db: Optional[AsyncSession] = None,
    ) -> None:
        """
        Dispatch an event to all registered webhooks for an organization.

        Args:
            event_type: Type of event (e.g., "document.signed")
            organization_id: Organization to notify
            data: Event payload data
            db: Optional database session (creates one if not provided)
        """
        should_close_db = db is None
        if db is None:
            db = async_session_factory()

        try:
            # Get active webhooks for this event
            result = await db.execute(
                text(
                    """
                    SELECT id, url, secret_hash, secret_encrypted, events
                    FROM webhooks
                    WHERE organization_id = :org_id
                    AND is_active = true
                    AND :event_type = ANY(events)
                """
                ),
                {"org_id": organization_id, "event_type": event_type},
            )
            webhooks = result.fetchall()

            if not webhooks:
                logger.debug(f"No webhooks registered for {event_type} in org {organization_id}")
                return

            # Build event payload
            event_id = f"evt_{secrets.token_hex(12)}"
            timestamp = datetime.now(timezone.utc).isoformat()

            payload = {
                "event": event_type,
                "event_id": event_id,
                "organization_id": organization_id,
                "timestamp": timestamp,
                "data": data,
            }

            # Dispatch to each webhook
            tasks = []
            for webhook in webhooks:
                secret = None
                if webhook.secret_encrypted:
                    try:
                        secret = decrypt_sensitive_value(bytes(webhook.secret_encrypted))
                    except ValueError as exc:
                        logger.warning(
                            "webhook_secret_decrypt_failed",
                            extra={"webhook_id": webhook.id, "error": str(exc)},
                        )
                tasks.append(
                    self._deliver_webhook(
                        db=db,
                        webhook_id=webhook.id,
                        url=webhook.url,
                        secret=secret,
                        event_type=event_type,
                        event_id=event_id,
                        payload=payload,
                        organization_id=organization_id,
                    )
                )

            # Run deliveries concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Error dispatching event {event_type}: {e}")
        finally:
            if should_close_db:
                await db.close()

    async def _deliver_webhook(
        self,
        db: AsyncSession,
        webhook_id: str,
        url: str,
        secret: Optional[str],
        event_type: str,
        event_id: str,
        payload: Dict[str, Any],
        organization_id: str,
    ) -> bool:
        """
        Deliver a webhook to a single endpoint.

        Args:
            db: Database session
            webhook_id: Webhook ID
            url: Webhook URL
            secret_hash: Hashed secret for signature (if any)
            event_type: Event type
            event_id: Unique event ID
            payload: Event payload
            organization_id: Organization ID

        Returns:
            True if delivery succeeded, False otherwise
        """
        delivery_id = f"del_{secrets.token_hex(12)}"
        payload_json = json.dumps(payload)

        # Create delivery record
        await db.execute(
            text(
                """
                INSERT INTO webhook_deliveries (
                    id, webhook_id, organization_id, event_type, event_id,
                    payload, status, attempts, max_attempts, created_at
                ) VALUES (
                    :id, :webhook_id, :org_id, :event_type, :event_id,
                    :payload, 'pending', 0, :max_attempts, :created_at
                )
            """
            ),
            {
                "id": delivery_id,
                "webhook_id": webhook_id,
                "org_id": organization_id,
                "event_type": event_type,
                "event_id": event_id,
                "payload": payload,
                "max_attempts": self.MAX_ATTEMPTS,
                "created_at": datetime.now(timezone.utc),
            },
        )
        await db.commit()

        # Attempt delivery
        success = await self._attempt_delivery(
            db=db,
            delivery_id=delivery_id,
            webhook_id=webhook_id,
            url=url,
            secret=secret,
            payload_json=payload_json,
            event_type=event_type,
        )

        # Schedule retry if first attempt failed
        if not success:
            await self._schedule_retry(db, delivery_id)

        return success

    async def _attempt_delivery(
        self,
        db: AsyncSession,
        delivery_id: str,
        webhook_id: str,
        url: str,
        secret: Optional[str],
        payload_json: str,
        event_type: str,
    ) -> bool:
        """
        Attempt to deliver a webhook.

        Args:
            db: Database session
            delivery_id: Delivery record ID
            webhook_id: Webhook ID
            url: Webhook URL
            secret_hash: Hashed secret for signature
            payload_json: JSON payload string
            event_type: Event type

        Returns:
            True if delivery succeeded
        """
        try:
            validate_https_public_url(url, resolve_dns=True)
        except ValueError:
            await self._record_failure(db, delivery_id, webhook_id, "Untrusted webhook URL")
            return False

        client = await self.get_client()

        headers = self.build_headers(
            event_type=event_type,
            delivery_id=delivery_id,
            payload_json=payload_json,
            secret=secret,
        )

        try:
            start_time = datetime.now(timezone.utc)
            response = await client.post(url, content=payload_json, headers=headers)
            elapsed_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            success = 200 <= response.status_code < 300

            # Update delivery record
            await db.execute(
                text(
                    """
                    UPDATE webhook_deliveries
                    SET
                        status = :status,
                        attempts = attempts + 1,
                        response_status_code = :status_code,
                        response_body = :response_body,
                        response_time_ms = :response_time,
                        delivered_at = CASE WHEN :success THEN :now ELSE delivered_at END
                    WHERE id = :delivery_id
                """
                ),
                {
                    "delivery_id": delivery_id,
                    "status": "success" if success else "failed",
                    "status_code": response.status_code,
                    "response_body": response.text[:1000] if response.text else None,
                    "response_time": elapsed_ms,
                    "success": success,
                    "now": datetime.now(timezone.utc),
                },
            )

            # Update webhook stats
            if success:
                await db.execute(
                    text(
                        """
                        UPDATE webhooks
                        SET
                            success_count = success_count + 1,
                            last_triggered_at = :now,
                            last_success_at = :now
                        WHERE id = :webhook_id
                    """
                    ),
                    {"webhook_id": webhook_id, "now": datetime.now(timezone.utc)},
                )
            else:
                await db.execute(
                    text(
                        """
                        UPDATE webhooks
                        SET
                            failure_count = failure_count + 1,
                            last_triggered_at = :now,
                            last_failure_at = :now,
                            last_failure_reason = :reason
                        WHERE id = :webhook_id
                    """
                    ),
                    {
                        "webhook_id": webhook_id,
                        "now": datetime.now(timezone.utc),
                        "reason": f"HTTP {response.status_code}",
                    },
                )

            await db.commit()

            if success:
                logger.info(f"Webhook delivered: {delivery_id} -> {url} ({response.status_code})")
            else:
                logger.warning(f"Webhook failed: {delivery_id} -> {url} ({response.status_code})")

            return success

        except httpx.TimeoutException:
            await self._record_failure(db, delivery_id, webhook_id, "Request timed out")
            return False
        except httpx.RequestError as e:
            await self._record_failure(db, delivery_id, webhook_id, str(e))
            return False
        except Exception as e:
            await self._record_failure(db, delivery_id, webhook_id, f"Unexpected error: {e}")
            return False

    async def _record_failure(
        self,
        db: AsyncSession,
        delivery_id: str,
        webhook_id: str,
        error_message: str,
    ) -> None:
        """Record a delivery failure."""
        await db.execute(
            text(
                """
                UPDATE webhook_deliveries
                SET
                    status = 'failed',
                    attempts = attempts + 1,
                    error_message = :error
                WHERE id = :delivery_id
            """
            ),
            {"delivery_id": delivery_id, "error": error_message},
        )

        await db.execute(
            text(
                """
                UPDATE webhooks
                SET
                    failure_count = failure_count + 1,
                    last_triggered_at = :now,
                    last_failure_at = :now,
                    last_failure_reason = :reason
                WHERE id = :webhook_id
            """
            ),
            {
                "webhook_id": webhook_id,
                "now": datetime.now(timezone.utc),
                "reason": error_message,
            },
        )

        await db.commit()
        logger.error(f"Webhook delivery failed: {delivery_id} - {error_message}")

    async def _schedule_retry(
        self,
        db: AsyncSession,
        delivery_id: str,
    ) -> None:
        """Schedule a retry or mark as permanently failed after max attempts."""
        result = await db.execute(
            text("SELECT attempts, max_attempts FROM webhook_deliveries WHERE id = :id"),
            {"id": delivery_id},
        )
        row = result.fetchone()
        if not row:
            return

        if row.attempts >= row.max_attempts:
            await db.execute(
                text("UPDATE webhook_deliveries" " SET status = 'permanently_failed', next_retry_at = NULL" " WHERE id = :id"),
                {"id": delivery_id},
            )
            await db.commit()
            logger.warning(f"Webhook delivery permanently failed (DLQ): {delivery_id}")
        else:
            delay_index = min(row.attempts - 1, len(self.RETRY_DELAYS) - 1)
            delay_seconds = self.RETRY_DELAYS[delay_index]
            next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
            await db.execute(
                text("UPDATE webhook_deliveries" " SET status = 'retrying', next_retry_at = :next_retry" " WHERE id = :id"),
                {"id": delivery_id, "next_retry": next_retry},
            )
            await db.commit()
            logger.info(f"Webhook delivery {delivery_id} scheduled for retry " f"at {next_retry.isoformat()}")

    async def process_pending_retries(self) -> int:
        """Process all deliveries due for retry. Returns count processed."""
        db = async_session_factory()
        processed = 0
        try:
            result = await db.execute(
                text(
                    "SELECT d.id, d.webhook_id, d.payload, d.event_type,"
                    " w.url, w.secret_encrypted"
                    " FROM webhook_deliveries d"
                    " JOIN webhooks w ON w.id = d.webhook_id"
                    " WHERE d.status = 'retrying'"
                    " AND d.next_retry_at <= :now"
                    " ORDER BY d.next_retry_at ASC"
                    " LIMIT 50"
                    " FOR UPDATE OF d SKIP LOCKED"
                ),
                {"now": datetime.now(timezone.utc)},
            )
            rows = result.fetchall()

            for row in rows:
                secret = None
                if row.secret_encrypted:
                    try:
                        secret = decrypt_sensitive_value(bytes(row.secret_encrypted))
                    except ValueError as exc:
                        logger.warning(
                            "webhook_secret_decrypt_failed",
                            extra={"webhook_id": row.webhook_id, "error": str(exc)},
                        )

                payload_json = json.dumps(row.payload)
                success = await self._attempt_delivery(
                    db=db,
                    delivery_id=row.id,
                    webhook_id=row.webhook_id,
                    url=row.url,
                    secret=secret,
                    payload_json=payload_json,
                    event_type=row.event_type,
                )

                if not success:
                    await self._schedule_retry(db, row.id)

                processed += 1

        except Exception as e:
            logger.error(f"Error processing webhook retries: {e}")
        finally:
            await db.close()

        if processed:
            logger.info(f"Processed {processed} webhook retries")
        return processed

    async def retry_delivery(
        self,
        db: AsyncSession,
        delivery_id: str,
        organization_id: str | None = None,
    ) -> bool:
        """
        Manually retry a failed or permanently_failed delivery.

        Resets the delivery for another attempt and tries immediately.
        Returns True if the delivery was found and retried.
        If organization_id is provided, enforces ownership check.
        """
        query = (
            "SELECT d.id, d.webhook_id, d.payload, d.event_type, d.status,"
            " w.url, w.secret_encrypted"
            " FROM webhook_deliveries d"
            " JOIN webhooks w ON w.id = d.webhook_id"
            " WHERE d.id = :id"
        )
        params: dict = {"id": delivery_id}
        if organization_id:
            query += " AND w.organization_id = :org_id"
            params["org_id"] = organization_id

        result = await db.execute(text(query), params)
        row = result.fetchone()
        if not row or row.status not in ("failed", "permanently_failed"):
            return False

        # Reset for retry
        await db.execute(
            text(
                "UPDATE webhook_deliveries"
                " SET status = 'retrying',"
                " next_retry_at = :now,"
                " attempts = GREATEST(attempts - 1, 0)"
                " WHERE id = :id"
            ),
            {"id": delivery_id, "now": datetime.now(timezone.utc)},
        )
        await db.commit()

        # Attempt immediately
        secret = None
        if row.secret_encrypted:
            try:
                secret = decrypt_sensitive_value(bytes(row.secret_encrypted))
            except ValueError:
                pass

        payload_json = json.dumps(row.payload)
        success = await self._attempt_delivery(
            db=db,
            delivery_id=row.id,
            webhook_id=row.webhook_id,
            url=row.url,
            secret=secret,
            payload_json=payload_json,
            event_type=row.event_type,
        )

        if not success:
            await self._schedule_retry(db, row.id)

        return True


# Singleton instance
webhook_dispatcher = WebhookDispatcher()


# Convenience functions for common events
async def emit_document_signed(
    organization_id: str,
    document_id: str,
    title: Optional[str] = None,
    document_type: Optional[str] = None,
) -> None:
    """Emit document.signed event."""
    await webhook_dispatcher.dispatch_event(
        event_type="document.signed",
        organization_id=organization_id,
        data={
            "document_id": document_id,
            "title": title,
            "document_type": document_type,
            "verification_url": f"https://api.encypherai.com/api/v1/verify/{document_id}",
        },
    )


async def emit_document_revoked(
    organization_id: str,
    document_id: str,
    reason: Optional[str] = None,
) -> None:
    """Emit document.revoked event."""
    await webhook_dispatcher.dispatch_event(
        event_type="document.revoked",
        organization_id=organization_id,
        data={
            "document_id": document_id,
            "reason": reason,
        },
    )


async def emit_quota_warning(
    organization_id: str,
    metric: str,
    used: int,
    limit: int,
    percentage: float,
) -> None:
    """Emit quota.warning event when usage exceeds 80%."""
    await webhook_dispatcher.dispatch_event(
        event_type="quota.warning",
        organization_id=organization_id,
        data={
            "metric": metric,
            "used": used,
            "limit": limit,
            "percentage": percentage,
            "message": f"Your {metric} usage is at {percentage:.1f}% of your limit",
        },
    )


async def emit_key_created(
    organization_id: str,
    key_id: str,
    key_name: Optional[str] = None,
) -> None:
    """Emit key.created event."""
    await webhook_dispatcher.dispatch_event(
        event_type="key.created",
        organization_id=organization_id,
        data={
            "key_id": key_id,
            "key_name": key_name,
        },
    )


async def emit_key_revoked(
    organization_id: str,
    key_id: str,
) -> None:
    """Emit key.revoked event."""
    await webhook_dispatcher.dispatch_event(
        event_type="key.revoked",
        organization_id=organization_id,
        data={
            "key_id": key_id,
        },
    )
