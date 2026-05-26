# Claude Code API — researched once

**Env:** `ANTHROPIC_API_KEY`  
**Docs:** [Environment variables](https://code.claude.com/docs/en/env-vars) · [Authentication](https://code.claude.com/docs/en/authentication)

## Auth

- **`ANTHROPIC_API_KEY`** — Anthropic Console API key; sent as `X-Api-Key`. Used by Claude Code in this repo when running `/skills`.
- Subscription auth via `/login` does not require `.env`; if both are set, API key can take precedence after approval — run `/status` to confirm.

## Used by

| Context | Purpose |
|---------|---------|
| Claude Code CLI | Run Agency OS skills (`/onboard-client`, `/report`, `/proposal`, etc.) |
| Not used by | `scripts/*.py` (those use integration keys only) |

## Get a key

1. [console.anthropic.com](https://console.anthropic.com/) → API keys.
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
3. In Claude Code: `/status` → confirm API key auth.

## Adding / removing

1. Add or clear `ANTHROPIC_API_KEY` in `.env` (template in `.env.example`).
2. Full variable list: `references/env-api-keys.md`.
3. To use subscription only: remove or unset `ANTHROPIC_API_KEY` in `.env`.
