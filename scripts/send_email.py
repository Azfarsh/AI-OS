#!/usr/bin/env python3
"""Send email via SMTP with optional attachment path."""

import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from _common import REPO_ROOT, fail, ok, require_env


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--attachment", default=None)
    args = parser.parse_args()

    env = require_env("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "EMAIL_FROM")
    msg = MIMEMultipart()
    msg["From"] = env["EMAIL_FROM"]
    msg["To"] = args.to
    msg["Subject"] = args.subject
    msg.attach(MIMEText(args.body, "plain"))

    if args.attachment:
        path = Path(args.attachment)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if not path.exists():
            fail(f"Attachment not found: {path}")
        msg.attach(MIMEText(path.read_text(encoding="utf-8"), "plain", "utf-8"))

    with smtplib.SMTP(env["SMTP_HOST"], int(env["SMTP_PORT"])) as server:
        server.starttls()
        server.login(env["SMTP_USER"], env["SMTP_PASSWORD"])
        server.sendmail(env["EMAIL_FROM"], [args.to], msg.as_string())

    ok(f"EMAIL_SENT_TO={args.to}")


if __name__ == "__main__":
    main()
