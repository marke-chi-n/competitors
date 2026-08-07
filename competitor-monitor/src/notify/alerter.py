"""
Alert generation. Email sending is disabled until explicitly configured.
Interface is decoupled — set env vars to activate.

Required env vars (when ready to activate):
  ALERT_EMAIL_ENABLED=true
  ALERT_EMAIL_RECIPIENT=you@company.com
  ALERT_SMTP_HOST=smtp.example.com
  ALERT_SMTP_PORT=587
  ALERT_SMTP_USER=user@example.com
  ALERT_SMTP_PASSWORD=secret
"""
import json
import logging
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


def build_email_body(changes: list) -> str:
    """Build plain-text email body from list of change dicts."""
    lines = []
    for c in changes:
        lines.append(f"Concorrente: {c.get('competitor', '')}")
        lines.append(f"Tipo da mudança: {c.get('change_type', '')}")
        lines.append(f"Severidade: {c.get('severity', '')}")
        lines.append("")
        lines.append(f"O que mudou:\n{c.get('curator_summary', '')}")
        lines.append("")
        lines.append(f"Impacto na ficha:\n{c.get('field', 'Ver dado')}")
        lines.append("")
        lines.append(f"Por que merece revisão:\n{c.get('reason', '')}")
        lines.append("")
        lines.append(f"Fonte: {c.get('evidence', [{}])[0].get('url', '')}")
        lines.append(f"Confidence: {c.get('confidence', 0)}")
        lines.append("─" * 60)
    return "\n".join(lines)


def send_alert(changes: list) -> bool:
    """
    Send consolidated alert email.
    Returns True if sent, False if disabled or failed.
    """
    enabled = os.environ.get("ALERT_EMAIL_ENABLED", "false").lower() == "true"
    if not enabled:
        logger.info("Email alerts disabled. Set ALERT_EMAIL_ENABLED=true to activate.")
        _save_pending_alert(changes)
        return False

    high_or_medium = [c for c in changes
                      if c.get("severity") in ("HIGH", "MEDIUM")]
    if not high_or_medium:
        return False

    recipient = os.environ.get("ALERT_EMAIL_RECIPIENT", "")
    smtp_host = os.environ.get("ALERT_SMTP_HOST", "")
    smtp_port = int(os.environ.get("ALERT_SMTP_PORT", "587"))
    smtp_user = os.environ.get("ALERT_SMTP_USER", "")
    smtp_pass = os.environ.get("ALERT_SMTP_PASSWORD", "")

    if not all([recipient, smtp_host, smtp_user, smtp_pass]):
        logger.warning("Email config incomplete. Required: ALERT_SMTP_HOST, ALERT_SMTP_USER, "
                       "ALERT_SMTP_PASSWORD, ALERT_EMAIL_RECIPIENT")
        _save_pending_alert(high_or_medium)
        return False

    today = date.today().isoformat()
    subject = (f"[Monitoramento de Concorrentes] {len(high_or_medium)} "
               f"alterações encontradas — {today}")
    body = build_email_body(high_or_medium)

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient, msg.as_string())
        logger.info(f"Alert sent to {recipient}: {len(high_or_medium)} changes")
        return True
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
        _save_pending_alert(high_or_medium)
        return False


def _save_pending_alert(changes: list):
    """Save alert to file when email is not configured."""
    REPORTS_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    path = REPORTS_DIR / f"pending-alert-{today}.json"
    path.write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Alert saved to {path}")
