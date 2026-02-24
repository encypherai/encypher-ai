"""Send a review-needed notification email when the blog-writer opens a draft PR."""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

NOTIFY_TO = "erik.svilich@encypherai.com"

pr_url = os.environ.get("PR_URL", "").strip()
smtp_host = os.environ.get("SMTP_HOST", "").strip()
smtp_port = int(os.environ.get("SMTP_PORT", "587"))
smtp_tls = os.environ.get("SMTP_TLS", "true").strip().lower() == "true"
smtp_user = os.environ.get("SMTP_USER", "").strip()
smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()
from_email = os.environ.get("EMAIL_FROM", smtp_user).strip()
from_name = os.environ.get("EMAIL_FROM_NAME", "Encypher Blog Bot").strip()

if not pr_url:
    print("No PR_URL set - nothing to notify.")
    sys.exit(0)

if not all([smtp_host, smtp_user, smtp_password]):
    print("SMTP credentials not configured - skipping notification.")
    sys.exit(0)

subject = "Blog post needs your review"

body = f"""The automated blog-writer ran but the reviewer flagged issues with the post.

PR: {pr_url}

Please review the post and either merge it (if it looks good) or close the PR and note what needs fixing.
"""

html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; color: #1b2f50; line-height: 1.6; padding: 40px 20px;">
  <table width="560" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
    <tr>
      <td style="background: linear-gradient(135deg, #1b2f50 0%, #2a87c4 100%);
                 padding: 24px 30px; border-radius: 8px 8px 0 0; text-align: center;">
        <span style="color: #ffffff; font-size: 18px; font-weight: 600;">Encypher Blog Bot</span>
      </td>
    </tr>
    <tr>
      <td style="background: #ffffff; padding: 32px 30px;
                 border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
        <h2 style="margin: 0 0 16px 0; font-size: 20px;">Blog post needs your review</h2>
        <p style="margin: 0 0 16px 0; color: #475569;">
          The automated reviewer flagged issues with this week's post.
          Please review and merge (or close) the draft PR below.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin: 24px 0;">
          <tr>
            <td style="background-color: #2a87c4; border-radius: 6px;">
              <a href="{pr_url}"
                 style="display: inline-block; padding: 11px 22px; color: #ffffff;
                        text-decoration: none; font-weight: 600; font-size: 14px;">
                Open draft PR
              </a>
            </td>
          </tr>
        </table>
        <p style="margin: 0; color: #94a3b8; font-size: 12px;">{pr_url}</p>
      </td>
    </tr>
  </table>
</body>
</html>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = formataddr((from_name, from_email))
msg["To"] = NOTIFY_TO
msg.attach(MIMEText(body, "plain"))
msg.attach(MIMEText(html, "html"))

try:
    if smtp_port == 465:
        server_ctx = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        with server_ctx as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            if smtp_tls:
                server.starttls()
                server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    print(f"Notification sent to {NOTIFY_TO} for {pr_url}")
except Exception as e:
    # Non-fatal: PR was already created, notification is best-effort
    print(f"WARNING: Could not send notification email: {e}")
    sys.exit(0)
