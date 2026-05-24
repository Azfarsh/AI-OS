"""Check memory/leads/ for existing email or company."""

from __future__ import annotations

import re
from pathlib import Path

from ais_os.config import get_config


def leads_dir() -> Path:
    return get_config().workspace / "memory" / "leads"


def is_duplicate(email: str, company: str) -> tuple[bool, str | None]:
    directory = leads_dir()
    if not directory.is_dir():
        return False, None
    email_l = email.strip().lower()
    company_l = company.strip().lower()
    for path in directory.glob("*.md"):
        text = path.read_text(encoding="utf-8").lower()
        if email_l and email_l in text:
            return True, path.name
        if company_l and company_l in text:
            return True, path.name
    return False, None
