"""Notification service business logic"""
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from ..db.models import Notification
from ..models.schemas import NotificationCreate


class NotificationService:
    """Notification service"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        notification_data: NotificationCreate,
    ) -> Notification:
        """Create and queue a notification"""
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
        
        # In production, this would queue the notification for async processing
        # For now, mark as sent immediately
        notification.status = "sent"
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        return notification
    
    @staticmethod
    def get_user_notifications(db: Session, user_id: str, limit: int = 100) -> List[Notification]:
        """Get notifications for user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).all()
