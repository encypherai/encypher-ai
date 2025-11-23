import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject_template
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_EMAIL}>"
    message["To"] = email_to

    html_content = html_template
    # Simple template replacement
    for key, value in environment.items():
        html_content = html_content.replace(f"{{{{ {key} }}}}", str(value))

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        
        if settings.SMTP_PORT == 465:
             with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmessage(message)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmessage(message)
        
        logger.info(f"Sent email to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")

def send_new_lead_notification(demo_request: Any) -> None:
    """
    Send notification to sales team about a new lead.
    """
    if not settings.EMAILS_ENABLED:
        logger.warning("Email sending is disabled. Skipping lead notification.")
        return

    subject = f"New Demo Request: {demo_request.organization}"
    
    html_content = f"""
    <html>
        <body>
            <h2>New Demo Request</h2>
            <p><strong>Name:</strong> {demo_request.name}</p>
            <p><strong>Email:</strong> {demo_request.email}</p>
            <p><strong>Organization:</strong> {demo_request.organization}</p>
            <p><strong>Role:</strong> {demo_request.role}</p>
            <p><strong>Source:</strong> {demo_request.source}</p>
            <p><strong>Message:</strong></p>
            <p>{demo_request.message}</p>
            <br>
            <p>
                <a href="https://dashboard.encypherai.com/admin/leads/{demo_request.id}">
                    View in Dashboard
                </a>
            </p>
        </body>
    </html>
    """
    
    # In a real scenario, we'd have a sales email in settings
    sales_email = "sales@encypherai.com" 
    
    send_email(
        email_to=sales_email,
        subject_template=subject,
        html_template=html_content,
    )

def send_demo_confirmation(email_to: str, name: str) -> None:
    """
    Send confirmation email to the user who requested a demo.
    """
    if not settings.EMAILS_ENABLED:
        return

    subject = "We've received your demo request - EncypherAI"
    
    html_content = f"""
    <html>
        <body>
            <h2>Hi {name},</h2>
            <p>Thanks for your interest in EncypherAI.</p>
            <p>We've received your request for a demo. One of our team members will be in touch shortly to schedule a time that works for you.</p>
            <p>In the meantime, feel free to check out our <a href="https://encypherai.com/docs">documentation</a>.</p>
            <br>
            <p>Best regards,</p>
            <p>The EncypherAI Team</p>
        </body>
    </html>
    """
    
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_content,
    )
