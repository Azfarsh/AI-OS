#!/usr/bin/env python3
"""
send_email.py — Bombay Media Email Sender
Onboarding (template + optional contract PDF) and proposal (PPTX attachment) emails.

Usage — onboarding:
    python scripts/send_email.py \\
        --to "client@example.com" \\
        --subject "Welcome to Bombay Media — Your Next Steps" \\
        --template onboarding \\
        --client-contact "John" \\
        --drive-url "https://drive.google.com/..." \\
        --clickup-url "https://app.clickup.com/..." \\
        --contract-path "clients/acme/contracts/contract-2025-06-01.pptx"

Usage — proposal:
    python scripts/send_email.py \\
        --to "prospect@example.com" \\
        --subject "Bombay Media × Acme — Growth Proposal" \\
        --client-name "Jane Doe" \\
        --company "Acme" \\
        --attachment "clients/jane-doe/proposals/proposal-2025-06-12.pptx"
"""

from __future__ import annotations

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

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", os.getenv("AGENCY_NAME", "Bombay Media"))
AGENCY_NAME = os.getenv("AGENCY_NAME", "Bombay Media")

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

PROPOSAL_TEMPLATE = """Hi {first_name},

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


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def build_proposal_body(client_name: str, company: str, body_file: str | None) -> str:
    if body_file:
        path = Path(body_file)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.exists():
            return path.read_text(encoding="utf-8").format(
                client_name=client_name,
                company=company,
                first_name=client_name.split()[0],
            )
    first_name = client_name.split()[0] if client_name else "there"
    return PROPOSAL_TEMPLATE.format(first_name=first_name, company=company)


def attach_file(msg: MIMEMultipart, file_path: str, label: str) -> None:
    path = Path(file_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        print(f"  ⚠ Attachment not found: {path}")
        return
    with open(path, "rb") as f:
        part = MIMEApplication(f.read(), Name=path.name)
    part["Content-Disposition"] = f'attachment; filename="{path.name}"'
    msg.attach(part)
    print(f"  ✓ Attached: {path.name} ({label})")


def send(msg: MIMEMultipart, to: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        fail("SMTP_USER and SMTP_PASSWORD must be set in .env (use a Gmail App Password)")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        fail(
            "Gmail authentication failed. Use an App Password (not your regular password) "
            "and quote SMTP_PASSWORD in .env if it contains spaces."
        )
    except Exception as exc:
        fail(f"Failed to send email: {exc}")

    print(f"✓ Email sent to {to}")
    print(f"EMAIL_SENT:{to}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bombay Media — Email Sender")
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument(
        "--template",
        default=None,
        choices=["onboarding", "contract-followup", "custom"],
        help="Onboarding template (omit for proposal mode)",
    )
    parser.add_argument("--client-name", default="")
    parser.add_argument("--client-contact", default="there")
    parser.add_argument("--company", default="")
    parser.add_argument("--drive-url", default="[Drive link pending]")
    parser.add_argument("--clickup-url", default="[ClickUp link pending]")
    parser.add_argument("--contract-path", default=None)
    parser.add_argument("--attachment", default=None, help="Proposal PPTX attachment")
    parser.add_argument("--body-file", default=None, help="Optional proposal body markdown")
    parser.add_argument("--body", default=None, help="Custom body (--template custom)")
    args = parser.parse_args()

    msg = MIMEMultipart()
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg["Reply-To"] = EMAIL_FROM

    if args.template == "onboarding":
        body = ONBOARDING_TEMPLATE.format(
            client_contact=args.client_contact,
            agency_name=AGENCY_NAME,
            drive_url=args.drive_url,
            clickup_url=args.clickup_url,
        )
    elif args.template == "custom":
        body = args.body or "No body provided."
    elif args.attachment or args.client_name:
        if not args.client_name or not args.company:
            fail("Proposal mode requires --client-name and --company")
        body = build_proposal_body(args.client_name, args.company, args.body_file)
    else:
        fail("Specify --template onboarding or proposal args (--client-name, --company, --attachment)")

    msg.attach(MIMEText(body.strip(), "plain"))

    if args.contract_path:
        attach_file(msg, args.contract_path, "contract")
    if args.attachment:
        attach_file(msg, args.attachment, "proposal")

    send(msg, args.to)


if __name__ == "__main__":
    main()
