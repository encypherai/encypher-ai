"""
Email service for sending emails from the application.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an email using the configured SMTP server.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional, will be generated from HTML if not provided)
        from_email: Sender email address (defaults to settings.EMAILS_FROM_EMAIL)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # For development/testing, just log the email instead of sending
    if settings.ENVIRONMENT.lower() in ["development", "test"]:
        logger.info(f"Would send email to {to_email} with subject: {subject}")
        logger.info(f"Content: {html_content}")
        return True

    # In production, actually send the email
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email or settings.EMAILS_FROM_EMAIL
        message["To"] = to_email

        # Add text part if provided
        if text_content:
            message.attach(MIMEText(text_content, "plain"))

        # Add HTML part
        message.attach(MIMEText(html_content, "html"))

        # Connect to SMTP server and send
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()

            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            server.sendmail(message["From"], [to_email], message.as_string())

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_password_reset_email(email: str, reset_url: str) -> bool:
    """
    Send a password reset email with a link to reset the password.

    Args:
        email: Recipient email address
        reset_url: URL for resetting the password

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Password Reset - Encypher Dashboard"

    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2a87c4;">Reset Your Password</h2>
            <p>You have requested to reset your password for the Encypher Dashboard.</p>
            <p>Please click the link below to reset your password. This link will expire in 24 hours.</p>
            <p>
                <a href="{reset_url}" style="display: inline-block; background-color: #2a87c4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                    Reset Password
                </a>
            </p>
            <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
            <p>Thank you,<br>The Encypher Team</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Reset Your Password
    
    You have requested to reset your password for the Encypher Dashboard.
    
    Please visit the following link to reset your password. This link will expire in 24 hours.
    
    {reset_url}
    
    If you did not request a password reset, please ignore this email or contact support if you have concerns.
    
    Thank you,
    The Encypher Team
    """

    return await send_email(to_email=email, subject=subject, html_content=html_content, text_content=text_content)
