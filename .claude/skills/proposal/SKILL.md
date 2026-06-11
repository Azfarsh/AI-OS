# /proposal

## Trigger

```
/proposal "<Prospect Name>" "<Company Name>" "<prospect-email>"
```

**Example:**
```
/proposal "James Carter" "FitCoach Pro" "james@fitcoachpro.com"
```

---

## Pre-flight (Non-skippable — Read These First)

Before doing anything, read:

1. `CLAUDE.md` — agency identity, brand rules, voice
2. `context/agency-profile.md` — services, pricing, guarantee, case studies
3. `context/priorities.md` — current quarter focus (informs which services to emphasise)
4. `connections.md` — verify `google-drive` and `smtp` status before any external step

---

## Critical Rule — Notes Must Exist

**This skill cannot fabricate a proposal.** It requires real meeting notes.

Before proceeding past Step 1, check:
- Does `clients/{slug}/notes.md` exist?
- Is it non-empty (more than the template headings)?

If notes.md is missing or empty → **HALT immediately** and print:

```
⛔ Cannot generate proposal — notes.md is missing or empty.

Run this first:
  python scripts/fetch_notes.py --client "{slug}"

This fetches the meeting notes from Google Drive.
Then re-run: /proposal "{name}" "{company}" "{email}"
```

---

## Steps

### Step 1 — Parse & Resolve Client

- Slugify the prospect name: `"James Carter" → "james-carter"`
- Check if `clients/{slug}/` folder exists
- If not → create it with subfolders: `proposals/`, `notes/`
- Check `context/clients.md` for existing entry — if found as `active`, warn and confirm before continuing

### Step 2 — Fetch Notes from Google Drive

Run:
```bash
python scripts/fetch_notes.py --client "{slug}" --company "{company}"
```

This script:
- Searches Google Drive for a file named `{Company Name} - Meeting Notes` in the agency's notes folder
- Downloads and saves it to `clients/{slug}/notes.md`
- Prints the file path on success

**If script fails or `google-drive` is `not connected` in connections.md:**
- Halt and instruct user to manually place notes at `clients/{slug}/notes.md`
- Do not proceed until notes file is populated

### Step 3 — Parse Notes

Read `clients/{slug}/notes.md` and extract:
- Pain points (what the prospect said isn't working)
- Current ad spend / platforms they're on
- Budget discussed (monthly retainer + ad spend appetite)
- Goals and timeline
- Any objections or concerns
- Company niche / audience description

Store these as variables — they drive every dynamic section of the proposal.

### Step 4 — Generate Branded PPTX

Run:
```bash
python scripts/generate_proposal.py \
  --client-name "{Prospect Name}" \
  --company "{Company Name}" \
  --client-email "{prospect-email}" \
  --slug "{slug}" \
  --pain-points "{extracted from notes}" \
  --budget "{extracted from notes}" \
  --services "{inferred from notes — meta,content,google,seo}" \
  --ad-spend-range "{extracted from notes}"
```

This generates a 4-slide branded PPTX saved to:
`clients/{slug}/proposals/proposal-{YYYY-MM-DD}.pptx`

Slide contents are dynamically filled from notes. See `references/proposal-sop.md` for what goes where.

### Step 5 — Send Email

Run:
```bash
python scripts/send_email.py \
  --to "{prospect-email}" \
  --subject "Bombay Media × {Company Name} — Growth Proposal" \
  --body-file "references/assets/proposal-email-body.md" \
  --attachment "clients/{slug}/proposals/proposal-{date}.pptx" \
  --client-name "{Prospect Name}" \
  --company "{Company Name}"
```

**If `smtp` is `not connected`:** Skip email, print path to PPTX, and log that email was skipped.

### Step 6 — Register Prospect

Append to `context/clients.md`:
```
| {today's date} | {Company Name} | {slug} | {services} | {budget} | prospect |
```

### Step 7 — Log Decision

Append to `decisions/log.md`:
```
{ISO timestamp} | /proposal | Proposal sent to {Prospect Name} ({Company Name}) | Email: {prospect-email} | Services: {services} | Budget discussed: {budget} | File: clients/{slug}/proposals/proposal-{date}.pptx
```

---

## Outputs

| Artifact | Path |
|---|---|
| Branded PPTX proposal | `clients/{slug}/proposals/proposal-{YYYY-MM-DD}.pptx` |
| Meeting notes (fetched) | `clients/{slug}/notes.md` |
| Email sent | To prospect email |
| Client registry entry | `context/clients.md` (status: prospect) |
| Decision log entry | `decisions/log.md` |

---

## Connections Required

| Id | Required for |
|---|---|
| `google-drive` | Fetching notes.md from Drive |
| `smtp` | Sending proposal email |

If either is `not connected`, skill degrades gracefully:
- No Drive → user manually places notes.md
- No SMTP → PPTX is saved locally, email skipped, path printed

---

## Failure Modes

| Failure | Action |
|---|---|
| `notes.md` missing/empty | HALT. Print instructions. Do not generate. |
| `fetch_notes.py` fails | HALT. Instruct manual notes placement. |
| `generate_proposal.py` fails | HALT with error. Print exact error output. Never silently skip. |
| `send_email.py` fails | Log failure. PPTX still saved. Print path. Do not retry silently. |
| Duplicate prospect in clients.md | Warn. Ask for confirmation before adding new row. |

---

## Log Entry Format

```
{ISO timestamp} | /proposal | Generated and sent proposal | Client: {name} | Company: {company} | Email: {email} | Budget: {budget} | Services: {services} | PPTX: {path}
```
