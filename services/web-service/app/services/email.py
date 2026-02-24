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
        reply_to: str | None = None,
    ) -> bool:
        """Send an email. Returns True on success, False on failure."""
        if not settings.EMAILS_ENABLED:
            logger.info(f"Email disabled - would send to {to_email}: {subject}")
            return True  # Return True so callers don't treat as error

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = to_email
        if reply_to:
            msg["Reply-To"] = reply_to

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
Organization: {demo_request.organization or "Not provided"}
Role: {demo_request.role or "Not provided"}

Message:
{demo_request.message or "No message provided"}

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
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.organization or "Not provided"}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Role:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.role or "Not provided"}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">{demo_request.source}</td></tr>
    </table>
    <h3 style="margin-top: 20px;">Message:</h3>
    <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        {demo_request.message or "No message provided"}
    </p>
    <p style="color: #666; font-size: 12px; margin-top: 20px;">
        Request ID: {demo_request.uuid}
    </p>
</body>
</html>
"""

    email_client.send_email(
        to_email=settings.CONTACT_EMAIL,
        subject=subject,
        body=body,
        html=html,
        reply_to=demo_request.email,
    )


# Logo URL - hosted on production site for email compatibility
# White logo used on blue gradient header background
# Must be PNG: SVG is blocked by Gmail, Outlook, and most email clients
LOGO_URL = "https://encypherai.com/encypher_full_logo_white.png"


# ICP-specific email content configuration
# Messaging aligned with demo pages, not explicit sales copy
ICP_EMAIL_CONFIG = {
    "ai-demo": {
        "subject": "We received your demo request",
        "tagline": "Infrastructure for text provenance in AI pipelines",
        "cta_text": "Continue Exploring",
        "cta_url": "https://encypherai.com/ai-demo",
        "secondary_cta_text": "View Pricing",
        "secondary_cta_url": "https://encypherai.com/pricing?tab=ai-labs",
        "next_steps": [
            "A solutions engineer will reach out within 24 hours",
            "We'll discuss your specific use case",
            "Schedule a personalized walkthrough",
        ],
    },
    "publisher-demo": {
        "subject": "We received your demo request",
        "tagline": "Cryptographic proof of origin for your content",
        "cta_text": "Continue Exploring",
        "cta_url": "https://encypherai.com/publisher-demo",
        "secondary_cta_text": "View Pricing",
        "secondary_cta_url": "https://encypherai.com/pricing?tab=publishers",
        "next_steps": [
            "A member of our team will reach out within 24 hours",
            "We'll discuss your content protection needs",
            "Schedule a personalized demo",
        ],
    },
    "enterprise": {
        "subject": "We received your inquiry",
        "tagline": "Text authentication infrastructure for enterprises",
        "cta_text": "Learn More",
        "cta_url": "https://encypherai.com/pricing?tab=enterprises",
        "secondary_cta_text": "View Solutions",
        "secondary_cta_url": "https://encypherai.com/solutions",
        "next_steps": [
            "An account manager will reach out within 24 hours",
            "We'll discuss your requirements",
            "Schedule a technical deep-dive",
        ],
    },
    "general": {
        "subject": "We received your inquiry",
        "tagline": "Proof of origin for text content",
        "cta_text": "Explore Solutions",
        "cta_url": "https://encypherai.com",
        "secondary_cta_text": "View Pricing",
        "secondary_cta_url": "https://encypherai.com/pricing",
        "next_steps": [
            "A member of our team will reach out within 24 hours",
            "We'll discuss your specific needs",
            "If appropriate, we'll schedule a demo",
        ],
    },
}


def _get_email_config(context: str) -> dict:
    """Get ICP-specific email configuration."""
    return ICP_EMAIL_CONFIG.get(context, ICP_EMAIL_CONFIG["general"])


def send_demo_confirmation(
    to_email: str,
    name: str,
    context: str = "general",
) -> None:
    """Send confirmation email to the requester with ICP-aligned messaging."""
    config = _get_email_config(context)

    subject = config["subject"]

    # Plain text version
    next_steps_text = "\n".join(f"  • {step}" for step in config["next_steps"])
    body = f"""Hello {name},

Thank you for your interest in Encypher.

We've received your request and our team will review it shortly. You can expect to hear from us within 24 hours.

What happens next?
{next_steps_text}

In the meantime, explore more at: {config["cta_url"]}

Best regards,
The Encypher Team

---
Encypher Corporation
https://encypherai.com
"""

    # HTML version with proper branding
    next_steps_html = "".join(f'<li style="margin-bottom: 8px;">{step}</li>' for step in config["next_steps"])

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Roboto', Arial, sans-serif; line-height: 1.6; color: #1b2f50; background-color: #f5f5f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <!-- Header with Logo -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1b2f50 0%, #2a87c4 100%); padding: 40px 30px; text-align: center;">
                            <img src="{LOGO_URL}" alt="Encypher" width="200" style="max-width: 200px; height: auto;">
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 8px 0; color: #1b2f50; font-size: 24px; font-weight: 600;">
                                Hello {name},
                            </h2>
                            
                            <p style="margin: 0 0 24px 0; font-size: 15px; color: #64748b;">
                                {config["tagline"]}
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #1b2f50; font-size: 16px;">
                                Thank you for your interest. We've received your request and our team will review it shortly.
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #1b2f50; font-size: 16px;">
                                You can expect to hear from us within <strong>24 hours</strong>.
                            </p>
                            
                            <h3 style="margin: 28px 0 12px 0; color: #1b2f50; font-size: 16px; font-weight: 600;">
                                What happens next?
                            </h3>
                            
                            <ul style="margin: 0 0 28px 0; padding-left: 20px; color: #64748b; font-size: 15px;">
                                {next_steps_html}
                            </ul>
                            
                            <!-- CTA Buttons -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td align="center" style="padding: 8px 0;">
                                        <a href="{config["cta_url"]}" style="display: inline-block; background-color: #2a87c4; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 15px;">
                                            {config["cta_text"]}
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 8px 0;">
                                        <a href="{config["secondary_cta_url"]}" style="display: inline-block; color: #2a87c4; padding: 10px 20px; text-decoration: none; font-weight: 500; font-size: 14px;">
                                            {config["secondary_cta_text"]}
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 28px 0 0 0; color: #1b2f50; font-size: 15px;">
                                Best regards,<br>
                                <strong>The Encypher Team</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 8px 0; color: #64748b; font-size: 13px;">
                                <a href="https://encypherai.com" style="color: #2a87c4; text-decoration: none;">encypherai.com</a>
                            </p>
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                &copy; 2025 Encypher Corporation. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    email_client.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        html=html,
    )


def send_newsletter_welcome(to_email: str) -> None:
    """Send welcome email to new newsletter subscriber."""
    subject = "You're subscribed to the Encypher blog"

    body = """Welcome to the Encypher blog!

You'll receive an email when we publish new posts on AI provenance, content authentication, and the evolving legal landscape around AI-generated content.

That's it - no spam, just blog posts.

Best regards,
The Encypher Team

---
Encypher - https://encypherai.com
"""

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; line-height: 1.6; color: #1b2f50; background-color: #f5f5f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
        <tr><td align="center" style="padding: 40px 20px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <tr><td style="background: linear-gradient(135deg, #1b2f50 0%, #2a87c4 100%); padding: 40px 30px; text-align: center;">
                    <img src="{LOGO_URL}" alt="Encypher" width="200" style="max-width: 200px; height: auto;">
                </td></tr>
                <tr><td style="padding: 40px 30px;">
                    <h2 style="margin: 0 0 16px 0; color: #1b2f50; font-size: 22px;">You're subscribed!</h2>
                    <p style="margin: 0 0 16px 0; color: #1b2f50; font-size: 15px;">
                        You'll receive an email when we publish new posts on AI provenance, content authentication,
                        and the evolving legal landscape around AI-generated content.
                    </p>
                    <p style="margin: 0 0 24px 0; color: #1b2f50; font-size: 15px;">
                        That's it - no spam, just blog posts.
                    </p>
                    <p style="margin: 28px 0 0 0; color: #1b2f50; font-size: 15px;">
                        Best regards,<br><strong>The Encypher Team</strong>
                    </p>
                </td></tr>
                <tr><td style="background-color: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                        &copy; 2026 Encypher Corporation. All rights reserved.<br>
                        <a href="https://encypherai.com" style="color: #2a87c4; text-decoration: none;">encypherai.com</a>
                    </p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</body>
</html>
"""

    email_client.send_email(to_email=to_email, subject=subject, body=body, html=html)


def send_newsletter_broadcast(
    to_email: str,
    unsubscribe_token: str,
    title: str,
    excerpt: str,
    post_url: str,
    image_url: str | None = None,
    site_url: str = "https://encypherai.com",
) -> None:
    """Send blog post notification email to a newsletter subscriber."""
    unsubscribe_url = f"{site_url}/newsletter/unsubscribe?token={unsubscribe_token}"
    subject = f"New post: {title}"

    body = f"""{title}

{excerpt}

Read the full post: {post_url}

---
You subscribed at encypherai.com/blog.
Unsubscribe: {unsubscribe_url}
"""

    image_html = ""
    if image_url:
        image_html = (
            f'<img src="{image_url}" alt="" width="600" '
            f'style="width: 100%; max-width: 600px; height: auto; '
            f'display: block; border-radius: 8px 8px 0 0;">'
        )

    image_row = ""
    if image_url:
        image_row = f'<tr><td style="padding: 0;">{image_html}</td></tr>'

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; line-height: 1.6; color: #1b2f50; background-color: #f5f5f5;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
        <tr><td align="center" style="padding: 40px 20px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <tr><td style="background: linear-gradient(135deg, #1b2f50 0%, #2a87c4 100%); padding: 24px 30px; text-align: center;">
                    <img src="{LOGO_URL}" alt="Encypher" width="160" style="max-width: 160px; height: auto;">
                </td></tr>
                {image_row}
                <tr><td style="padding: 36px 30px;">
                    <h1 style="margin: 0 0 16px 0; color: #1b2f50; font-size: 24px; line-height: 1.3;">{title}</h1>
                    <p style="margin: 0 0 28px 0; color: #475569; font-size: 15px; line-height: 1.6;">{excerpt}</p>
                    <table role="presentation" cellspacing="0" cellpadding="0">
                        <tr><td style="border-radius: 8px; background-color: #2a87c4;">
                            <a href="{post_url}" style="display: inline-block; padding: 12px 24px; color: #ffffff; text-decoration: none; font-weight: 600; font-size: 15px;">
                                Read the full post
                            </a>
                        </td></tr>
                    </table>
                </td></tr>
                <tr><td style="background-color: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                        You subscribed at encypherai.com/blog.<br>
                        <a href="{unsubscribe_url}" style="color: #94a3b8;">Unsubscribe</a>
                        &nbsp;&middot;&nbsp;
                        <a href="https://encypherai.com" style="color: #2a87c4; text-decoration: none;">encypherai.com</a><br>
                        &copy; 2026 Encypher Corporation. All rights reserved.
                    </p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</body>
</html>
"""

    email_client.send_email(to_email=to_email, subject=subject, body=body, html=html)
