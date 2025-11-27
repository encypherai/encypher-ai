"""
Email service for sending transactional emails.
Uses SMTP with Jinja2 templates for branded emails.
"""
import os
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..core.config import settings

logger = structlog.get_logger(__name__)

# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"

# Jinja2 environment
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"])
)


def generate_token(length: int = 32) -> str:
    """Generate a URL-safe random token."""
    return secrets.token_urlsafe(length)


def render_template(template_name: str, **context) -> str:
    """
    Render an email template with the given context.
    Automatically adds common variables like year.
    """
    base_context = {
        "year": datetime.now().year,
        "brand_name": "EncypherAI",
    }
    template_context = {**base_context, **context}
    
    template = jinja_env.get_template(template_name)
    return template.render(**template_context)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
) -> bool:
    """
    Send an email via SMTP.
    
    Returns True if successful, False otherwise.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg["To"] = to_email
        
        # Plain text fallback
        if plain_content:
            msg.attach(MIMEText(plain_content, "plain"))
        
        # HTML content
        msg.attach(MIMEText(html_content, "html"))
        
        # Connect and send
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASS:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())
        
        logger.info(
            "email_sent",
            to=to_email,
            subject=subject,
        )
        return True
        
    except Exception as e:
        logger.error(
            "email_send_failed",
            to=to_email,
            subject=subject,
            error=str(e),
        )
        return False


def send_verification_email(
    to_email: str,
    user_name: Optional[str],
    verification_token: str,
) -> bool:
    """Send email verification email."""
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
    
    html_content = render_template(
        "email_verification.html",
        subject="Verify your email address",
        user_name=user_name,
        verification_url=verification_url,
    )
    
    plain_content = f"""
Verify your email address

Hi{' ' + user_name if user_name else ''},

Thanks for signing up for EncypherAI! To complete your registration, please verify your email address by visiting:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with EncypherAI, you can safely ignore this email.

— The EncypherAI Team
"""
    
    return send_email(
        to_email=to_email,
        subject="Verify your email address - EncypherAI",
        html_content=html_content,
        plain_content=plain_content.strip(),
    )


def send_welcome_email(
    to_email: str,
    user_name: Optional[str],
) -> bool:
    """Send welcome email after verification."""
    dashboard_url = settings.DASHBOARD_URL or f"{settings.FRONTEND_URL}/dashboard"
    
    html_content = render_template(
        "welcome.html",
        subject="Welcome to EncypherAI!",
        user_name=user_name,
        dashboard_url=dashboard_url,
    )
    
    plain_content = f"""
Welcome to EncypherAI!

Hi{' ' + user_name if user_name else ''},

Your email has been verified and your account is now active. You're all set to start making AI transparent and trustworthy!

Here's what you can do next:
- Generate API Keys – Create keys to integrate EncypherAI into your applications
- Explore the Dashboard – Monitor your usage and manage your account
- Read the Docs – Learn how to embed provenance metadata in AI-generated content

Go to Dashboard: {dashboard_url}

Need help? Check out our documentation at https://encypherai.com/docs or email support@encypherai.com.

— The EncypherAI Team
"""
    
    return send_email(
        to_email=to_email,
        subject="Welcome to EncypherAI! 🎉",
        html_content=html_content,
        plain_content=plain_content.strip(),
    )


def send_password_reset_email(
    to_email: str,
    user_name: Optional[str],
    reset_token: str,
    ip_address: Optional[str] = None,
) -> bool:
    """Send password reset email."""
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
    
    html_content = render_template(
        "password_reset.html",
        subject="Reset your password",
        user_name=user_name,
        reset_url=reset_url,
        ip_address=ip_address,
    )
    
    plain_content = f"""
Reset your password

Hi{' ' + user_name if user_name else ''},

We received a request to reset the password for your EncypherAI account. Visit the link below to create a new password:

{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

— The EncypherAI Team
"""
    
    return send_email(
        to_email=to_email,
        subject="Reset your password - EncypherAI",
        html_content=html_content,
        plain_content=plain_content.strip(),
    )
