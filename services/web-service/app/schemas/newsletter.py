from typing import Literal

from pydantic import BaseModel, EmailStr


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr
    source: str = "blog"


class NewsletterUnsubscribeRequest(BaseModel):
    token: str


class NewsletterSubscriberStatusUpdateRequest(BaseModel):
    status: Literal["active", "unsubscribed", "invalid"]
    reason: str | None = None


class NewsletterBroadcastRequest(BaseModel):
    title: str
    excerpt: str
    post_url: str
    image_url: str | None = None
    secret: str
