"""
Shared auth helpers used across multiple routers.
"""

from fastapi import HTTPException, status

from encypher_commercial_shared.email import EmailConfig
from ..core.config import settings


def extract_bearer_token(authorization: str) -> str:
    """
    Parse 'Bearer <token>' and return the token.

    Raises HTTP 401 with a usage hint if the header is malformed.
    """
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials. Expected header: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return parts[1].strip()


def get_email_config() -> EmailConfig:
    """Build an EmailConfig from application settings (single source of truth)."""
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
        support_email=settings.SUPPORT_EMAIL,
    )
