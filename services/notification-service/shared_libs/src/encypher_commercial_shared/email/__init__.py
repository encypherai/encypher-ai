"""
EncypherAI Email Module

Shared email functionality for all EncypherAI services.
Provides SMTP sending, template rendering, and common email types.
"""

from .emails import (
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)
from .sender import (
    EmailConfig,
    generate_token,
    render_template,
    send_email,
)

__all__ = [
    # Core
    "EmailConfig",
    "send_email",
    "render_template",
    "generate_token",
    # Pre-built emails
    "send_verification_email",
    "send_welcome_email",
    "send_password_reset_email",
]
