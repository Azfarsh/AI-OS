#!/usr/bin/env python3
"""
send_email.py — Bombay Media Email Sender
Sends onboarding emails with optional attachment (contract PDF).

FREE TIER: Works with Gmail + App Password (no paid service needed).
Setup:
  1. Go to myaccount.google.com → Security → 2-Step Verification → App passwords
  2. Create an App Password for "Mail"
  3. Set SMTP_USER=your@gmail.com and SMTP_PASSWORD=the-app-password in .env

Usage:
    python scripts/send_email.py \
        --to "client@example.com" \
        --subject "Welcome to Bombay Media — Next Steps" \
        --template "onboarding" \
        --client-name "Acme Coaching" \
        --drive-url "https://drive.google.com/..." \
        --clickup-url "https://app.clickup.com/..." \
        --contract-path "clients/acme-coaching/contracts/contract-2025-06-01.pdf"
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
    print("ERROR: Run: pip install python-dotenv")
    sys.exit(1)

load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM    = os.getenv("EMAIL_FROM", "farhan@bombay-media.com")
AGENCY_NAME   = os.getenv("AGENCY_NAME", "Bombay Media")


# ── Email templates ───────────────────────────────────────────────

ONBOARDING_TEMPLATE = """
Hi {client_contact},

Welcome to {agency_name} — excited to get started on your growth.

Here's everything you need right now:

📁 Your Google Drive folder (assets, reports, contracts):
{drive_url}

✅ Your project board (track every task):
{clickup_url}

📄 Your Service Agreement is attached. Please review and sign — takes under 2 minutes.

Once signed, I'll reach out to schedule our kickoff call where we'll:
- Walk through your current ad account
- Set your 90-day ROAS targets
- Brief the creative team on your brand

Any questions before then, reply directly to this email.

— Farhan Rakhangi
Co-Founder & Director of Growth
Bombay Media
farhan@bombay-media.com
bmmediagrowth.com
Dubai · Mumbai
"""

CONTRACT_FOLLOWUP_TEMPLATE = """
Hi {client_contact},

Just following up on the service agreement I sent over — wanted to make sure it landed in your inbox.

Once that's signed we can lock in the kickoff call and get your campaigns live.

Let me know if you have any questions about the terms.

— Farhan
Bombay Media | farhan@bombay-media.com
"""


def build_email(to: str, subject: str, body: str, contract_path: str = None) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"]    = f"{AGENCY_NAME} <{EMAIL_FROM}>"
    msg["To"]      = to
    msg["Subject"] = subject
    msg["Reply-To"] = EMAIL_FROM

    msg.attach(MIMEText(body.strip(), "plain"))

    if contract_path:
        p = Path(contract_path)
        if p.exists():
            with open(p, "rb") as f:
                part = MIMEApplication(f.read(), Name=p.name)
            part["Content-Disposition"] = f'attachment; filename="{p.name}"'
            msg.attach(part)
            print(f"  ✓ Attached: {p.name}")
        else:
            print(f"  ⚠ Attachment not found: {contract_path}")

    return msg


def send(msg: MIMEMultipart, to: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("ERROR: SMTP_USER and SMTP_PASSWORD must be set in .env")
        print("  → For Gmail: use an App Password (not your normal password)")
        sys.exit(1)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, to, msg.as_string())

    print(f"✓ Email sent to {to}")
    print(f"EMAIL_SENT:{to}")


def main():
    parser = argparse.ArgumentParser(description="Bombay Media — Email Sender")
    parser.add_argument("--to",              required=True)
    parser.add_argument("--subject",         required=True)
    parser.add_argument("--template",        default="onboarding",
                        choices=["onboarding", "contract-followup", "custom"])
    parser.add_argument("--client-name",     default="")
    parser.add_argument("--client-contact",  default="there")
    parser.add_argument("--drive-url",       default="[Drive link pending]")
    parser.add_argument("--clickup-url",     default="[ClickUp link pending]")
    parser.add_argument("--contract-path",   default=None,
                        help="Path to contract PDF to attach")
    parser.add_argument("--body",            default=None,
                        help="Custom body text (only used with --template custom)")
    args = parser.parse_args()

    if args.template == "onboarding":
        body = ONBOARDING_TEMPLATE.format(
            client_contact=args.client_contact,
            agency_name=AGENCY_NAME,
            drive_url=args.drive_url,
            clickup_url=args.clickup_url,
        )
    elif args.template == "contract-followup":
        body = CONTRACT_FOLLOWUP_TEMPLATE.format(
            client_contact=args.client_contact,
        )
    elif args.template == "custom":
        body = args.body or "No body provided."
    else:
        body = ""

    msg = build_email(
        to=args.to,
        subject=args.subject,
        body=body,
        contract_path=args.contract_path,
    )
    send(msg, args.to)


if __name__ == "__main__":
    main()
