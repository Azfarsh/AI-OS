---
name: report
description: Pull ad platform metrics and write a client performance report. Trigger on "/report" with client name and period.
---

# /report

## Trigger

```
/report "<Client Name>" --period "2024-11" [--send-email] [--demo] [--audio]
```

**CLI equivalent (full automation):**
```
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo --audio --send-email
```

## Pre-flight

- `context/clients.md` — resolve slug by client name
- `clients/{slug}/client-brief.md` — platforms and account IDs
- `references/report-template.md` — **section structure** (Executive Summary, tables, insights)
- `templates/report-template.md` — **wrapper** with `{{CLIENT_NAME}}`, `{{PERIOD}}`, `{{REPORT_BODY}}`
- `references/meta-ads-api.md`, `references/google-ads-api.md`
- `connections.md` — only call live pull scripts for connected platform ids

## Report template — where to edit

| File | What to change |
|------|----------------|
| `references/report-template.md` | Section headings, table columns, insight/recommendation format |
| `templates/report-template.md` | Header/footer wrapper, agency branding placeholders |
| `clients/{slug}/fixtures/*.json` | Dummy metrics for dry runs (copy pattern from `demo-corp`) |

Do **not** edit generated `clients/{slug}/reports/report-*.md` by hand for template changes — update the reference files above.

## Steps

1. **Resolve client** — match name in `context/clients.md`. Fail if not found or status is `archived`.

2. **Read brief** — determine active platforms (`meta`, `google`) and account/customer IDs.

3. **Pull data**
   - **Demo (`--demo` or `connections.md` status `demo-mock`):**
     `python scripts/report_pull_demo.py --client-slug {slug} --period {period}`
     Reads `clients/{slug}/fixtures/meta-{period}.json` and `google-{period}.json`.
   - **Live** — for each platform in brief **and** `connected` in `connections.md`:
     - Meta: `python scripts/meta_ads_pull.py --account-id {id} --period {period} --client-slug {slug}`
     - Google: `python scripts/google_ads_pull.py --customer-id {id} --period {period} --client-slug {slug}`
   Skip platforms not in brief or not connected (log skip).

4. **Synthesise** — `python scripts/synthesize_report.py --client-name "{name}" --client-slug {slug} --period {period}`  
   Reads `.tmp-*.json`, fills structure from `references/report-template.md`, wraps with `templates/report-template.md`.  
   Saves `clients/{slug}/reports/report-{period}.md`.

5. **Audio (optional)** — if `--audio` and `elevenlabs` connected:
   `python scripts/elevenlabs_tts.py --report-path clients/{slug}/reports/report-{period}.md --output clients/{slug}/reports/report-{period}.mp3`

6. **Clean up** — delete all `.tmp-*.json` in that reports folder.

7. **Email (optional)** — if `--send-email`:
   - Read client email from `clients/{slug}/client-brief.md` (Primary contact line).
   - Require `smtp` = `connected` in `connections.md` and SMTP vars in `.env`.
   - Run:
     ```
     python scripts/send_email.py \
       --to "{email from brief}" \
       --subject "Bombay Media × {Client Name} — Performance Report — {period}" \
       --template report \
       --client-name "{Client Name}" \
       --company "{Client Name}" \
       --period "{period}" \
       --attachment "clients/{slug}/reports/report-{period}.pptx" \
       --attachment "clients/{slug}/reports/report-{period}.md"
     ```
   - If `--audio` was used and MP3 exists, attach `report-{period}.mp3` as a third file.
   - Halt on send failure; do not mark workflow complete.

8. **Log** — append to `decisions/log.md`.

**One-shot:** Steps 3–8 are combined in `scripts/report_workflow.py`.

## Outputs

- `clients/{slug}/reports/report-{period}.md`
- `clients/{slug}/reports/report-{period}.mp3` (if `--audio`)
- Email if flag set

## Connections required

- `meta-ads` and/or `google-ads` per client (or `--demo` / `demo-mock`)
- `smtp` if `--send-email`
- `elevenlabs` if `--audio`

## Failure modes

- No platform data pulled: halt before writing report.
- Script failure: do not delete temp files until user confirms.

## Log entry

`{ISO timestamp} | /report | {Client} {period} | platforms: {list} | path: clients/{slug}/reports/report-{period}.md`
