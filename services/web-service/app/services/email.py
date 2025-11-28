"""
Email service for sending notifications and confirmations.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailClient:
    """SMTP email client for sending notifications."""

    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.use_tls = settings.SMTP_TLS
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM_EMAIL
        self.from_name = settings.EMAIL_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> bool:
        """Send an email. Returns True on success, False on failure."""
        if not settings.EMAILS_ENABLED:
            logger.info(f"Email disabled - would send to {to_email}: {subject}")
            return True  # Return True so callers don't treat as error

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = to_email

        # Always add plain text
        msg.attach(MIMEText(body, "plain"))

        # Add HTML if provided
        if html:
            msg.attach(MIMEText(html, "html"))

        try:
            if self.port == 465:
                with smtplib.SMTP_SSL(self.host, self.port, timeout=10) as server:
                    if self.username:
                        server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                    server.ehlo()
                    if self.use_tls:
                        server.starttls()
                    if self.username:
                        server.login(self.username, self.password)
                    server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP auth error sending to {to_email}: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connect error sending to {to_email}: {e}")
            return False
        except TimeoutError as e:
            logger.error(f"SMTP timeout sending to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False


# Singleton instance
email_client = EmailClient()


def send_demo_notification(
    demo_request: Any,
    context: str = "general",
) -> None:
    """Send notification to sales team about a new demo request."""
    context_labels = {
        "ai-demo": "AI Demo",
        "publisher-demo": "Publisher Demo",
        "enterprise": "Enterprise Sales",
        "general": "General Sales",
    }
    label = context_labels.get(context, context.title())

    subject = f"New {label} Request from {demo_request.organization or 'Unknown'}"

    body = f"""New {label} Request

Name: {demo_request.name}
Email: {demo_request.email}
Organization: {demo_request.organization or 'Not provided'}
Role: {demo_request.role or 'Not provided'}

Message:
{demo_request.message or 'No message provided'}

Source: {demo_request.source}
Request ID: {demo_request.uuid}
"""

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2563eb;">New {label} Request</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.name}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="mailto:{demo_request.email}">{demo_request.email}</a></td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Organization:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.organization or 'Not provided'}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Role:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.role or 'Not provided'}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.source}</td></tr>
    </table>
    <h3 style="margin-top: 20px;">Message:</h3>
    <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        {demo_request.message or 'No message provided'}
    </p>
    <p style="color: #666; font-size: 12px; margin-top: 20px;">
        Request ID: {demo_request.uuid}
    </p>
</body>
</html>
"""

    email_client.send_email(
        to_email=settings.SALES_EMAIL,
        subject=subject,
        body=body,
        html=html,
    )


def send_demo_confirmation(
    to_email: str,
    name: str,
    context: str = "general",
) -> None:
    """Send confirmation email to the requester."""
    context_messages = {
        "ai-demo": "AI Performance Analytics",
        "publisher-demo": "content protection solutions",
        "enterprise": "enterprise solutions",
        "general": "products and services",
    }
    product_msg = context_messages.get(context, "products and services")

    subject = "Thank you for your interest in Encypher"

    body = f"""Hello {name},

Thank you for your interest in Encypher's {product_msg}!

We've received your request and our team will review it shortly. You can expect to hear from us within 24 hours.

In the meantime, feel free to explore our website at https://encypherai.com for more information.

Best regards,
The Encypher Team
"""

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #2563eb, #0891b2); padding: 30px; text-align: center;">
        <h1 style="color: white; margin: 0;">Encypher</h1>
    </div>
    <div style="padding: 30px;">
        <h2>Hello {name},</h2>
        <p>Thank you for your interest in Encypher's {product_msg}!</p>
        <p>We've received your request and our team will review it shortly. You can expect to hear from us within <strong>24 hours</strong>.</p>
        <h3>What happens next?</h3>
        <ul>
            <li>A member of our team will reach out to you</li>
            <li>We'll discuss your specific needs</li>
            <li>If appropriate, we'll schedule a personalized demo</li>
        </ul>
        <p>In the meantime, feel free to explore our website for more information:</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="https://encypherai.com" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Visit encypherai.com
            </a>
        </p>
        <p>Best regards,<br>The Encypher Team</p>
    </div>
    <div style="background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
        <p> 2025 Encypher Corporation. All rights reserved.</p>
    </div>
</body>
</html>
"""

    email_client.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        html=html,
    )
