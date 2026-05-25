---
name: onboard-client
description: Fully onboard a new agency client — ClickUp, Drive, contract, repo folder, registry. Trigger on "/onboard-client" with client name, email, services, budget.
---

# /onboard-client

## Trigger

```
/onboard-client "<Client Name>" "<client-email>" "<Services: meta,google,seo>" "<Monthly Budget>"
```

## Pre-flight

Read before any action:

- `CLAUDE.md`
- `context/agency-profile.md`
- `context/clients.md`
- `references/onboarding-sop.md`
- `references/connections-guide.md`
- `connections.md` — verify required ids are `script` (not `not connected`): `clickup`, `google-drive`, `docuseal`, `smtp`
- `references/clickup-api.md`, `references/gdrive-api.md`, `references/docuseal-api.md`
- `templates/contract-template.md`

If a required connection is not wired, **halt** and list which ids to wire (do not silently skip required steps).

## Steps

1. **Parse inputs** — client name, email, services (comma list), budget. Slugify name (`acme-corp`). Fail if any required field missing.

2. **Check duplicate** — scan `context/clients.md` for slug or name. If found, ask for explicit confirmation before continuing.

3. **Create client folder** — `clients/{slug}/` with `proposals/`, `reports/`, `contracts/`. Write `client-brief.md` (inputs, services, email, timestamp). Write empty `notes.md`.

4. **ClickUp** — `python scripts/clickup_create_project.py --client "{name}" --services "{services}"`. Capture `CLICKUP_PROJECT_URL` from stdout.

5. **Google Drive** — `python scripts/gdrive_create_folder.py --client "{slug}" --display-name "{name}"`. Capture `GDRIVE_FOLDER_URL`.

6. **Contract** — fill `templates/contract-template.md` → save `clients/{slug}/contracts/contract-{date}.md`. Run `python scripts/docuseal_send_contract.py --client-email "{email}" --contract-path "clients/{slug}/contracts/contract-{date}.md"`.

7. **Onboarding email** — `python scripts/send_email.py --to "{email}" --subject "Welcome to {AGENCY_NAME}" --body` including Drive + ClickUp links and contract note.

8. **Register** — append row to `context/clients.md`: `| {date} | {name} | {slug} | {services} | {budget} | active |`

9. **Log** — append to `decisions/log.md`:
   `{ISO timestamp} | /onboard-client | Onboarded {name} | ClickUp: {url} | Drive: {url} | Contract sent to {email}`

## Outputs

- `clients/{slug}/client-brief.md`
- `clients/{slug}/contracts/contract-{date}.md`
- External: ClickUp project, Drive tree, DocuSeal submission, email

## Connections required

`clickup`, `google-drive`, `docuseal`, `smtp` (see `connections.md` ids)

## Failure modes

- Script exit code ≠ 0: stop, show stderr, do not register client or log success.
- Partial external success: note what completed in `decisions/log.md` and tell user how to retry one step.

## Log entry

See step 9.
