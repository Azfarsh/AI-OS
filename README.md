# Agency OS

CLI-only AI Operating System for a digital marketing agency. Built on [AIS-OS](https://github.com/nateherkai/AIS-OS).

- **No frontend, no backend server, no database**
- Skills run in [Claude Code](https://docs.anthropic.com/en/docs/claude-code) via `/skill-name`
- Persistent state: Markdown in this repo
- Integrations: Python scripts in `scripts/` + `connections.md` registry

## Quick start

1. Open this folder in **Cursor** (or Claude Code).
2. Copy `.env.example` → `.env` when you wire APIs (not needed for dry runs). Key reference: `references/env-api-keys.md`.
3. `python scripts/validate_repo.py` — confirm structure.
4. Follow **`TESTING_IN_CURSOR.md`** — copy-paste prompts to run every workflow without Claude Code.
5. Read **`AGENCY_OS_KICKSTART.md`** — full build contract.

## Skills

| Skill | Purpose |
|-------|---------|
| `/onboard` | Personal/agency intake (AIS-OS) |
| `/audit` | Personal Four-Cs audit |
| `/level-up` | Weekly automation |
| `/onboard-client` | New client onboarding |
| `/report` | Monthly performance report |
| `/proposal` | Proposal from meeting notes |
| `/agency-audit` | Agency Four-Cs scoreboard |

## Structure

```
context/          agency + client registry
clients/{slug}/   per-client artifacts
references/       SOPs, templates, API guides
templates/        fillable scaffolds
scripts/          API CLIs (one integration per file)
connections.md    wired services (add/remove safely)
.claude/skills/   skill definitions
```

## Add or remove a service

Follow `references/connections-guide.md`. Never delete API docs — mark `not connected` in `connections.md`.

## License

MIT — see `LICENSE`. Four Cs™ and Three Ms™ are trademarks of Nate Herk © 2026.
