# Agency OS — Kickstart Brief for Claude Code / Cursor

> **Read this before writing a single file.** This document is your complete build contract. It tells you what exists, what to build, where everything lives, and the exact rules you must not break. Follow it strictly.

---

## 0. What This Project Is

A **CLI-only AI Operating System** for a digital marketing agency, built on top of [Nate Herk's AIS-OS starter kit](https://github.com/nateherkai/AIS-OS).

- **No frontend. No backend server. No database.**
- Everything runs via `claude code` in the terminal.
- Skills are invoked with `/skill-name` slash commands inside a Claude Code session.
- All persistent state lives in flat Markdown files inside this repo.
- External services are reached via MCP servers or lightweight Python/Bash scripts in `scripts/`.

The four skills being built (`/onboard-client`, `/report`, `/proposal`, `/audit`) are **agency workflows**, not replacements for the base AIS-OS skills (`/onboard`, `/audit`, `/level-up`). They sit alongside them in `.claude/skills/`.

---

## 1. Repo Structure (Strict — Do Not Deviate)

This is the canonical folder layout. Follow Nate's structure exactly. Add only what is listed here; do not invent new top-level folders.

```
agency-os/                                   ← Root (fork/clone of AIS-OS)
│
├── CLAUDE.md                                ← Root operating manual (filled at setup)
├── EXPANSIONS.md                            ← From AIS-OS — do not modify
├── connections.md                           ← Registry of every external tool wired in
├── aios-intake.md                           ← Agency-level intake (adapted from AIS-OS)
├── .env.example                             ← All required env vars, no secrets
├── .env                                     ← Secrets — gitignored
├── .gitignore
│
├── context/                                 ← About the agency (filled at setup)
│   ├── agency-profile.md                    ← Name, services, team, ICP
│   ├── clients.md                           ← Active client registry (append-only)
│   └── priorities.md                        ← Current quarter focus
│
├── references/                              ← Frameworks, SOPs, templates — READ-ONLY at runtime
│   ├── 3ms-framework.md                     ← From AIS-OS — do not modify
│   ├── onboarding-sop.md                    ← ★ YOU CREATE: step-by-step client onboarding rules
│   ├── report-template.md                   ← ★ YOU CREATE: section structure for performance reports
│   ├── proposal-template.md                 ← ★ YOU CREATE: proposal section structure
│   ├── clickup-api.md                       ← Researched-once API reference for ClickUp
│   ├── gdrive-api.md                        ← Researched-once API reference for Google Drive
│   ├── docuseal-api.md                      ← Researched-once API reference for DocuSeal
│   ├── meta-ads-api.md                      ← Meta Ads API reference
│   └── google-ads-api.md                    ← Google Ads API reference
│
├── templates/                               ← Parameterized document scaffolds
│   ├── contract-template.md                 ← Contract body (filled per client by /onboard-client)
│   ├── report-template.md                   ← Report doc scaffold (filled by /report)
│   └── proposal-template.md                 ← Proposal doc scaffold (filled by /proposal)
│
├── clients/                                 ← One subfolder per client (created by /onboard-client)
│   └── {client-slug}/
│       ├── client-brief.md                  ← Who they are, services, platforms, contacts
│       ├── notes.md                         ← Running notes — meeting notes, pain points, etc.
│       ├── proposals/                       ← Generated proposals
│       ├── reports/                         ← Generated reports
│       └── contracts/                       ← Contract snapshots
│
├── decisions/
│   └── log.md                               ← Append-only. Log every non-trivial decision here.
│
├── archives/                                ← Old clients, deprecated skills, old intakes. Never delete.
│
├── scripts/                                 ← Python/Bash scripts that hit APIs
│   ├── clickup_create_project.py
│   ├── gdrive_create_folder.py
│   ├── docuseal_send_contract.py
│   ├── meta_ads_pull.py
│   ├── google_ads_pull.py
│   └── send_email.py
│
└── .claude/
    └── skills/
        ├── onboard/SKILL.md                 ← From AIS-OS — keep as-is
        ├── audit/SKILL.md                   ← From AIS-OS — keep as-is
        ├── level-up/SKILL.md                ← From AIS-OS — keep as-is
        ├── onboard-client/SKILL.md          ← ★ YOU BUILD
        ├── report/SKILL.md                  ← ★ YOU BUILD
        ├── proposal/SKILL.md                ← ★ YOU BUILD
        └── agency-audit/SKILL.md            ← ★ YOU BUILD
```

---

## 2. Foundational Rules (From AIS-OS — Non-Negotiable)

These are the architecture laws from Nate's framework. Every decision you make must pass these.

1. **Boring is beautiful.** Workflows beat agents. Scripts beat MCPs when MCPs add fragility.
2. **Researched-once-saved-forever.** When you figure out how an API works, write it to `references/{tool}-api.md`. Never re-research at runtime.
3. **Context is non-skippable.** Every skill must read relevant context files before doing anything. Never assume.
4. **Cadence is last.** Do not automate what doesn't work manually first.
5. **Flat with good naming beats deep nesting.** `clients/acme-corp/reports/` is the max depth.
6. **One `CLAUDE.md` at root.** Skills can reference it; never duplicate it.
7. **`decisions/log.md` is append-only.** Log every meaningful choice with a timestamp and rationale.
8. **`archives/` is the graveyard.** Move old things here. Never delete.
9. **`.env` holds secrets.** `.env.example` holds the keys. Both are required. `.env` is gitignored.
10. **No frontend, no backend, no DB.** The terminal and flat files are the only surfaces.

---

## 3. The Four Cs — How to Evaluate Every Skill

Before marking any skill "done", score it against the Four Cs (Nate Herk's framework):

| C | Question | Pass condition |
|---|----------|----------------|
| **Context** | Does the skill read the right context before acting? | Reads `CLAUDE.md`, `context/`, and relevant `clients/{slug}/` files at start |
| **Connections** | Does the skill actually reach the external systems it needs? | MCP or script is wired and tested; `connections.md` entry exists |
| **Capabilities** | Does a short trigger phrase produce a correct multi-step artifact? | Running `/onboard-client acme john@acme.com` produces ClickUp project + Drive folder + contract email |
| **Cadence** | Could this run unattended on a schedule if needed? | Skill is stateless — all inputs are explicit; no hidden interactive state |

---

## 4. Environment Variables Required

Create `.env.example` with these keys (no values). The developer fills `.env` before first run.

```
# Claude Code (Anthropic API)
ANTHROPIC_API_KEY=

# ClickUp
CLICKUP_API_TOKEN=
CLICKUP_TEAM_ID=
CLICKUP_SPACE_ID=

# Google Drive / Gmail (Service Account or OAuth)
GOOGLE_SERVICE_ACCOUNT_JSON_PATH=
GOOGLE_DRIVE_ROOT_FOLDER_ID=

# DocuSeal
DOCUSEAL_API_TOKEN=
DOCUSEAL_TEMPLATE_ID=

# Meta Ads
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=

# Email (SMTP or SendGrid)
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=

# Agency defaults
AGENCY_NAME=
AGENCY_EMAIL=
```

---

## 5. Skill Specifications

Each skill lives at `.claude/skills/{skill-name}/SKILL.md`. This file is the sole source of truth for what the skill does and how to invoke it. Claude Code reads this file when the slash command is triggered.

### Pattern every SKILL.md must follow

```markdown
# /skill-name

## Trigger
Exact invocation syntax and accepted arguments.

## Pre-flight
What to read before doing anything (context files, client brief, reference SOPs).

## Steps
Numbered, deterministic steps. Each step names its output and which script/MCP it calls.

## Outputs
Exact list of artifacts produced and where they land in the repo.

## Connections required
Which entries in connections.md must be live for this skill to work.

## Failure modes
What to do if a step fails. Never silently continue.

## Log entry
What to append to decisions/log.md when the skill completes.
```

---

### 5.1 `/onboard-client`

**What it does:** Fully onboards a new client. Creates ClickUp project from SOP, creates Google Drive folder tree, generates and sends a contract via DocuSeal, creates the client folder in `clients/`.

**Trigger syntax:**
```
/onboard-client "<Client Name>" "<client-email>" "<Services: meta,google,seo>" "<Monthly Budget>"
```

**Pre-flight reads:**
- `CLAUDE.md`
- `context/agency-profile.md`
- `references/onboarding-sop.md`
- `references/clickup-api.md`
- `references/gdrive-api.md`
- `references/docuseal-api.md`
- `templates/contract-template.md`

**Steps (in order):**

1. **Parse inputs** — extract client name, email, services, budget. Slugify the client name (`acme-corp`). Fail loudly if any required input is missing.

2. **Check for duplicate** — scan `context/clients.md` for existing entry. If found, halt and ask for confirmation before proceeding.

3. **Create client folder in repo** — create `clients/{slug}/` with subfolders `proposals/`, `reports/`, `contracts/`. Write `client-brief.md` with parsed inputs and timestamp. Write empty `notes.md`.

4. **Create ClickUp project** — run `scripts/clickup_create_project.py --client "{name}" --services "{services}"`. The script reads `references/onboarding-sop.md` and creates tasks/lists matching the SOP checklist. Log the returned ClickUp project URL.

5. **Create Google Drive folder** — run `scripts/gdrive_create_folder.py --client "{slug}"`. Creates root folder `/{AGENCY_NAME}/Clients/{Client Name}/` with subfolders: `Reports/`, `Assets/`, `Contracts/`, `Creative/`. Log the returned Drive folder URL.

6. **Generate contract** — fill `templates/contract-template.md` with client name, services, budget, date. Save to `clients/{slug}/contracts/contract-{date}.md`. Run `scripts/docuseal_send_contract.py --client-email "{email}" --contract-path "clients/{slug}/contracts/contract-{date}.md"`.

7. **Send onboarding email** — run `scripts/send_email.py` with the Drive folder link, ClickUp project link, and a note that contract has been sent for signature.

8. **Register client** — append a row to `context/clients.md`:
   ```
   | {date} | {Client Name} | {slug} | {services} | {budget} | active |
   ```

9. **Log decision** — append to `decisions/log.md`:
   ```
   {ISO timestamp} | /onboard-client | Onboarded {Client Name} | ClickUp: {url} | Drive: {url} | Contract sent to {email}
   ```

**Outputs:**
- `clients/{slug}/client-brief.md`
- `clients/{slug}/contracts/contract-{date}.md`
- ClickUp project (external)
- Google Drive folder tree (external)
- Contract sent via DocuSeal (external)
- Onboarding email sent

**Connections required:** `clickup`, `google-drive`, `docuseal`, `smtp`

---

### 5.2 `/report`

**What it does:** Pulls performance data for a named client from their active ad platforms (Meta, Google Ads, Instagram Ads via Meta API), synthesises it into a formatted report following `references/report-template.md`, saves the report to `clients/{slug}/reports/`, and optionally emails it.

**Trigger syntax:**
```
/report "<Client Name>" --period "2024-11" [--send-email]
```

**Pre-flight reads:**
- `clients/{slug}/client-brief.md` (to know which platforms this client uses)
- `references/report-template.md`
- `references/meta-ads-api.md`
- `references/google-ads-api.md`

**Steps (in order):**

1. **Resolve client** — look up `{slug}` from `context/clients.md` by matching client name. Fail if not found.

2. **Read client brief** — parse `clients/{slug}/client-brief.md` to get the list of active platforms and account IDs.

3. **Pull platform data** — for each active platform:
   - Meta Ads + Instagram: run `scripts/meta_ads_pull.py --account-id {id} --period {period}`
   - Google Ads: run `scripts/google_ads_pull.py --customer-id {id} --period {period}`
   - Each script outputs a structured JSON file to `clients/{slug}/reports/.tmp-{platform}-{period}.json`

4. **Synthesise report** — read all `.tmp-*.json` files. Read `references/report-template.md`. Fill the template: executive summary, per-platform metrics (spend, impressions, clicks, CTR, CPC, conversions, ROAS), insights, recommendations. Save to `clients/{slug}/reports/report-{period}.md`.

5. **Clean up temp files** — delete all `.tmp-*` JSON files.

6. **Send email (conditional)** — if `--send-email` flag was passed, run `scripts/send_email.py` attaching the report to the client's email address from `client-brief.md`.

7. **Log** — append to `decisions/log.md`.

**Outputs:**
- `clients/{slug}/reports/report-{period}.md`
- Email sent (conditional)

**Connections required:** `meta-ads`, `google-ads`, `smtp` (conditional)

---

### 5.3 `/proposal`

**What it does:** Generates a tailored agency proposal for a prospective client using notes captured after the first meeting. Fetches enrichment data (company info, ad spend estimates, industry benchmarks) from the web, fills `templates/proposal-template.md`, saves to `clients/{slug}/proposals/`, and emails it to the prospect.

**Trigger syntax:**
```
/proposal "<Prospect Name>" "<Company Name>" "<prospect-email>"
```

**Pre-flight reads:**
- `context/agency-profile.md` (agency credentials, services, case studies)
- `clients/{slug}/notes.md` (pain points, budget discussed, meeting notes — **this file must exist and be filled before running**)
- `references/proposal-template.md`
- `templates/proposal-template.md`

**Important rule:** If `clients/{slug}/notes.md` is empty or missing, the skill must halt and instruct the user to fill it first. The proposal cannot be fabricated without real meeting notes.

**Steps (in order):**

1. **Resolve or create client folder** — if `clients/{slug}/` does not exist, create it with empty `notes.md` and halt with instructions to fill notes before re-running.

2. **Read notes** — parse `clients/{slug}/notes.md` for: pain points, stated budget, current marketing situation, goals, timeline, any objections noted.

3. **Enrich context** — use Claude Code's web search or a `scripts/enrich_company.py` script to gather: company size, industry, known ad spend (if public), competitive landscape. Append findings to a temp context block (not saved to disk).

4. **Fill proposal template** — read `templates/proposal-template.md`. Populate:
   - Executive summary tailored to their stated pain points
   - Proposed service scope matching their budget and goals
   - Case studies from `context/agency-profile.md` that are most relevant
   - Pricing (derived from budget discussion in notes)
   - Timeline
   - Next steps / CTA

5. **Save proposal** — write to `clients/{slug}/proposals/proposal-{date}.md`.

6. **Send email** — run `scripts/send_email.py` with proposal as attachment to `{prospect-email}`. Subject: `[{Agency Name}] — Proposal for {Company Name}`.

7. **Register prospect in clients.md** — append row with status `prospect`.

8. **Log** — append to `decisions/log.md`.

**Outputs:**
- `clients/{slug}/proposals/proposal-{date}.md`
- Email sent to prospect

**Connections required:** `smtp`

---

### 5.4 `/agency-audit`

**What it does:** Evaluates how well the agency OS is performing across Nate Herk's Four Cs — Context, Capabilities, Cadence, Connections. Reads the live state of the repo and produces a scored gap report saved to `decisions/log.md` and printed to terminal.

**Trigger syntax:**
```
/agency-audit
```

**Pre-flight reads:** Everything. This skill is read-only and must scan:
- `CLAUDE.md`
- `context/` (all files)
- `connections.md`
- `.claude/skills/` (all SKILL.md files)
- `clients/` (count active clients, check for stale reports)
- `decisions/log.md` (recency of last audit)
- `references/` (check which API guides exist vs which connections are claimed)

**Scoring rubric (0–3 per C, 12 total):**

**Context (0–3)**
- 0: `CLAUDE.md` is template/unfilled
- 1: Agency profile exists but clients.md is sparse
- 2: All context files filled, clients registered
- 3: Clients have filled `notes.md` and `client-brief.md`; context is fresh (updated < 30 days)

**Connections (0–3)**
- 0: No entries in `connections.md` beyond template rows
- 1: 1–2 connections wired (have scripts + API reference files)
- 2: 3–4 connections wired
- 3: All required connections for active skills are wired and have `references/{tool}-api.md`

**Capabilities (0–3)**
- 0: Agency skills exist but no client has been onboarded via `/onboard-client`
- 1: `/onboard-client` has been run at least once (evidence: clients/ has a folder)
- 2: At least 2 of the 4 agency skills have been run for real clients
- 3: All 4 skills have been run; reports exist for at least one client

**Cadence (0–3)**
- 0: No decisions logged, no audit history
- 1: Decisions logged, but no recurring report cadence established
- 2: Reports generated for at least 1 period; audit has been run before
- 3: Reports exist for 2+ consecutive periods per active client; audit run in last 7 days

**Output format:**

```
╔══════════════════════════════════════════════╗
║     AGENCY OS — FOUR Cs AUDIT REPORT        ║
║     {ISO date}                               ║
╚══════════════════════════════════════════════╝

Context      [██░░] 2/3  — clients.md has 3 clients but notes.md missing for 2
Connections  [█░░░] 1/3  — ClickUp wired; Google Drive, DocuSeal not yet connected
Capabilities [██░░] 2/3  — /onboard-client run; /report run once; /proposal not yet run
Cadence      [█░░░] 1/3  — 1 report generated; no recurring schedule; first audit

TOTAL: 6/12

TOP 3 GAPS TO CLOSE THIS WEEK:
1. Wire Google Drive (connections: gdrive) — blocks /onboard-client fully working
2. Fill notes.md for Acme Corp and TechStart before next /proposal run
3. Run /report for all active clients to establish cadence baseline

Previous audit: never
Next suggested audit: {date + 7 days}
```

**Saves:** Appends audit summary to `decisions/log.md`.

**Connections required:** None (read-only, no external calls).

---

## 6. Scripts — What Each Must Do

All scripts live in `scripts/`. Each script must:
- Accept all inputs as CLI arguments (no interactive prompts)
- Load credentials from `.env` (use `python-dotenv`)
- Print a single-line success or error result to stdout
- Exit with code 0 on success, 1 on failure
- Never write to any file outside `clients/` or designated temp paths

| Script | Language | Key library | Notes |
|--------|----------|-------------|-------|
| `clickup_create_project.py` | Python | `requests` | Reads onboarding-sop.md, creates list + tasks via ClickUp REST API |
| `gdrive_create_folder.py` | Python | `google-api-python-client` | Creates folder tree under root Drive folder |
| `docuseal_send_contract.py` | Python | `requests` | POSTs to DocuSeal `/submissions` endpoint with recipient email + template ID |
| `meta_ads_pull.py` | Python | `facebook-business` SDK | Pulls campaign/adset/ad level metrics for date range |
| `google_ads_pull.py` | Python | `google-ads` SDK | Pulls campaign metrics via GAQL query |
| `send_email.py` | Python | `smtplib` or `sendgrid` | Sends email with optional markdown attachment |
| `enrich_company.py` | Python | `requests` + web search | Scrapes public info about a company (LinkedIn, Crunchbase, website) |

---

## 7. Reference Files You Must Create

These files must exist before any skill will work. Create them as structured Markdown.

### `references/onboarding-sop.md`

Document the agency's standard onboarding process. Structure:

```markdown
# Client Onboarding SOP

## Phase 1 — Internal Setup (Day 1)
- [ ] Create ClickUp project
- [ ] Create Google Drive folder structure
- [ ] Add client to CRM / clients.md
- [ ] Assign account manager

## Phase 2 — Contract & Legal (Day 1–3)
- [ ] Send contract via DocuSeal
- [ ] Follow up if not signed within 48h
- [ ] File signed contract in Drive > Contracts/

## Phase 3 — Kickoff (Day 3–7)
- [ ] Schedule kickoff call
- [ ] Gather brand assets (logos, colors, fonts)
- [ ] Audit existing ad accounts
- [ ] Set up reporting access

## Phase 4 — Launch Prep (Day 7–14)
- [ ] Build ad account structure
- [ ] Create initial creatives
- [ ] Get client approval
- [ ] Launch
```

The `/onboard-client` skill reads this file and creates corresponding ClickUp tasks.

### `references/report-template.md`

Defines the report structure the `/report` skill must follow:

```markdown
# Performance Report — {Client Name} — {Period}

## Executive Summary
(2–3 sentences: overall performance vs goal, biggest win, biggest concern)

## Platform Breakdown

### Meta Ads
| Metric | This Period | Last Period | Change |
...

### Google Ads
...

## Key Insights
(3–5 bullets: data-driven observations)

## Recommendations
(3–5 bullets: what to change next period)

## Next Steps
```

### `references/proposal-template.md`

Defines the proposal structure the `/proposal` skill must follow:

```markdown
# Proposal — {Agency Name} × {Company Name}

## About Us
## Understanding Your Challenge
## Proposed Solution
## Why It Works (Case Studies)
## Scope of Work
## Investment
## Timeline
## What Happens Next
```

---

## 8. `connections.md` — Required Rows

When each connection is wired, update this file. The `/agency-audit` skill reads it to score Connections.

| # | Domain | Tool | Mechanism | Auth | Last checked |
|---|--------|------|-----------|------|--------------|
| 1 | Project management | ClickUp | script | `CLICKUP_API_TOKEN` in .env | — |
| 2 | File storage | Google Drive | script | `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` in .env | — |
| 3 | Contract signing | DocuSeal | script | `DOCUSEAL_API_TOKEN` in .env | — |
| 4 | Paid social | Meta Ads | script | `META_ACCESS_TOKEN` in .env | — |
| 5 | Search ads | Google Ads | script | `GOOGLE_ADS_REFRESH_TOKEN` in .env | — |
| 6 | Communication | SMTP / SendGrid | script | `SMTP_*` in .env | — |

---

## 9. Build Order (Follow This Exactly)

The Four Cs dependency graph says: **Context → Connections + Capabilities (parallel) → Cadence**. Build in this order:

```
Phase 1 — Foundation (Context)
  1. Fork / clone AIS-OS repo
  2. Fill CLAUDE.md with agency identity
  3. Create context/agency-profile.md, context/clients.md, context/priorities.md
  4. Create .env.example and .gitignore
  5. Create references/onboarding-sop.md, report-template.md, proposal-template.md
  6. Create templates/ scaffolds

Phase 2 — Connections
  7. Write scripts/clickup_create_project.py + references/clickup-api.md
  8. Write scripts/gdrive_create_folder.py + references/gdrive-api.md
  9. Write scripts/docuseal_send_contract.py + references/docuseal-api.md
  10. Write scripts/meta_ads_pull.py + references/meta-ads-api.md
  11. Write scripts/google_ads_pull.py + references/google-ads-api.md
  12. Write scripts/send_email.py
  13. Update connections.md with all 6 rows

Phase 3 — Capabilities (Skills)
  14. Write .claude/skills/onboard-client/SKILL.md
  15. Write .claude/skills/report/SKILL.md
  16. Write .claude/skills/proposal/SKILL.md
  17. Write .claude/skills/agency-audit/SKILL.md

Phase 4 — Validate
  18. Run /onboard-client with a test client
  19. Run /agency-audit — score should be ≥ 8/12
  20. Run /report for test client
  21. Run /proposal for a test prospect
```

Do not start Phase 3 until at least Phases 1–2 pass a manual sanity check.

---

## 10. Critical Do-Nots

- **Do not** create a web server, REST API, or any `app.py` / `server.js`
- **Do not** create a database (SQLite, Postgres, anything)
- **Do not** create a frontend (React, HTML, anything)
- **Do not** store client data anywhere except `clients/{slug}/` in this repo
- **Do not** hardcode credentials — they go in `.env` only
- **Do not** make scripts interactive — all inputs come as CLI args
- **Do not** add `notes/`, `misc/`, `tmp/`, or `inbox/` folders (per AIS-OS anti-patterns)
- **Do not** modify the three AIS-OS base skills (`/onboard`, `/audit`, `/level-up`)
- **Do not** deviate from the folder structure in Section 1
- **Do not** skip writing a `references/{tool}-api.md` when adding a new script

---

## 11. Checklist — Definition of Done

A build is complete when every item below is checked:

- [ ] `CLAUDE.md` filled with real agency identity (not template placeholders)
- [ ] `context/agency-profile.md` written
- [ ] `context/clients.md` exists (even if empty)
- [ ] `.env.example` has all required keys
- [ ] `.env` is in `.gitignore`
- [ ] All 6 `references/{tool}-api.md` files exist
- [ ] All 3 `references/{workflow}-template.md` files exist
- [ ] All 3 `templates/` scaffolds exist
- [ ] All 6 scripts exist, accept CLI args, load from `.env`
- [ ] `connections.md` has all 6 rows filled
- [ ] All 4 agency skill `SKILL.md` files written
- [ ] `/agency-audit` runs without error and scores ≥ 8/12
- [ ] `/onboard-client` has been run once end-to-end with a test client
- [ ] `decisions/log.md` has at least one real entry

---

*Built on top of [AIS-OS](https://github.com/nateherkai/AIS-OS) by Nate Herk. The Four Cs of an AIOS™ and The Three Ms of AI™ are trademarks of Nate Herk © 2026.*
