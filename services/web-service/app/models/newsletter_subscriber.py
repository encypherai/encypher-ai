from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.base import Base


class NewsletterSubscriber(Base):
    """Model for newsletter subscribers."""

    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    unsubscribe_token = Column(String(64), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)
    status = Column(String(32), nullable=False, default="active", index=True)
    status_reason = Column(Text)
    source = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(Text)

    def __repr__(self):
        return f"<NewsletterSubscriber {self.email} active={self.active}>"
