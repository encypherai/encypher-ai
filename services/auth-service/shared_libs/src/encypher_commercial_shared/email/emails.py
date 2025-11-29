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

Thanks for signing up for EncypherAI! To complete your registration, please verify your email address by visiting:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account with EncypherAI, you can safely ignore this email.

— The EncypherAI Team
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject="Verify your email address - EncypherAI",
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
        config=config,
        to_email=to_email,
        subject="Welcome to EncypherAI! 🎉",
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

We received a request to reset the password for your EncypherAI account. Visit the link below to create a new password:

{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.

— The EncypherAI Team
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject="Reset your password - EncypherAI",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_team_invitation_email(
    config: EmailConfig,
    to_email: str,
    organization_name: str,
    inviter_name: str,
    role: str,
    invitation_token: str,
    message: Optional[str] = None,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send team invitation email.
    
    Args:
        config: Email configuration
        to_email: Recipient email
        organization_name: Name of the organization
        inviter_name: Name of the person who sent the invitation
        role: Role being offered (admin, manager, member, viewer)
        invitation_token: The invitation token
        message: Optional personal message from inviter
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"
    invitation_url = f"{dashboard_url}/invite/{invitation_token}"
    
    html_content = render_template(
        "team_invitation.html",
        subject=f"You're invited to join {organization_name}",
        organization_name=organization_name,
        inviter_name=inviter_name,
        role=role,
        invitation_url=invitation_url,
        message=message,
    )
    
    plain_content = f"""
You're invited to join {organization_name}

Hi there,

{inviter_name} has invited you to join {organization_name} on EncypherAI as a {role}.

{f'"{message}" — {inviter_name}' if message else ''}

Accept the invitation by visiting:
{invitation_url}

This invitation will expire in 7 days.

What you'll get access to:
- C2PA-compliant content signing and verification
- Shared API keys and usage analytics
- Team collaboration features
- Centralized billing and management

If you don't recognize {inviter_name} or {organization_name}, you can safely ignore this email.

— The EncypherAI Team
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject=f"You're invited to join {organization_name} on EncypherAI",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_role_changed_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    organization_name: str,
    old_role: str,
    new_role: str,
    changed_by: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send role change notification email.
    
    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        organization_name: Name of the organization
        old_role: Previous role
        new_role: New role
        changed_by: Name of person who made the change
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"
    
    html_content = render_template(
        "role_changed.html",
        subject=f"Your role in {organization_name} has been updated",
        user_name=user_name,
        organization_name=organization_name,
        old_role=old_role,
        new_role=new_role,
        changed_by=changed_by,
        dashboard_url=dashboard_url,
    )
    
    plain_content = f"""
Your role has been updated

Hi{' ' + user_name if user_name else ''},

Your role in {organization_name} has been changed from {old_role} to {new_role}.

Changed by: {changed_by}

View Team Settings: {dashboard_url}/team

If you have questions about this change, please contact your organization administrator.

— The EncypherAI Team
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject=f"Your role in {organization_name} has been updated",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )


def send_member_removed_email(
    config: EmailConfig,
    to_email: str,
    user_name: Optional[str],
    organization_name: str,
    organization_email: str,
    logger: Optional[Any] = None,
) -> bool:
    """
    Send member removal notification email.
    
    Args:
        config: Email configuration
        to_email: Recipient email
        user_name: User's name (optional)
        organization_name: Name of the organization
        organization_email: Contact email for the organization
        logger: Optional logger
        
    Returns:
        True if sent successfully
    """
    dashboard_url = config.dashboard_url or f"{config.frontend_url}/dashboard"
    
    html_content = render_template(
        "member_removed.html",
        subject=f"You've been removed from {organization_name}",
        user_name=user_name,
        organization_name=organization_name,
        organization_email=organization_email,
        dashboard_url=dashboard_url,
    )
    
    plain_content = f"""
You've been removed from {organization_name}

Hi{' ' + user_name if user_name else ''},

This email is to inform you that you have been removed from {organization_name} on EncypherAI.

You no longer have access to this organization's resources, API keys, or team features.

What happens now:
- Your access to {organization_name}'s API keys has been revoked
- You can no longer view the organization's analytics or audit logs
- Any content you signed will remain valid

If you believe this was done in error, please contact the organization administrator at {organization_email}.

Go to Dashboard: {dashboard_url}

You can still use EncypherAI with your personal account or join other organizations.

— The EncypherAI Team
"""
    
    return send_email(
        config=config,
        to_email=to_email,
        subject=f"You've been removed from {organization_name}",
        html_content=html_content,
        plain_content=plain_content.strip(),
        logger=logger,
    )
