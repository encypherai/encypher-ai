"""
Pre-built email functions for common use cases.

These functions combine template rendering with sending for convenience.
"""

from typing import Any, Optional

from .sender import EmailConfig, render_template, send_email


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
    verification_url = f"{config.frontend_url}/auth/verify-email?token={verification_token}"

    html_content = render_template(
        "email_verification.html",
        subject="Verify your email address",
        user_name=user_name,
        verification_url=verification_url,
    )

    plain_content = f"""
Verify your email address

Hi{" " + user_name if user_name else ""},

Thanks for signing up for Encypher! To complete your registration, please verify your email address by visiting:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with Encypher, you can safely ignore this email.

— The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Verify your email address - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
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

    html_content = render_template(
        "welcome.html",
        subject="Welcome to Encypher!",
        user_name=user_name,
        dashboard_url=dashboard_url,
    )

    plain_content = f"""
Welcome to Encypher!

Hi{" " + user_name if user_name else ""},

Your email has been verified and your account is now active. You're all set to start making AI transparent and trustworthy!

Here's what you can do next:
- Generate API Keys – Create keys to integrate Encypher into your applications
- Explore the Dashboard – Monitor your usage and manage your account
- Read the Docs – Learn how to embed provenance metadata in AI-generated content

Go to Dashboard: {dashboard_url}

Need help? Check out our documentation at https://encypherai.com/docs or email support@encypherai.com.

— The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Welcome to Encypher! 🎉",
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
    reset_url = f"{config.frontend_url}/auth/reset-password?token={reset_token}"

    html_content = render_template(
        "password_reset.html",
        subject="Reset your password",
        user_name=user_name,
        reset_url=reset_url,
        ip_address=ip_address,
    )

    plain_content = f"""
Reset your password

Hi{" " + user_name if user_name else ""},

We received a request to reset the password for your Encypher account. Visit the link below to create a new password:

{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

— The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Reset your password - Encypher",
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
    Send email notifying user their API access was approved.

    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"

    html_content = render_template(
        "api_access_approved.html",
        subject="Your API Access Has Been Approved!",
        user_name=user_name,
        dashboard_url=dashboard_url,
    )

    plain_content = f"""
Your API Access Has Been Approved!

Hi{" " + user_name if user_name else ""},

Great news! Your request for API access has been approved. You can now generate API keys and start integrating Encypher into your applications.

What's next?
- Generate an API key – Create your first key in the dashboard
- Install our SDK – Available for Python, JavaScript, and more
- Start signing content – Add C2PA provenance to your AI-generated content

Go to Dashboard: {dashboard_url}/api-keys

Check out our documentation at https://encypherai.com/docs to get started quickly.

— The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="Your API Access Has Been Approved! 🎉 - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_api_access_denied_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    denial_reason: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send email notifying user their API access was denied.

    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        denial_reason: Reason for denial
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"

    html_content = render_template(
        "api_access_denied.html",
        subject="API Access Request Update",
        user_name=user_name,
        dashboard_url=dashboard_url,
        denial_reason=denial_reason,
    )

    plain_content = f"""
API Access Request Update

Hi{" " + user_name if user_name else ""},

Thank you for your interest in Encypher. After reviewing your API access request, we were unable to approve it at this time.

Reason: {denial_reason}

You can re-apply! If you believe this was in error or would like to provide more details about your use case, you're welcome to submit a new request.

Go to Dashboard: {dashboard_url}/api-keys

If you have questions or need clarification, please reach out to us at support@encypherai.com.

— The Encypher Team
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject="API Access Request Update - Encypher",
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
    Send email to admin notifying of new API access request.

    Args:
        config: Email configuration
        to_email: Admin email
        requester_name: Name of user requesting access
        requester_email: Email of user requesting access
        use_case: The use case description
        requested_at: When the request was made
        logger: Optional logger

    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"
    admin_url = f"{dashboard_url}/admin"

    html_content = render_template(
        "api_access_request_admin.html",
        subject="New API Access Request",
        requester_name=requester_name,
        requester_email=requester_email,
        use_case=use_case,
        requested_at=requested_at,
        admin_url=admin_url,
    )

    plain_content = f"""
New API Access Request

A new API access request requires your review.

Name: {requester_name or "Not provided"}
Email: {requester_email}
Use Case: {use_case}
Requested: {requested_at}

Review in Admin Dashboard: {admin_url}

— Encypher System
"""

    return send_email(
        config=config,
        to_email=to_email,
        subject=f"New API Access Request from {requester_email} - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )
