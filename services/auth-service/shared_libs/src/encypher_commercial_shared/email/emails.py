"""
Pre-built email functions for common use cases.

These functions combine template rendering with sending for convenience.
"""

from typing import Optional, Any

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
