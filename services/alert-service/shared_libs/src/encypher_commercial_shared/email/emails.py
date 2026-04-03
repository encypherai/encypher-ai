"""
Pre-built email functions for common use cases.

These functions combine template rendering with sending for convenience.
"""

import html
import re
from typing import Any, Optional

from .sender import EmailConfig, render_template, send_email


HTML_TAG_RE = re.compile(r"<[^>]+>")
URL_LIKE_RE = re.compile(r"(https?://|www\.)", re.IGNORECASE)


def sanitize_user_name(user_name: Optional[str]) -> Optional[str]:
    if not user_name:
        return None
    cleaned = HTML_TAG_RE.sub("", user_name).strip()
    if not cleaned:
        return None
    if URL_LIKE_RE.search(cleaned):
        return None
    return cleaned


def _escape_html(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return html.escape(value, quote=True)


def send_verification_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    verification_token: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send email verification email.

    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        verification_token: The verification token
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    # Use dashboard_url for auth pages, fall back to frontend_url
    base_url = config.dashboard_url or config.frontend_url
    verification_url = f"{base_url}/auth/verify-email?token={verification_token}"

    safe_user_name = sanitize_user_name(user_name)

    html_content = render_template(
        "email_verification.html",
        subject="Verify your email address",
        user_name=safe_user_name,
        verification_url=verification_url,
    )

    plain_content = f"""
Verify your email address

Hi{" " + safe_user_name if safe_user_name else ""},

Thanks for signing up for Encypher! To complete your registration, please verify your email address by visiting:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with Encypher, you can safely ignore this email.

- The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Verify your email address - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        bcc_email=config.support_email if config.support_email else None,
        logger=logger,
    )


def send_welcome_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    logger: Optional[Any] = None,
) -> bool:
    """
    Send welcome email after verification.

    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"

    safe_user_name = sanitize_user_name(user_name)

    html_content = render_template(
        "welcome.html",
        subject="Welcome to Encypher!",
        user_name=safe_user_name,
        dashboard_url=dashboard_url,
    )

    plain_content = f"""
Welcome to Encypher!

Hi{" " + safe_user_name if safe_user_name else ""},

Your email has been verified and your account is now active. You're all set to start embedding cryptographic proof of origin in your content.

Here's what you can do next:
- Generate API Keys - Integrate text authentication into your applications
- Explore the Dashboard - Monitor your usage and manage your account
- Read the Docs - Learn how to embed cryptographic watermarking in text content

Go to Dashboard: {dashboard_url}

Need help? Check out our documentation at https://encypher.com/docs or email support@encypher.com.

Encipher provides infrastructure for text provenance - cryptographic proof of origin that survives copy-paste and distribution.

- The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Welcome to Encypher!",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_password_reset_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    reset_token: str,
    ip_address: Optional[str] = None,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send password reset email.

    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        reset_token: The password reset token
        ip_address: IP address of requester (optional, for security info)
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    # Use dashboard_url for auth pages, fall back to frontend_url
    base_url = config.dashboard_url or config.frontend_url
    reset_url = f"{base_url}/reset-password/{reset_token}"

    safe_user_name = sanitize_user_name(user_name)

    html_content = render_template(
        "password_reset.html",
        subject="Reset your password",
        user_name=safe_user_name,
        reset_url=reset_url,
        ip_address=ip_address,
    )

    plain_content = f"""
Reset your password

Hi{" " + safe_user_name if safe_user_name else ""},

We received a request to reset the password for your Encypher account. Visit the link below to create a new password:

{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

- The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Reset your password - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_api_access_request_admin_email(
    config: EmailConfig,
    to_email: str,
    requester_name: Optional[str],
    requester_email: str,
    use_case: str,
    requested_at: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send notification to admin about new API access request.

    Args:
        config: Email configuration
        to_email: Admin email address
        requester_name: Name of user requesting access
        requester_email: Email of user requesting access
        use_case: User's stated use case
        requested_at: When the request was made
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    base_url = config.dashboard_url or config.frontend_url
    admin_url = f"{base_url}/admin/api-access"

    safe_requester_name = sanitize_user_name(requester_name)
    safe_requester_name_html = _escape_html(safe_requester_name)
    safe_requester_email_html = _escape_html(requester_email)
    safe_use_case_html = _escape_html(use_case)
    safe_requested_at_html = _escape_html(requested_at)

    plain_content = f"""
New API Access Request

A user has requested API access:

Name: {safe_requester_name or "Not provided"}
Email: {requester_email}
Requested: {requested_at}

Use Case:
{use_case}

Review this request at: {admin_url}

- Encypher System
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>New API Access Request</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px;">
    <h2 style="color: #1d3557;">New API Access Request</h2>
    <p>A user has requested API access:</p>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr><td style="padding: 8px; font-weight: bold;">Name:</td><td style="padding: 8px;">{safe_requester_name_html or "Not provided"}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Email:</td><td style="padding: 8px;">{safe_requester_email_html}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Requested:</td><td style="padding: 8px;">{safe_requested_at_html}</td></tr>
    </table>
    <h3 style="color: #457b9d;">Use Case:</h3>
    <p style="background: #f4f7fa; padding: 15px; border-radius: 8px;">{safe_use_case_html}</p>
    <p><a href="{admin_url}" style="display: inline-block; background: #1d3557; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Review Request</a></p>
</body>
</html>
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject=f"[Action Required] New API Access Request from {requester_email}",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_api_access_approved_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    logger: Optional[Any] = None,
) -> bool:
    """
    Send notification to user that their API access was approved.
    """
    base_url = config.dashboard_url or config.frontend_url
    api_keys_url = f"{base_url}/settings/api-keys"

    safe_user_name = sanitize_user_name(user_name)
    safe_user_name_html = _escape_html(safe_user_name)

    plain_content = f"""
API Access Approved!

Hi{" " + safe_user_name if safe_user_name else ""},

Great news! Your API access request has been approved.

You can now generate API keys and start using the Encypher API.

Get started: {api_keys_url}

- The Encypher Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>API Access Approved</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px;">
    <h2 style="color: #2d6a4f;">API Access Approved!</h2>
    <p>Hi{" " + safe_user_name_html if safe_user_name_html else ""},</p>
    <p>Great news! Your API access request has been approved.</p>
    <p>You can now generate API keys and start using the Encypher API.</p>
    <p><a href="{api_keys_url}" style="display: inline-block; background: #2d6a4f; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Generate API Keys</a></p>
    <p style="color: #666; margin-top: 20px;">- The Encypher Team</p>
</body>
</html>
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Your API Access Has Been Approved - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_api_access_denied_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    denial_reason: Optional[str] = None,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send notification to user that their API access was denied.
    """
    reason_text = denial_reason or "Your use case did not meet our current requirements."

    safe_user_name = sanitize_user_name(user_name)
    safe_user_name_html = _escape_html(safe_user_name)
    safe_reason_html = _escape_html(reason_text)

    plain_content = f"""
API Access Request Update

Hi{" " + safe_user_name if safe_user_name else ""},

Thank you for your interest in the Encypher API. After reviewing your request, we were unable to approve it at this time.

Reason: {reason_text}

If you believe this was in error or would like to provide additional information, please reply to this email.

- The Encypher Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>API Access Request Update</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px;">
    <h2 style="color: #1d3557;">API Access Request Update</h2>
    <p>Hi{" " + safe_user_name_html if safe_user_name_html else ""},</p>
    <p>Thank you for your interest in the Encypher API. After reviewing your request, we were unable to approve it at this time.</p>
    <p style="background: #f4f7fa; padding: 15px; border-radius: 8px;"><strong>Reason:</strong> {safe_reason_html}</p>
    <p>If you believe this was in error or would like to provide additional information, please reply to this email.</p>
    <p style="color: #666; margin-top: 20px;">- The Encypher Team</p>
</body>
</html>
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="API Access Request Update - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_new_signup_admin_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    user_email: str,
    signup_method: str = "email",
    logger: Optional[Any] = None,
) -> bool:
    """
    Send notification to admin about new user signup.

    Args:
        config: Email configuration
        to_email: Admin/support email address
        user_name: Name of new user
        user_email: Email of new user
        signup_method: How they signed up (email, google, github)
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    method_display = {
        "email": "Email/Password",
        "google": "Google OAuth",
        "github": "GitHub OAuth",
    }.get(signup_method, signup_method.title())

    safe_user_name = sanitize_user_name(user_name)
    safe_user_name_html = _escape_html(safe_user_name)
    safe_user_email_html = _escape_html(user_email)
    safe_method_display_html = _escape_html(method_display)

    plain_content = f"""
New User Signup

A new user has signed up for Encypher:

Name: {safe_user_name or "Not provided"}
Email: {user_email}
Method: {method_display}

- Encypher System
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head><title>New User Signup</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px;">
    <h2 style="color: #1d3557;">New User Signup</h2>
    <p>A new user has signed up for Encypher:</p>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr><td style="padding: 8px; font-weight: bold;">Name:</td><td style="padding: 8px;">{safe_user_name_html or "Not provided"}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Email:</td><td style="padding: 8px;">{safe_user_email_html}</td></tr>
        <tr><td style="padding: 8px; font-weight: bold;">Method:</td><td style="padding: 8px;">{safe_method_display_html}</td></tr>
    </table>
</body>
</html>
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject=f"New Signup: {user_email} ({method_display})",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )
