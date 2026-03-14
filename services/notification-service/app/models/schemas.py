"""Pydantic schemas for Notification Service"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# Reject content that contains HTML tags or binary-looking data.
# The notification-service sends emails through server-side templates; raw HTML
# from callers is not allowed.  Plain text only.
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Also catch HTML entity-encoded tags (e.g. &#60;script&#62;) which bypass the
# literal-tag regex but render as HTML in email clients.
_HTML_ENTITY_TAG_RE = re.compile(r"&(#\d{1,5}|#x[0-9a-fA-F]{1,4}|lt|gt);", re.IGNORECASE)
# Guard against binary / high-byte content submitted as a string.
_NON_ASCII_THRESHOLD = 0.10  # >10% non-ASCII chars triggers rejection


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""

    # Only 'email' is implemented; sms/webhook are placeholders not yet active.
    notification_type: str = Field(pattern="^email$")
    # Task 1.2: validate recipient as a proper email address
    recipient: EmailStr
    subject: Optional[str] = Field(default=None, max_length=998)
    # Task 1.3: plain text only; reject HTML and binary-looking content
    content: str

    @field_validator("content")
    @classmethod
    def content_must_be_plain_text(cls, v: str) -> str:
        """Reject content that contains HTML markup."""
        if _HTML_TAG_RE.search(v):
            raise ValueError("content must be plain text; HTML is not accepted. Use subject and content fields for the message body.")
        if _HTML_ENTITY_TAG_RE.search(v):
            raise ValueError("content must be plain text; HTML entities (e.g. &#60;) are not accepted.")
        # Task 2.3: binary / encoding guard -- reject if too many non-ASCII chars
        if len(v) > 0:
            non_ascii = sum(1 for c in v if ord(c) > 127)
            ratio = non_ascii / len(v)
            if ratio > _NON_ASCII_THRESHOLD:
                raise ValueError(
                    "content contains too many non-ASCII characters "
                    f"({non_ascii}/{len(v)} = {ratio:.0%}). "
                    "Plain UTF-8 text is accepted; binary or base64-encoded data is not."
                )
        return v

    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response"""

    id: str
    user_id: str
    notification_type: str
    status: str
    recipient: str
    subject: Optional[str]
    sent_at: Optional[datetime]
    failed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    # Task 2.2: request-ID and timing metadata surfaced per-response via endpoint
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str
    # Task 2.1: navigation hints for machine consumers
    hint: Optional[str] = None
