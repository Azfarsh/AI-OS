"""Shared boot briefing and branded banner for Agency OS voice surfaces."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from _common import REPO_ROOT

AGENCY_NAME = "Bombay Media"
TAGLINE = "AI-Powered Performance Marketing"


def _parse_clients() -> list[dict[str, str]]:
    path = REPO_ROOT / "context" / "clients.md"
    if not path.exists():
        return []
    clients: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Slug" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 6:
            continue
        clients.append(
            {
                "date": parts[0],
                "name": parts[1],
                "slug": parts[2],
                "services": parts[3],
                "budget": parts[4],
                "status": parts[5],
            }
        )
    return clients


def _parse_connections() -> list[dict[str, str]]:
    path = REPO_ROOT / "connections.md"
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Key" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 7:
            continue
        key_match = re.search(r"`([^`]+)`", parts[2] if len(parts) > 2 else "")
        status_match = re.search(r"`([^`]+)`", parts[5] if len(parts) > 5 else "")
        if key_match and status_match:
            rows.append(
                {
                    "service": parts[1],
                    "key": key_match.group(1),
                    "status": status_match.group(1),
                }
            )
    return rows


def get_boot_briefing() -> dict:
    clients = _parse_clients()
    connections = _parse_connections()
    active = [c for c in clients if c["status"].lower() in {"active", "prospect"}]
    connected = [c for c in connections if c["status"] == "connected"]
    now = datetime.now().strftime("%A, %d %B %Y")

    spoken = (
        f"Bombay Media Agency OS online. Today is {now}. "
        f"{len(active)} client{'s' if len(active) != 1 else ''} in registry. "
        f"{len(connected)} integration{'s' if len(connected) != 1 else ''} connected. "
        "Say report, onboard, proposal, status, or list clients."
    )

    return {
        "agency": AGENCY_NAME,
        "tagline": TAGLINE,
        "date": now,
        "client_count": len(active),
        "clients": active,
        "connected_count": len(connected),
        "connections": connections,
        "spoken": spoken,
        "command_phrases": [
            "Status check",
            "List clients",
            "Run a report for Demo Corp, period 2025-01, demo data, email it",
            "Onboard client Acme Coaching, john@acme.com, meta and content, budget 5000",
            "Create a proposal for Jane at Demo Corp, email jane@demo.com",
        ],
    }


def print_boot_banner() -> None:
    briefing = get_boot_briefing()
    line = "=" * 62
    print(line)
    print(f"  {AGENCY_NAME.upper()} AGENCY OS")
    print(f"  {TAGLINE}")
    print(line)
    print(f"  {briefing['date']}")
    print(f"  Clients: {briefing['client_count']}  |  Connected: {briefing['connected_count']}")
    print(line)
    print("  Commands: report | onboard | proposal | status | list clients")
    print(line)
