"""Notification service business logic"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import structlog

from ..db.models import Notification
from ..models.schemas import NotificationCreate
from ..core.config import settings
from encypher_commercial_shared.email import EmailConfig, send_email, render_template

logger = structlog.get_logger(__name__)


def _get_email_config() -> EmailConfig:
    """Create email config from settings."""
    return EmailConfig(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_pass=settings.SMTP_PASS,
        smtp_tls=settings.SMTP_TLS,
        email_from=settings.EMAIL_FROM,
        email_from_name=settings.EMAIL_FROM_NAME,
        frontend_url=settings.FRONTEND_URL,
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
            status="pending",
            recipient=notification_data.recipient,
            subject=notification_data.subject,
            content=notification_data.content,
            metadata=notification_data.metadata,
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send based on notification type
        success = False
        if notification_data.notification_type == "email":
            success = NotificationService._send_email_notification(notification)
        else:
            # For other types (sms, webhook), mark as pending for future implementation
            logger.warning(
                "unsupported_notification_type",
                notification_type=notification_data.notification_type,
                notification_id=notification.id,
            )
        
        # Update status
        if success:
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = "failed"
        
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def _send_email_notification(notification: Notification) -> bool:
        """Send an email notification."""
        config = _get_email_config()
        
        return send_email(
            config=config,
            to_email=notification.recipient,
            subject=notification.subject,
            html_content=notification.content,
            logger=logger,
        )
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: str, limit: int = 100) -> List[Notification]:
        """Get notifications for user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
