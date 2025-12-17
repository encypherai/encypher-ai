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
    # Use dashboard_url for auth pages, fall back to frontend_url
    base_url = config.dashboard_url or config.frontend_url
    verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
    
    html_content = render_template(
        "email_verification.html",
        subject="Verify your email address",
        user_name=user_name,
        verification_url=verification_url,
    )
    
    plain_content = f"""
Verify your email address

Hi{' ' + user_name if user_name else ''},

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

Hi{' ' + user_name if user_name else ''},

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


def send_api_access_request_admin_email(
    config: EmailConfig,
    admin_email: str,
    user_email: str,
    user_name: Optional[str],
    admin_url: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send notification to admin about new API access request.
    
    Args:
        config: Email configuration
        admin_email: Admin's email address
        user_email: Requesting user's email
        user_name: Requesting user's name (optional)
        admin_url: URL to admin panel for approval
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    plain_content = f"""
New API Access Request

A user has requested API access:

User: {user_name or 'Unknown'} ({user_email})

Please review and approve/deny this request at:
{admin_url}

— Encypher System
"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<h2>New API Access Request</h2>
<p>A user has requested API access:</p>
<ul>
<li><strong>Name:</strong> {user_name or 'Unknown'}</li>
<li><strong>Email:</strong> {user_email}</li>
</ul>
<p><a href="{admin_url}" style="background: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Request</a></p>
<p style="color: #666; font-size: 12px;">— Encypher System</p>
</body>
</html>
"""
    
    return send_email(
        config=config,
        to_email=admin_email,
        subject="New API Access Request - Encypher",
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
    Send API access approval notification to user.
    
    Args:
        config: Email configuration
        to_email: User's email address
        user_name: User's name (optional)
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"
    
    plain_content = f"""
Your API Access Has Been Approved!

Hi{' ' + user_name if user_name else ''},

Great news! Your request for API access has been approved. You can now generate API keys and start integrating Encypher into your applications.

Get started:
{dashboard_url}/api-keys

Need help? Check out our documentation at https://encypherai.com/docs

— The Encypher Team
"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<h2>Your API Access Has Been Approved! 🎉</h2>
<p>Hi{' ' + user_name if user_name else ''},</p>
<p>Great news! Your request for API access has been approved. You can now generate API keys and start integrating Encypher into your applications.</p>
<p><a href="{dashboard_url}/api-keys" style="background: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Generate API Keys</a></p>
<p>Need help? Check out our <a href="https://encypherai.com/docs">documentation</a>.</p>
<p style="color: #666;">— The Encypher Team</p>
</body>
</html>
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject="Your API Access Has Been Approved! - Encypher",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_api_access_denied_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    reason: Optional[str] = None,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send API access denial notification to user.
    
    Args:
        config: Email configuration
        to_email: User's email address
        user_name: User's name (optional)
        reason: Reason for denial (optional)
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    reason_text = f"\n\nReason: {reason}" if reason else ""
    
    plain_content = f"""
API Access Request Update

Hi{' ' + user_name if user_name else ''},

Thank you for your interest in Encypher. After reviewing your request, we're unable to approve API access at this time.{reason_text}

If you believe this was in error or have questions, please contact us at support@encypherai.com.

— The Encypher Team
"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
<h2>API Access Request Update</h2>
<p>Hi{' ' + user_name if user_name else ''},</p>
<p>Thank you for your interest in Encypher. After reviewing your request, we're unable to approve API access at this time.</p>
{f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
<p>If you believe this was in error or have questions, please contact us at <a href="mailto:support@encypherai.com">support@encypherai.com</a>.</p>
<p style="color: #666;">— The Encypher Team</p>
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
