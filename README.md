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
5. For **voice control**, see **`VOICE_SETUP.md`** — ElevenLabs talks you through workflows.
6. Read **`AGENCY_OS_KICKSTART.md`** — full build contract.

## Run workflows (manual CLI)

No microphone required. Run from the repo root:

### Report (demo data)

```powershell
python scripts/report_workflow.py --client-name "Xenvo" --period 2025-01 --demo
python scripts/report_workflow.py --client-name "Xenvo" --period 2025-01 --demo --audio
```

Output: `clients/xenvo/reports/report-2025-01.md` (+ optional `.mp3`).

### Onboard client

```powershell
python scripts/generate_contract.py `
  --client-name "Xenvo" `
  --client-email "azfarshaikh7860@gmail.com" `
  --client-city "Dubai" `
  --client-country "UAE" `
  --client-contact "Xenvo" `
  --services "meta,content" `
  --monthly-retainer "5000"
```

Output: `clients/xenvo/contracts/contract-YYYY-MM-DD.pptx`

### Proposal

```powershell
python scripts/generate_proposal.py `
  --client-name "Xenvo" `
  --company "Xenvo" `
  --client-email "azfarshaikh7860@gmail.com" `
  --slug "xenvo" `
  --budget "5000" `
  --services "meta,content"
```

Output: `clients/xenvo/proposals/proposal-YYYY-MM-DD.pptx`

## Run workflows (voice agent)

One-time setup: `VOICE_SETUP.md` (API key, agent ID, `pip install -r requirements.txt`).

### Live voice session (microphone)

```powershell
python scripts/setup_elevenlabs_agent.py
python scripts/voice_agent.py
```

Say things like:

- *"Run a demo report for Xenvo for January 2025."*
- *"Onboard client Xenvo, email azfarshaikh7860@gmail.com, services meta and content, budget five thousand."*
- *"Generate a proposal for Xenvo, company Xenvo, email azfarshaikh7860@gmail.com."*

Press `Ctrl+C` to end the session.

### Test without microphone (same tools the voice agent uses)

```powershell
# All three workflows for Xenvo
python scripts/voice_agent.py --test-xenvo

# Individual tools
python scripts/voice_agent.py --test-tool run_report --test-params "{\"client_name\":\"Xenvo\",\"period\":\"2025-01\",\"demo\":true}"
python scripts/voice_agent.py --test-report
python scripts/voice_agent.py --text-only
```

`--test-xenvo` runs report, onboard, and proposal with the voice-agent tool layer (JSON string results, same path as live voice).

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
| `/voice` | Voice-controlled workflows (ElevenLabs) |

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
