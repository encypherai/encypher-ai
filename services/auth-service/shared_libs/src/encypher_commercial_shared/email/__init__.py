"""
Encypher Email Module

Shared email functionality for all Encypher services.
Provides SMTP sending, template rendering, and common email types.
"""

from .sender import (
    EmailConfig,
    send_email,
    render_template,
    generate_token,
)

from .emails import (
    send_verification_email,
    send_welcome_email,
    send_password_reset_email,
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
