from pydantic import BaseModel, EmailStr


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr
    source: str = "blog"


class NewsletterUnsubscribeRequest(BaseModel):
    token: str


class NewsletterBroadcastRequest(BaseModel):
    title: str
    excerpt: str
    post_url: str
    image_url: str | None = None
    secret: str
