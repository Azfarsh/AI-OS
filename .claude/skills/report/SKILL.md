---
name: report
description: Pull ad platform metrics and write a client performance report. Trigger on "/report" with client name and period.
---

# /report

## Trigger

```
/report "<Client Name>" --period "2024-11" [--send-email]
```

## Pre-flight

- `context/clients.md` — resolve slug by client name
- `clients/{slug}/client-brief.md` — platforms and account IDs
- `references/report-template.md`
- `references/meta-ads-api.md`, `references/google-ads-api.md`
- `connections.md` — only call scripts for connected platform ids

## Steps

1. **Resolve client** — match name in `context/clients.md`. Fail if not found or status is `archived`.

2. **Read brief** — determine active platforms (`meta`, `google`) and account/customer IDs.

3. **Pull data** — for each platform in brief **and** connected in `connections.md`:
   - Meta: `python scripts/meta_ads_pull.py --account-id {id} --period {period} --client-slug {slug}`
   - Google: `python scripts/google_ads_pull.py --customer-id {id} --period {period} --client-slug {slug}`
   Skip platforms not in brief or not connected (log skip).

4. **Synthesise** — read `.tmp-*.json` in `clients/{slug}/reports/`. Fill structure from `references/report-template.md`. Save `clients/{slug}/reports/report-{period}.md`.

5. **Clean up** — delete all `.tmp-*.json` in that reports folder.

6. **Email (optional)** — if `--send-email`, `python scripts/send_email.py` to email from brief with report path attached.

7. **Log** — append to `decisions/log.md`.

## Outputs

- `clients/{slug}/reports/report-{period}.md`
- Email if flag set

## Connections required

`meta-ads` and/or `google-ads` per client; `smtp` if `--send-email`

## Failure modes

- No platform data pulled: halt before writing report.
- Script failure: do not delete temp files until user confirms.

## Log entry

`{ISO timestamp} | /report | {Client} {period} | platforms: {list} | path: clients/{slug}/reports/report-{period}.md`
