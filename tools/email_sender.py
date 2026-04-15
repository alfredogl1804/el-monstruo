"""
El Monstruo — Email Sender Tool (Gmail SMTP)
==============================================
Gives El Monstruo the ability to send emails with results.

Uses Gmail SMTP with App Password (no OAuth complexity).
The kernel can send research results, alerts, and reports.

Env vars required:
    GMAIL_ADDRESS — Gmail address (e.g., monstruo@gmail.com)
    GMAIL_APP_PASSWORD — Gmail App Password (16 chars, no spaces)

Sprint 2 — 2026-04-15
"""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Optional

import structlog

logger = structlog.get_logger("tools.email_sender")

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


async def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    cc: Optional[str] = None,
) -> dict[str, Any]:
    """
    Send an email via Gmail SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body (if provided, email is multipart)
        cc: Optional CC address
    
    Returns:
        dict with keys: sent (bool), error (str or None), recipient
    """
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_password:
        return {
            "sent": False,
            "error": "GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set. Cannot send email.",
            "recipient": to,
        }

    try:
        # Build message
        if html_body:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))
        else:
            msg = MIMEText(body, "plain", "utf-8")

        msg["From"] = f"El Monstruo <{gmail_address}>"
        msg["To"] = to
        msg["Subject"] = subject
        if cc:
            msg["Cc"] = cc

        # Send via SMTP (blocking, but fast enough for single emails)
        with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_address, gmail_password)
            recipients = [to]
            if cc:
                recipients.append(cc)
            server.sendmail(gmail_address, recipients, msg.as_string())

        logger.info("email_sent", to=to, subject=subject[:50])
        return {
            "sent": True,
            "error": None,
            "recipient": to,
        }

    except smtplib.SMTPAuthenticationError as e:
        logger.error("email_auth_failed", error=str(e))
        return {
            "sent": False,
            "error": f"Gmail authentication failed. Check GMAIL_APP_PASSWORD. Error: {e}",
            "recipient": to,
        }
    except Exception as e:
        logger.error("email_send_failed", error=str(e))
        return {
            "sent": False,
            "error": str(e),
            "recipient": to,
        }
