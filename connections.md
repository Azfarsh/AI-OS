# Connections

Registry of every external system Agency OS can reach. **Stable id** in the Id column is what skills use in "Connections required". Mechanism `not connected` means skills skip or halt that step per `references/connections-guide.md`.

| # | Id | Domain | Tool | Mechanism | Auth | Last checked |
|---|-----|--------|------|-----------|------|--------------|
| 1 | clickup | Project management | ClickUp | not connected | `CLICKUP_API_TOKEN`, `CLICKUP_TEAM_ID`, `CLICKUP_SPACE_ID` | — |
| 2 | google-drive | File storage | Google Drive | not connected | `GOOGLE_SERVICE_ACCOUNT_JSON_PATH`, `GOOGLE_DRIVE_ROOT_FOLDER_ID` | — |
| 3 | docuseal | Contract signing | DocuSeal | not connected | `DOCUSEAL_API_TOKEN`, `DOCUSEAL_TEMPLATE_ID` | — |
| 4 | meta-ads | Paid social | Meta Ads | not connected | `META_ACCESS_TOKEN`, `META_APP_ID`, `META_APP_SECRET` | — |
| 5 | google-ads | Search ads | Google Ads | not connected | `GOOGLE_ADS_*` in `.env` | — |
| 6 | smtp | Communication | SMTP | not connected | `SMTP_*`, `EMAIL_FROM` | — |

**Mechanism values:** `script` (Python in `scripts/`), `mcp`, `export`, `not connected`.

When wiring a tool: set Mechanism to `script`, fill Last checked (YYYY-MM-DD), ensure `references/{tool}-api.md` exists, copy `.env.example` keys into `.env`. Full key guide: `references/env-api-keys.md`. Claude Code: `ANTHROPIC_API_KEY` — see `references/claude-code-api.md`.

**Remove a service:** set Mechanism to `not connected` only — do not delete API reference files; move to `archives/references/` if deprecated.

See `references/connections-guide.md` for add/remove checklist.
