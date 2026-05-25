"""Shared helpers for Agency OS scripts. Import only what you need per script."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env")


def require_env(*keys: str) -> dict[str, str]:
    load_env()
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        fail(f"Missing required env: {', '.join(missing)}")
    return {k: os.environ[k] for k in keys}


def ok(message: str) -> None:
    print(message)
    sys.exit(0)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def slugify(name: str) -> str:
    import re

    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")
