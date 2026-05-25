---
name: proposal
description: Generate and email a tailored proposal from meeting notes. Trigger on "/proposal" with prospect name, company, email.
---

# /proposal

## Trigger

```
/proposal "<Prospect Name>" "<Company Name>" "<prospect-email>"
```

## Pre-flight

- `context/agency-profile.md`
- `clients/{slug}/notes.md` — **must exist and be non-empty**
- `references/proposal-template.md`
- `templates/proposal-template.md`
- `connections.md` — `smtp` must be connected for send step

## Steps

1. **Resolve slug** — slugify prospect/company name. If `clients/{slug}/` missing, create folder + empty `notes.md` and **halt**: instruct user to fill notes and re-run.

2. **Read notes** — parse pain points, budget, goals, timeline, objections. If empty, **halt** (no fabricated proposals).

3. **Enrich (optional)** — `python scripts/enrich_company.py --company "{Company}" --website "{url if known}"` for public context. Do not save enrichment to disk.

4. **Fill proposal** — use `templates/proposal-template.md` + case studies from `context/agency-profile.md`. Save `clients/{slug}/proposals/proposal-{date}.md`.

5. **Send email** — `python scripts/send_email.py --to "{email}" --subject "[{AGENCY_NAME}] — Proposal for {Company}" --attachment "clients/{slug}/proposals/proposal-{date}.md"`

6. **Register** — append to `context/clients.md` with status `prospect` if not already listed.

7. **Log** — append to `decisions/log.md`.

## Outputs

- `clients/{slug}/proposals/proposal-{date}.md`
- Email to prospect

## Connections required

`smtp`

## Failure modes

- Empty notes: halt with checklist of what to capture in `notes.md`.
- SMTP not connected: save proposal locally, halt before send.

## Log entry

`{ISO timestamp} | /proposal | {Company} | sent to {email} | path: clients/{slug}/proposals/proposal-{date}.md`
