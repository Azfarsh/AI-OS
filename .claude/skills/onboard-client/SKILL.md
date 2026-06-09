# /onboard-client

## Trigger

```
/onboard-client "<Client Name>" "<client-email>" "<services>" "<monthly-budget>"
```

**Arguments:**
| Arg | Example | Required |
|---|---|---|
| Client Name | `"Acme Coaching"` | ✅ |
| Client Email | `"john@acme.com"` | ✅ |
| Services | `"meta,content"` or `"meta,google,content"` | ✅ |
| Monthly Budget | `"5000"` (USD, number only) | ✅ |

**Services accepted:** `meta` · `google` · `content` · `seo`

**Full example:**
```
/onboard-client "Acme Coaching" "john@acme.com" "meta,content" "5000"
```

---

## Pre-flight (Non-Skippable)

Before doing anything else, read these files in order:

1. `CLAUDE.md` — operating rules
2. `context/agency-profile.md` — agency identity, pricing, brand
3. `context/clients.md` — check for duplicate client
4. `references/onboarding-sop.md` — task structure for ClickUp
5. `connections.md` — verify which services are live before calling them

---

## Steps

### Step 1 — Parse & Validate Inputs

Extract from the trigger arguments:
- `CLIENT_NAME` → e.g. `Acme Coaching`
- `CLIENT_EMAIL` → e.g. `john@acme.com`
- `SERVICES` → e.g. `meta,content`
- `MONTHLY_BUDGET` → e.g. `5000`
- `CLIENT_SLUG` → slugify client name: lowercase, spaces → hyphens (e.g. `acme-coaching`)
- `DATE` → today in `YYYY-MM-DD` format
- `DATE_DISPLAY` → today in `DD Month YYYY` format (e.g. `01 June 2025`)
- `AGREEMENT_NUMBER` → format `BM-{YEAR}-{3-digit-sequence}` — check `context/clients.md` to get the next sequence number

**Fail loudly if:**
- Any required argument is missing or empty
- Email does not contain `@`
- Services contains an unrecognised value

---

### Step 2 — Duplicate Check

Scan `context/clients.md` for any row containing `CLIENT_SLUG`.

**If found:** STOP. Print:
```
⚠ Client already exists: {CLIENT_NAME} (slug: {CLIENT_SLUG})
  → Check clients/{CLIENT_SLUG}/ for existing files.
  → If re-onboarding, archive the old folder first: mv clients/{CLIENT_SLUG} archives/{CLIENT_SLUG}-{DATE}
  → Then re-run /onboard-client.
```

---

### Step 3 — Create Repo Folder Structure

Create the following files and folders:

```
clients/{CLIENT_SLUG}/
├── client-brief.md          ← fill with template below
├── notes.md                 ← empty, with header only
├── proposals/               ← empty folder
├── reports/                 ← empty folder
└── contracts/               ← empty folder (script will populate)
```

**`client-brief.md` template:**
```markdown
# Client Brief — {CLIENT_NAME}

## Identity
- **Company:** {CLIENT_NAME}
- **Slug:** {CLIENT_SLUG}
- **Primary Email:** {CLIENT_EMAIL}
- **Services:** {SERVICES}
- **Monthly Budget:** ${MONTHLY_BUDGET}
- **Onboarded:** {DATE}
- **Agreement No:** {AGREEMENT_NUMBER}
- **Status:** active

## Contacts
- **Primary Contact:** [Fill after kickoff call]
- **Title:** [Fill after kickoff call]
- **Phone:** [Fill after kickoff call]
- **City / Country:** [Fill after kickoff call]
- **Website:** [Fill after kickoff call]

## Ad Accounts
- **Meta Ad Account ID:** [Fill after access granted]
- **Google Ads Customer ID:** [Fill if applicable]

## Campaign Notes
[Fill after kickoff call]

## Reporting
- **Report Period:** Monthly
- **Report Day:** First Monday of each month
- **ROAS Target:** 3× (90-day guarantee)
```

**`notes.md` template:**
```markdown
# Notes — {CLIENT_NAME}

## Meeting Notes
[Add notes after each call — date, attendees, key points, action items]

## Pain Points
[Fill after discovery call]

## Goals
[Fill after discovery call]

## Budget Discussion
[Fill after discovery call]
```

---

### Step 4 — Generate Branded Contract (PPTX → PDF)

Check `connections.md` — confirm `contract-generator` is listed as active.

Run:
```bash
python scripts/generate_contract.py \
  --client-name "{CLIENT_NAME}" \
  --client-email "{CLIENT_EMAIL}" \
  --client-city "[Ask or leave blank]" \
  --client-country "[Ask or leave blank]" \
  --client-contact "[Ask or leave blank]" \
  --client-title "Founder" \
  --services "{SERVICES}" \
  --monthly-retainer "{MONTHLY_RETAINER}" \
  --ad-spend-min "3000" \
  --ad-spend-max "{MONTHLY_BUDGET}" \
  --agreement-number "{AGREEMENT_NUMBER}"
```

**If script exits with code 1:** STOP. Do not proceed to email step. Print the error.

Capture the output line starting with `CONTRACT_PATH:` — store as `CONTRACT_FILE`.

> **Note on monthly retainer:** Use `context/agency-profile.md` standard pricing unless the budget input implies a custom retainer. Budget < $5,000 → $2,500/month retainer. Budget $5,000–$10,000 → $3,000/month. Budget > $10,000 → $4,000/month.

---

### Step 5 — Create ClickUp Project

Check `connections.md` — if `clickup` status is `not connected`, skip this step and note it.

If connected, run:
```bash
python scripts/clickup_create_project.py \
  --client "{CLIENT_NAME}" \
  --services "{SERVICES}"
```

Capture the output line starting with `CLICKUP_URL:` — store as `CLICKUP_PROJECT_URL`.

**If script fails:** Note the failure, continue to next step (do not halt onboarding).

---

### Step 6 — Create Google Drive Folders

Check `connections.md` — if `google-drive` status is `not connected`, skip this step and note it.

If connected, run:
```bash
python scripts/gdrive_create_folder.py --client "{CLIENT_SLUG}"
```

Capture the output line starting with `DRIVE_URL:` — store as `DRIVE_FOLDER_URL`.

**If script fails:** Note the failure, continue to next step.

---

### Step 7 — Send Onboarding Email

Check `connections.md` — if `smtp` status is `not connected`, skip and note it.

If connected, run:
```bash
python scripts/send_email.py \
  --to "{CLIENT_EMAIL}" \
  --subject "Welcome to Bombay Media — Your Next Steps" \
  --template "onboarding" \
  --client-contact "[Contact name from brief, or 'there' if unknown]" \
  --drive-url "{DRIVE_FOLDER_URL}" \
  --clickup-url "{CLICKUP_PROJECT_URL}" \
  --contract-path "{CONTRACT_FILE}"
```

Capture the output line starting with `EMAIL_SENT:`.

---

### Step 8 — Register Client in Registry

Append a new row to `context/clients.md`:

```
| {DATE} | {CLIENT_NAME} | {CLIENT_SLUG} | {SERVICES} | ${MONTHLY_BUDGET} | active |
```

---

### Step 9 — Log Decision

Append to `decisions/log.md`:

```
## {ISO_TIMESTAMP} | /onboard-client | {CLIENT_NAME}

- Agreement No: {AGREEMENT_NUMBER}
- Client Email: {CLIENT_EMAIL}
- Services: {SERVICES}
- Monthly Budget: ${MONTHLY_BUDGET}
- Contract: {CONTRACT_FILE}
- ClickUp: {CLICKUP_PROJECT_URL or "skipped — not connected"}
- Drive: {DRIVE_FOLDER_URL or "skipped — not connected"}
- Email: {sent to CLIENT_EMAIL or "skipped — not connected"}
- Completed: {ISO_TIMESTAMP}
```

---

## Outputs

| Output | Location |
|---|---|
| Client brief | `clients/{slug}/client-brief.md` |
| Notes file | `clients/{slug}/notes.md` |
| Contract PPTX | `clients/{slug}/contracts/contract-{date}.pptx` |
| Contract PDF | `clients/{slug}/contracts/contract-{date}.pdf` |
| ClickUp project | External (URL logged) |
| Google Drive folder | External (URL logged) |
| Onboarding email | Sent to client |
| Client registry entry | `context/clients.md` |
| Decision log entry | `decisions/log.md` |

---

## Connections Required

| Service | Connection key | Required? |
|---|---|---|
| Contract generator | `contract-generator` | ✅ Always |
| ClickUp | `clickup` | ⚠ Skip if not connected |
| Google Drive | `google-drive` | ⚠ Skip if not connected |
| SMTP Email | `smtp` | ⚠ Skip if not connected |

---

## Failure Modes

| Failure | Action |
|---|---|
| Missing required argument | STOP immediately. Print which arg is missing. |
| Duplicate client found | STOP. Print instructions to archive or confirm. |
| `generate_contract.py` exits 1 | STOP. Print error. Do not email a broken contract. |
| Template PPTX missing | STOP. Print: "Copy Bombay_Media_Dummy_Contract.pptx to references/assets/Bombay_Media_Contract_Template.pptx" |
| ClickUp script fails | Note failure, continue. Log: "ClickUp: FAILED — {error}" |
| Drive script fails | Note failure, continue. Log: "Drive: FAILED — {error}" |
| Email script fails | Note failure, print error. Log: "Email: FAILED — {error}" |

**Never silently continue past a contract generation failure.**

---

## Terminal Summary (Print at End)

After completing all steps, print:

```
╔══════════════════════════════════════════════════════╗
║   BOMBAY MEDIA — CLIENT ONBOARDING COMPLETE         ║
╚══════════════════════════════════════════════════════╝

Client:       {CLIENT_NAME}
Agreement:    {AGREEMENT_NUMBER}
Services:     {SERVICES}
Budget:       ${MONTHLY_BUDGET}/month

✓ Repo folder:   clients/{CLIENT_SLUG}/
✓ Contract:      {CONTRACT_FILE}
✓ ClickUp:       {CLICKUP_PROJECT_URL or "skipped"}
✓ Drive:         {DRIVE_FOLDER_URL or "skipped"}
✓ Email:         {sent to CLIENT_EMAIL or "skipped"}
✓ Registry:      context/clients.md updated
✓ Log:           decisions/log.md updated

NEXT STEPS FOR FARHAN:
1. Fill in client city/country/contact in clients/{CLIENT_SLUG}/client-brief.md
2. Follow up on contract signature within 48h
3. Schedule kickoff call
```
