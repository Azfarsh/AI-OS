# Testing Agency OS in Cursor (no Claude Code)

Claude Code slash commands (`/report`, etc.) are **skill files** here. In Cursor, you run the same workflows by pasting the prompts below into **Agent chat** (this window). The agent reads `.claude/skills/*/SKILL.md` and follows them.

**Rules for every dry run**

- Do **not** call external APIs or run `scripts/*.py` that need `.env` secrets.
- Do **not** send email.
- Write outputs only under `clients/` and append to `decisions/log.md` when the skill says to log.
- Say `DRY RUN` in your message so the agent skips connection-dependent steps.

---

## 0. One-time setup (2 minutes)

```powershell
cd "C:\Users\Azfar\OneDrive\Desktop\AI OS"
python scripts/validate_repo.py
```

Expect: `OK — Agency OS structure valid`.

Optional: create venv later when you wire APIs:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 1. Structural check (you run; no agent)

| Command | What it proves |
|---------|----------------|
| `python scripts/validate_repo.py` | All skills, references, templates, demo data exist |

---

## 2. Agency audit — **fully local**

**Paste into Cursor Agent:**

```
DRY RUN — Execute .claude/skills/agency-audit/SKILL.md exactly.

- Read-only: do not modify files except append one line to decisions/log.md at the end.
- Print the full Four Cs box report in chat (Context, Connections, Capabilities, Cadence, total /12, top 3 gaps).
- connections.md shows everything not connected — score Connections honestly.
```

**Pass:** You see a scored report in chat + new line in `decisions/log.md`.

---

## 3. Personal audit (`/audit`) — **fully local**

**Paste:**

```
DRY RUN — Execute .claude/skills/audit/SKILL.md for this Agency OS repo.

Read-only except you may append a short audit summary to decisions/log.md.
Score the Four Cs (25 each). No API calls.
```

---

## 4. Onboard (`/onboard`) — **local, interactive**

**Paste:**

```
DRY RUN — Execute .claude/skills/onboard/SKILL.md.

Use aios-intake.md: if placeholders remain, ask me ONE question at a time (max 7).
When done (or if I say "use demo answers"), fill context/agency-profile.md, context/priorities.md, and update CLAUDE.md knowledge sections with demo agency:
- Name: Demo Agency
- Services: Meta, Google Ads, SEO
- ICP: B2B SaaS UK
Do not call any scripts.
```

**Pass:** `context/` and `CLAUDE.md` have real text, not `{{placeholders}}`.

---

## 5. Onboard client — **repo half (dry run)**

**Paste:**

```
DRY RUN — Execute .claude/skills/onboard-client/SKILL.md for:
Client: "Dry Run Ltd"
Email: dryrun@example.com
Services: meta,google
Budget: $5000/mo

SKIP steps 4–7 (ClickUp, Drive, DocuSeal, email) — connections not wired.
DO steps 1–3, 8–9: folders, client-brief.md, contract markdown from templates/contract-template.md, register in context/clients.md, log to decisions/log.md.
```

**Pass:** `clients/dry-run-ltd/` exists with brief + contract file; registry row added.

---

## 6. Report — **synthesis with dummy metrics**

**Prep (once):** Fixture JSON is in `clients/demo-corp/fixtures/`.

**CLI (full demo with email):**

```powershell
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo --send-email
```

Requires `.env` with `SMTP_USER` + `SMTP_PASSWORD` (Gmail App Password) and `smtp` = `connected` in `connections.md`.  
Demo Corp brief sends to **hannanchougle28@gmail.com**.

**Paste into Cursor Agent (dry run — no email):**

```
DRY RUN — Execute .claude/skills/report/SKILL.md:
/report "Demo Corp" --period "2025-01" --demo

- Resolve slug from context/clients.md
- Read clients/demo-corp/client-brief.md
- Run: python scripts/report_pull_demo.py --client-slug demo-corp --period 2025-01
- Run: python scripts/synthesize_report.py --client-name "Demo Corp" --client-slug demo-corp --period 2025-01
- Or use one-shot: python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo
- No --send-email
- Append decisions/log.md
```

**Pass:** `clients/demo-corp/reports/report-2025-01.md` exists with tables and insights.

---

## 7. Proposal — **full doc, no email**

**Paste:**

```
DRY RUN — Execute .claude/skills/proposal/SKILL.md:
/proposal "Jane Doe" "Demo Corp" "jane@demo-corp.example"

- Read clients/demo-corp/notes.md (must be non-empty)
- Read context/agency-profile.md
- Write clients/demo-corp/proposals/proposal-{today's date}.md from templates/proposal-template.md
- SKIP send_email.py
- Update context/clients.md if Demo Corp not listed (status: prospect)
- Append decisions/log.md
```

**Pass:** New file under `clients/demo-corp/proposals/`.

---

## 8. Level-up — **conversation only**

**Paste:**

```
DRY RUN — Execute .claude/skills/level-up/SKILL.md.

Run a shortened 3Ms interview (Mindset → Method → Machine). Propose ONE small automation for this Agency OS repo. Do not build scripts unless I say go. Append the scoped idea to decisions/log.md.
```

---

## 9. Script smoke test (optional, still no paid APIs)

`enrich_company.py` only needs a URL (may fail offline):

```powershell
python scripts/enrich_company.py --company "Demo Corp" --website "https://example.com"
```

Other scripts will **exit 1** without `.env` — that is expected until you wire connections.

---

## 11. Voice agent — **ElevenLabs (optional)**

Requires `.env` with `ELEVENLABS_API_KEY` and `ELEVENLABS_AGENT_ID`. See **`VOICE_SETUP.md`**.

```powershell
python scripts/setup_elevenlabs_agent.py   # once
python scripts/voice_agent.py            # speak to run workflows
```

Say: *"Run a demo report for Demo Corp, period 2025-01."*

---

## 10. Checklist — all dry runs done

| # | Workflow | Cursor prompt section | Artifact to verify |
|---|----------|----------------------|-------------------|
| 1 | Structure | §1 | `validate_repo.py` → OK |
| 2 | `/agency-audit` | §2 | Chat report + `decisions/log.md` |
| 3 | `/audit` | §3 | Chat report |
| 4 | `/onboard` | §4 | `context/agency-profile.md` filled |
| 5 | `/onboard-client` | §5 | `clients/dry-run-ltd/` |
| 6 | `/report` | §6 | `clients/demo-corp/reports/report-2025-01.md` |
| 7 | `/proposal` | §7 | `clients/demo-corp/proposals/proposal-*.md` |
| 8 | `/level-up` | §8 | `decisions/log.md` entry |

---

## Tips for Cursor

- **@-mention files** in chat for focus: `@.claude/skills/report/SKILL.md`, `@clients/demo-corp/notes.md`
- **Same chat thread** for a workflow so the agent keeps skill context.
- **New chat** per workflow if the thread gets long.
- When you get API keys later, remove `DRY RUN` and set `Mechanism` to `script` in `connections.md` for that row.

---

## What still needs Claude Code?

Nothing for day-to-day use if you stay in Cursor Agent. Claude Code only adds convenient `/slash` aliases to the same `SKILL.md` files. This repo is the source of truth either way.
