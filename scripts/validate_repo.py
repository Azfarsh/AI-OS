#!/usr/bin/env python3
"""Structural validation for Agency OS — no API calls."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "CLAUDE.md",
    "AGENCY_OS_KICKSTART.md",
    "connections.md",
    ".env.example",
    "context/agency-profile.md",
    "context/clients.md",
    "context/priorities.md",
    "decisions/log.md",
    "references/3ms-framework.md",
    "references/onboarding-sop.md",
    "references/report-template.md",
    "references/proposal-template.md",
    "references/connections-guide.md",
    "references/clickup-api.md",
    "references/gdrive-api.md",
    "references/docuseal-api.md",
    "references/meta-ads-api.md",
    "references/google-ads-api.md",
    "templates/contract-template.md",
    "templates/report-template.md",
    "templates/proposal-template.md",
    ".claude/skills/onboard/SKILL.md",
    ".claude/skills/audit/SKILL.md",
    ".claude/skills/level-up/SKILL.md",
    ".claude/skills/onboard-client/SKILL.md",
    ".claude/skills/report/SKILL.md",
    ".claude/skills/proposal/SKILL.md",
    ".claude/skills/agency-audit/SKILL.md",
]

REQUIRED_SCRIPTS = [
    "scripts/_common.py",
    "scripts/clickup_create_project.py",
    "scripts/gdrive_create_folder.py",
    "scripts/docuseal_send_contract.py",
    "scripts/meta_ads_pull.py",
    "scripts/google_ads_pull.py",
    "scripts/send_email.py",
    "scripts/enrich_company.py",
    "scripts/validate_repo.py",
]

DEMO_PATHS = [
    "clients/demo-corp/client-brief.md",
    "clients/demo-corp/notes.md",
    "clients/demo-corp/fixtures/meta-2025-01.json",
    "clients/demo-corp/fixtures/google-2025-01.json",
]


def main() -> None:
    missing: list[str] = []
    for rel in REQUIRED_PATHS + REQUIRED_SCRIPTS + DEMO_PATHS:
        if not (ROOT / rel).exists():
            missing.append(rel)

    if missing:
        print("FAIL — missing paths:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    print("OK — Agency OS structure valid (no API checks).")
    print(f"  Skills: 7 | Scripts: 8 | Demo client: clients/demo-corp/")
    sys.exit(0)


if __name__ == "__main__":
    main()
