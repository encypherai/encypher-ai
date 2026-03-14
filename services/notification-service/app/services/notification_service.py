"""Notification service business logic"""

from datetime import datetime
from typing import List

import structlog
from sqlalchemy.orm import Session

from encypher_commercial_shared.email import EmailConfig, send_email

from ..core.config import settings
from ..db.models import Notification
from ..models.schemas import NotificationCreate, NotificationStatus

logger = structlog.get_logger(__name__)

# Build EmailConfig once at module load — settings are static after startup.
_EMAIL_CONFIG = EmailConfig(
    smtp_host=settings.SMTP_HOST,
    smtp_port=settings.SMTP_PORT,
    smtp_user=settings.SMTP_USER,
    smtp_pass=settings.SMTP_PASS,
    smtp_tls=settings.SMTP_TLS,
    email_from=settings.EMAIL_FROM,
    email_from_name=settings.EMAIL_FROM_NAME,
    frontend_url=settings.MARKETING_SITE_URL,
    dashboard_url=settings.DASHBOARD_URL,
)


class NotificationService:
    """Notification service"""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        notification_data: NotificationCreate,
    ) -> Notification:
        """Create and send a notification"""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_data.notification_type,
            status=NotificationStatus.PENDING,
            recipient=notification_data.recipient,
            subject=notification_data.subject,
            content=notification_data.content,
            meta_data=notification_data.metadata,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Send based on notification type
        error: str | None = None
        success = False
        if notification_data.notification_type == "email":
            success, error = NotificationService._send_email_notification(notification)
        else:
            # sms and webhook are not yet implemented
            error = f"notification_type '{notification_data.notification_type}' is not supported"
            logger.warning(
                "unsupported_notification_type",
                notification_type=notification_data.notification_type,
                notification_id=notification.id,
            )

        # Update status
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.utcnow()
            notification.error_message = error

        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def _send_email_notification(notification: Notification) -> tuple[bool, str | None]:
        """Send an email notification. Returns (success, error_message)."""
        try:
            ok = send_email(
                config=_EMAIL_CONFIG,
                to_email=notification.recipient,
                subject=notification.subject or "",
                html_content="",
                plain_content=notification.content,
                logger=logger,
            )
            if ok:
                return True, None
            return False, "send_email returned False"
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def get_user_notifications(db: Session, user_id: str, limit: int = 20) -> List[Notification]:
        """Get notifications for user"""
        return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(limit).all()
