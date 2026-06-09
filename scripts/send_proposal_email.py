#!/usr/bin/env python3
"""
send_email.py — Bombay Media Email Sender
Sends a proposal email with PPTX attachment via Gmail SMTP (free tier).

Setup:
  - Use a Gmail account
  - Enable 2FA → generate an App Password at myaccount.google.com/apppasswords
  - Set SMTP_USER and SMTP_PASSWORD in .env

Usage:
    python scripts/send_email.py \
        --to "james@fitcoachpro.com" \
        --subject "Bombay Media × FitCoach Pro — Growth Proposal" \
        --client-name "James Carter" \
        --company "FitCoach Pro" \
        --attachment "clients/james-carter/proposals/proposal-2025-06-09.pptx"
"""

import argparse
import os
import smtplib
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
load_dotenv(REPO_ROOT / ".env")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASSWORD", "")
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Farhan Rakhangi — Bombay Media")


def build_email_body(client_name: str, company: str) -> str:
    """Plain-text email body in Bombay Media brand voice (Proof-First, Founder-Direct)."""
    first_name = client_name.split()[0]
    return f"""Hi {first_name},

Really enjoyed our conversation — it's clear {company} has the right product and audience. The gap is in the system, and that's exactly where we come in.

Attached is the growth proposal we put together for you. It covers:

→  What we'd run (Meta Ads, creatives, full funnel)
→  Real numbers from a recent client — $179,850 revenue from $7,017 ad spend in 90 days
→  Exactly how the investment breaks down
→  Your 3 next steps to get started

We guarantee 3× ROAS in 90 days. If we don't hit it, we work for free until we do. No asterisks.

To see where your funnel is leaking today, grab the free Funnel Leaks report:
→  bmmediagrowth.com

And when you're ready to talk through the plan:
→  calendly.com/bombay_media/complimentary-business-success-call

Happy to answer any questions before you book.

Farhan Rakhangi
Co-Founder, Bombay Media FZE
farhan@bombay-media.com
bmmediagrowth.com | Dubai · Mumbai
"""


def main():
    parser = argparse.ArgumentParser(description="Send proposal email via Gmail SMTP")
    parser.add_argument("--to",           required=True,  help="Recipient email")
    parser.add_argument("--subject",      required=True,  help="Email subject")
    parser.add_argument("--client-name",  required=True,  help="Prospect full name")
    parser.add_argument("--company",      required=True,  help="Company name")
    parser.add_argument("--attachment",   required=True,  help="Path to PPTX file")
    args = parser.parse_args()

    # ── Validate credentials ──────────────────────────────────────
    if not SMTP_USER or not SMTP_PASS:
        print("ERROR: SMTP_USER or SMTP_PASSWORD not set in .env")
        print("  → For Gmail: generate an App Password at myaccount.google.com/apppasswords")
        sys.exit(1)

    # ── Validate attachment ───────────────────────────────────────
    attach_path = Path(args.attachment)
    if not attach_path.exists():
        print(f"ERROR: Attachment not found: {attach_path}")
        sys.exit(1)

    # ── Build message ─────────────────────────────────────────────
    msg = MIMEMultipart()
    msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"]      = args.to
    msg["Subject"] = args.subject
    msg["Reply-To"] = SMTP_USER

    body = build_email_body(args.client_name, args.company)
    msg.attach(MIMEText(body, "plain"))

    with open(attach_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=attach_path.name)
        part["Content-Disposition"] = f'attachment; filename="{attach_path.name}"'
        msg.attach(part)

    # ── Send ──────────────────────────────────────────────────────
    try:
        print(f"📧 Connecting to {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, args.to, msg.as_string())
        print(f"✓ Email sent to {args.to}")
        print(f"EMAIL_SENT:{args.to}")
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Gmail authentication failed.")
        print("  → Make sure SMTP_PASSWORD is an App Password, not your regular Gmail password.")
        print("  → Generate one at: myaccount.google.com/apppasswords")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
