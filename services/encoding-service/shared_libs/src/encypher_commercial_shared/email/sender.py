"""
Core email sending functionality.

This module provides SMTP email sending with Jinja2 template support.
Services should use this module for all email operations.
"""

import os
import secrets
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Template directory (relative to this module)
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Jinja2 environment (lazy loaded)
_jinja_env: Optional[Environment] = None


def _get_jinja_env() -> Environment:
    """Get or create Jinja2 environment."""
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(["html", "xml"]))
    return _jinja_env


@dataclass
class EmailConfig:
    """
    Email configuration.

    Can be initialized from environment variables or passed directly.
    Services should create this once and reuse it.
    """

    smtp_host: str = "smtp.zoho.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_tls: bool = True
    email_from: str = "support@encypher.com"
    email_from_name: str = "Support - Encypher"
    frontend_url: str = "http://localhost:3000"
    dashboard_url: str = ""
    support_email: str = ""  # BCC for notifications

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Create config from environment variables."""
        return cls(
            smtp_host=os.getenv("SMTP_HOST", "smtp.zoho.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_pass=os.getenv("SMTP_PASS", ""),
            smtp_tls=os.getenv("SMTP_TLS", "true").lower() == "true",
            email_from=os.getenv("EMAIL_FROM", "support@encypher.com"),
            email_from_name=os.getenv("EMAIL_FROM_NAME", "Support - Encypher"),
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
            dashboard_url=os.getenv("DASHBOARD_URL", ""),
            support_email=os.getenv("SUPPORT_EMAIL", ""),
        )


def generate_token(length: int = 32) -> str:
    """Generate a URL-safe random token."""
    return secrets.token_urlsafe(length)


def render_template(template_name: str, **context) -> str:
    """
    Render an email template with the given context.

    Automatically adds common variables like year and brand_name.

    Args:
        template_name: Name of template file (e.g., "email_verification.html")
        **context: Template variables

    Returns:
        Rendered HTML string
    """
    base_context = {
        "year": datetime.now().year,
        "brand_name": "Encypher",
        "preheader": "",
    }
    template_context = {**base_context, **context}

    env = _get_jinja_env()
    template = env.get_template(template_name)
    return template.render(**template_context)


def send_email(
    config: EmailConfig,
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
    bcc_email: Optional[str] = None,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send an email via SMTP.

    Args:
        config: Email configuration
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        plain_content: Plain text fallback (optional)
        bcc_email: BCC recipient (optional)
        logger: Optional structured logger for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{config.email_from_name} <{config.email_from}>"
        msg["To"] = to_email

        # Plain text fallback
        if plain_content:
            msg.attach(MIMEText(plain_content, "plain"))

        # HTML content (skip empty to avoid a blank HTML alternative)
        if html_content:
            msg.attach(MIMEText(html_content, "html"))

        # Build recipient list (BCC is not in headers, just in sendmail)
        recipients = [to_email]
        if bcc_email:
            recipients.append(bcc_email)

        # Connect and send
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            if config.smtp_tls:
                server.starttls()
            if config.smtp_user and config.smtp_pass:
                server.login(config.smtp_user, config.smtp_pass)
            server.sendmail(config.email_from, recipients, msg.as_string())

        if logger:
            logger.info("email_sent", to=to_email, subject=subject, bcc=bcc_email)
        return True

    except Exception as e:
        if logger:
            logger.error("email_send_failed", to=to_email, subject=subject, error=str(e))
        return False
