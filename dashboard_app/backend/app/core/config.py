"""
Configuration settings for the Encypher Dashboard Backend.
"""

import os
import secrets
from typing import Optional

from pydantic import BaseModel


def _get_secret_key() -> str:
    """Return SECRET_KEY from env or generate a random ephemeral key for dev."""
    key = os.getenv("SECRET_KEY", "")
    if key:
        return key
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        raise RuntimeError("SECRET_KEY environment variable must be set in production")
    return secrets.token_urlsafe(48)


class Settings(BaseModel):
    """Application settings."""

    PROJECT_NAME: str = "Encypher Dashboard"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Frontend URL for links in emails
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Security
    SECRET_KEY: str = _get_secret_key()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./encypherai_dashboard.db")

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend
        "http://localhost",
    ]

    # Enterprise API integration
    ENTERPRISE_API_BASE_URL: str = os.getenv("ENTERPRISE_API_BASE_URL", "http://localhost:9000/api/v1")
    ENTERPRISE_API_KEY: Optional[str] = os.getenv("ENTERPRISE_API_KEY")
    ENTERPRISE_API_TIMEOUT: float = float(os.getenv("ENTERPRISE_API_TIMEOUT", "30"))

    # Email settings
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@encypherai.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Encypher Dashboard")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "25"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "False").lower() == "true"


settings = Settings()
