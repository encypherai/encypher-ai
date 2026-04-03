#!/usr/bin/env python3
"""
Email Template Preview Generator

This script renders all email templates and creates an HTML preview page
that can be opened in a browser for visual review.

Usage:
    python preview_email_templates.py

The script will:
1. Render all email templates with sample data
2. Generate a preview HTML file
3. Automatically open it in your default browser
"""

import webbrowser
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.encypher_commercial_shared.email.sender import render_template


def generate_preview_html() -> str:
    """Generate HTML preview of all email templates."""

    # Sample data for each template
    templates = {
        "Email Verification": {
            "template": "email_verification.html",
            "context": {
                "subject": "Verify your email address",
                "user_name": "Alex Johnson",
                "verification_url": "https://dashboard.encypherai.com/auth/verify-email?token=abc123xyz789",
            },
        },
        "Welcome Email": {
            "template": "welcome.html",
            "context": {
                "subject": "Welcome to Encypher!",
                "user_name": "Alex Johnson",
                "dashboard_url": "https://dashboard.encypherai.com",
            },
        },
        "Password Reset": {
            "template": "password_reset.html",
            "context": {
                "subject": "Reset your password",
                "user_name": "Alex Johnson",
                "reset_url": "https://dashboard.encypherai.com/reset-password/abc123xyz789",
                "ip_address": "192.168.1.100",
            },
        },
    }

    # Render each template
    rendered_templates = {}
    for name, config in templates.items():
        try:
            html = render_template(config["template"], **config["context"])
            rendered_templates[name] = html
        except Exception as e:
            rendered_templates[name] = f"<div style='color: red; padding: 20px;'>Error rendering template: {e}</div>"

    # Create preview page
    preview_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encypher Email Templates Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1b2f50 0%, #2a87c4 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 36px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .nav {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
        }}
        
        .nav h2 {{
            font-size: 18px;
            color: #1b2f50;
            margin-bottom: 16px;
        }}
        
        .nav-links {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .nav-links a {{
            display: inline-block;
            padding: 10px 20px;
            background: #f8fafc;
            color: #1b2f50;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
            border: 2px solid transparent;
        }}
        
        .nav-links a:hover {{
            background: #2a87c4;
            color: white;
            transform: translateY(-2px);
        }}
        
        .template-section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
        }}
        
        .template-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .template-header h2 {{
            font-size: 24px;
            color: #1b2f50;
        }}
        
        .template-meta {{
            display: flex;
            gap: 16px;
            font-size: 14px;
            color: #64748b;
        }}
        
        .template-meta span {{
            padding: 6px 12px;
            background: #f8fafc;
            border-radius: 6px;
        }}
        
        .template-preview {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            background: #f4f7fa;
        }}
        
        .template-preview iframe {{
            width: 100%;
            min-height: 600px;
            border: none;
            display: block;
        }}
        
        .brand-check {{
            background: #f8fafc;
            border-left: 4px solid #2a87c4;
            padding: 16px;
            margin-top: 20px;
            border-radius: 4px;
        }}
        
        .brand-check h3 {{
            font-size: 14px;
            color: #1b2f50;
            margin-bottom: 8px;
        }}
        
        .brand-check ul {{
            list-style: none;
            font-size: 13px;
            color: #64748b;
        }}
        
        .brand-check li {{
            padding: 4px 0;
        }}
        
        .brand-check li::before {{
            content: "✓ ";
            color: #2a87c4;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 Email Templates Preview</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
        
        <div class="nav">
            <h2>Quick Navigation</h2>
            <div class="nav-links">
"""

    # Add navigation links
    for name in rendered_templates.keys():
        anchor = name.lower().replace(" ", "-")
        preview_html += f'                <a href="#{anchor}">{name}</a>\n'

    preview_html += """
            </div>
        </div>
"""

    # Add each template preview
    for name, html in rendered_templates.items():
        anchor = name.lower().replace(" ", "-")
        preview_html += f"""
        <div class="template-section" id="{anchor}">
            <div class="template-header">
                <h2>{name}</h2>
                <div class="template-meta">
                    <span>📱 Responsive</span>
                    <span>🎨 Brand Colors</span>
                </div>
            </div>
            
            <div class="template-preview">
                <iframe srcdoc="{html.replace('"', "&quot;")}"></iframe>
            </div>
            
            <div class="brand-check">
                <h3>Brand Alignment Checklist:</h3>
                <ul>
                    <li>Uses official color palette (#1b2f50, #2a87c4)</li>
                    <li>Emphasizes "proof of origin" messaging</li>
                    <li>Focuses on text authentication infrastructure</li>
                    <li>Avoids generic "AI transparency" language</li>
                </ul>
            </div>
        </div>
"""

    preview_html += """
        <div class="footer">
            <p>Encypher Corporation • Cryptographic proof of origin for text content</p>
        </div>
    </div>
</body>
</html>
"""

    return preview_html


def main():
    """Generate preview and open in browser."""
    print("🔨 Generating email template previews...")

    try:
        # Generate preview HTML
        preview_html = generate_preview_html()

        # Create temporary file
        with NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(preview_html)
            temp_path = f.name

        print(f"✅ Preview generated: {temp_path}")
        print("🌐 Opening in browser...")

        # Open in browser
        webbrowser.open(f"file://{temp_path}")

        print("✨ Done! Preview should open in your default browser.")
        print(f"\nℹ️  Preview file location: {temp_path}")
        print("   (This temporary file will be cleaned up on next system restart)")

    except Exception as e:
        print(f"❌ Error generating preview: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
