#!/usr/bin/env python3
"""
Email Template Preview Script

Opens all email templates in your default browser for visual review.
Run from the web-service directory:
    uv run python scripts/preview_email_templates.py
"""

import tempfile
import webbrowser
from pathlib import Path

# Logo URL - hosted on production site
# White logo used on blue gradient header background
LOGO_URL = "https://encypherai.com/encypher_full_logo_white.svg"


def generate_demo_notification_html() -> str:
    """Generate sample demo notification email HTML (internal/sales team)."""
    return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2563eb;">New AI Demo Request</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">John Smith</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="mailto:john.smith@acme.com">john.smith@acme.com</a></td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Organization:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Acme Corporation</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Role:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">VP of Engineering</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">ai-demo</td></tr>
    </table>
    <h3 style="margin-top: 20px;">Message:</h3>
    <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        We're interested in integrating Encypher's AI detection capabilities into our content management platform. 
        We handle approximately 10,000 articles per day and need a scalable solution.
    </p>
    <p style="color: #666; font-size: 12px; margin-top: 20px;">
        Request ID: 550e8400-e29b-41d4-a716-446655440000
    </p>
</body>
</html>
"""


def generate_confirmation_html(
    name: str,
    tagline: str,
    next_steps: list[str],
    cta_text: str,
    cta_url: str,
    secondary_cta_text: str,
    secondary_cta_url: str,
) -> str:
    """Generate branded confirmation email HTML."""
    next_steps_html = "".join(f'<li style="margin-bottom: 8px;">{step}</li>' for step in next_steps)

    return f"""
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
                                {tagline}
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
                                        <a href="{cta_url}" style="display: inline-block; background-color: #2a87c4; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 15px;">
                                            {cta_text}
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 8px 0;">
                                        <a href="{secondary_cta_url}" style="display: inline-block; color: #2a87c4; padding: 10px 20px; text-decoration: none; font-weight: 500; font-size: 14px;">
                                            {secondary_cta_text}
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


def generate_ai_demo_confirmation_html() -> str:
    """Generate AI Labs ICP confirmation email."""
    return generate_confirmation_html(
        name="John",
        tagline="Real-world performance intelligence for AI",
        next_steps=[
            "A solutions engineer will reach out within 24 hours",
            "We'll discuss your specific use case",
            "Schedule a personalized walkthrough",
        ],
        cta_text="Continue Exploring",
        cta_url="https://encypherai.com/ai-demo",
        secondary_cta_text="View Pricing",
        secondary_cta_url="https://encypherai.com/pricing?tab=ai-labs",
    )


def generate_publisher_notification_html() -> str:
    """Generate sample publisher demo notification email HTML (internal/sales team)."""
    return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2563eb;">New Publisher Demo Request</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Sarah Johnson</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="mailto:sarah@newsoutlet.com">sarah@newsoutlet.com</a></td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Organization:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">News Outlet Inc.</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Role:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Head of Digital Content</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">publisher-demo</td></tr>
    </table>
    <h3 style="margin-top: 20px;">Message:</h3>
    <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        Looking for content protection and attribution solutions for our online publication. 
        We publish 500+ articles daily and need to protect our content from unauthorized AI training.
    </p>
    <p style="color: #666; font-size: 12px; margin-top: 20px;">
        Request ID: 660e8400-e29b-41d4-a716-446655440001
    </p>
</body>
</html>
"""


def generate_publisher_confirmation_html() -> str:
    """Generate Publisher ICP confirmation email."""
    return generate_confirmation_html(
        name="Sarah",
        tagline="Content authentication for the AI era",
        next_steps=[
            "A member of our team will reach out within 24 hours",
            "We'll discuss your content protection needs",
            "Schedule a personalized demo",
        ],
        cta_text="Continue Exploring",
        cta_url="https://encypherai.com/publisher-demo",
        secondary_cta_text="View Pricing",
        secondary_cta_url="https://encypherai.com/pricing?tab=publishers",
    )


def generate_enterprise_notification_html() -> str:
    """Generate sample enterprise sales notification email HTML (internal/sales team)."""
    return """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2563eb;">New Enterprise Sales Request</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Michael Chen</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;"><a href="mailto:mchen@enterprise.com">mchen@enterprise.com</a></td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Organization:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">Enterprise Solutions Ltd.</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Role:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">CTO</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">enterprise-contact</td></tr>
    </table>
    <h3 style="margin-top: 20px;">Message:</h3>
    <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        We need an enterprise-grade solution for content authentication across our global network. 
        Looking for API integration, SSO support, and dedicated account management.
    </p>
    <p style="color: #666; font-size: 12px; margin-top: 20px;">
        Request ID: 770e8400-e29b-41d4-a716-446655440002
    </p>
</body>
</html>
"""


def generate_enterprise_confirmation_html() -> str:
    """Generate Enterprise ICP confirmation email."""
    return generate_confirmation_html(
        name="Michael",
        tagline="Enterprise content authentication",
        next_steps=[
            "An account manager will reach out within 24 hours",
            "We'll discuss your requirements",
            "Schedule a technical deep-dive",
        ],
        cta_text="Learn More",
        cta_url="https://encypherai.com/pricing?tab=enterprises",
        secondary_cta_text="View Solutions",
        secondary_cta_url="https://encypherai.com/solutions",
    )


def generate_index_html(templates: dict[str, str]) -> str:
    """Generate an index page with links to all templates."""
    links = ""
    for name in templates:
        links += f'<li><a href="{name}.html" target="_blank">{name.replace("_", " ").title()}</a></li>\n'

    return """
<!DOCTYPE html>
<html>
<head>
    <title>Encypher Email Templates Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #1b2f50;
            border-bottom: 2px solid #2a87c4;
            padding-bottom: 10px;
        }
        .template-list {
            list-style: none;
            padding: 0;
        }
        .template-list li {
            margin: 10px 0;
            padding: 15px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .template-list a {
            color: #2a87c4;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
        }
        .template-list a:hover {
            text-decoration: underline;
        }
        .category {
            margin-top: 30px;
        }
        .category h2 {
            color: #64748b;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <h1>📧 Encypher Email Templates</h1>
    <p>Click on any template to preview it in a new tab.</p>
    
    <div class="category">
        <h2>AI Demo Emails</h2>
        <ul class="template-list">
            <li><a href="ai_demo_notification.html" target="_blank">AI Demo - Sales Notification</a></li>
            <li><a href="ai_demo_confirmation.html" target="_blank">AI Demo - User Confirmation</a></li>
        </ul>
    </div>
    
    <div class="category">
        <h2>Publisher Demo Emails</h2>
        <ul class="template-list">
            <li><a href="publisher_notification.html" target="_blank">Publisher Demo - Sales Notification</a></li>
            <li><a href="publisher_confirmation.html" target="_blank">Publisher Demo - User Confirmation</a></li>
        </ul>
    </div>
    
    <div class="category">
        <h2>Enterprise Sales Emails</h2>
        <ul class="template-list">
            <li><a href="enterprise_notification.html" target="_blank">Enterprise - Sales Notification</a></li>
            <li><a href="enterprise_confirmation.html" target="_blank">Enterprise - User Confirmation</a></li>
        </ul>
    </div>
</body>
</html>
"""


def main() -> None:
    """Generate and open email template previews in browser."""
    templates = {
        "ai_demo_notification": generate_demo_notification_html(),
        "ai_demo_confirmation": generate_ai_demo_confirmation_html(),
        "publisher_notification": generate_publisher_notification_html(),
        "publisher_confirmation": generate_publisher_confirmation_html(),
        "enterprise_notification": generate_enterprise_notification_html(),
        "enterprise_confirmation": generate_enterprise_confirmation_html(),
    }

    # Create temp directory for HTML files
    temp_dir = Path(tempfile.mkdtemp(prefix="encypher_email_preview_"))
    print(f"📁 Creating preview files in: {temp_dir}")

    # Write each template
    for name, html in templates.items():
        file_path = temp_dir / f"{name}.html"
        file_path.write_text(html, encoding="utf-8")
        print(f"  ✓ {name}.html")

    # Write index page
    index_path = temp_dir / "index.html"
    index_path.write_text(generate_index_html(templates), encoding="utf-8")
    print("  ✓ index.html")

    # Open index in browser
    print("\n🌐 Opening email templates in your default browser...")
    webbrowser.open(f"file://{index_path}")

    print(f"\n✅ Done! Preview files are in: {temp_dir}")
    print("   (These will be cleaned up when you restart your computer)")


if __name__ == "__main__":
    main()
