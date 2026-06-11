# Claude Code API — researched once

**Env:** `ANTHROPIC_API_KEY` (direct Anthropic) **or** OpenRouter trio below  
**Docs:** [Environment variables](https://code.claude.com/docs/en/env-vars) · [Authentication](https://code.claude.com/docs/en/authentication) · [OpenRouter + Claude Code](https://openrouter.ai/docs/guides/coding-agents/claude-code-integration)

## Auth — direct Anthropic

- **`ANTHROPIC_API_KEY`** — Anthropic Console API key; sent as `X-Api-Key`. Used by Claude Code in this repo when running `/skills`.
- Subscription auth via `/login` does not require `.env`; if both are set, API key can take precedence after approval — run `/status` to confirm.

## Auth — OpenRouter

Use when your key starts with `sk-or-v1-` (OpenRouter), not `sk-ant-` (Anthropic).

| Variable | Value |
|----------|--------|
| `ANTHROPIC_BASE_URL` | `https://openrouter.ai/api` |
| `ANTHROPIC_AUTH_TOKEN` | Your OpenRouter API key |
| `ANTHROPIC_API_KEY` | **Empty string** `""` — required so Claude Code does not fall back to Anthropic login |

Optional: `OPENROUTER_API_KEY` — same key, for your reference in `.env` (copy into `ANTHROPIC_AUTH_TOKEN`).

Project-level Claude Code config (gitignored): `.claude/settings.local.json` with the same `env` block. This repo ships that file when you wire OpenRouter locally.

**Verify:** In Claude Code run `/status` — base URL should be `https://openrouter.ai/api`, auth via `ANTHROPIC_AUTH_TOKEN`.

**Troubleshooting:** If you previously used Anthropic `/login`, run `/logout`, restart the terminal, and confirm shell profile does not set a non-empty `ANTHROPIC_API_KEY`.

**Custom models (optional):** Set `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL` to OpenRouter model ids (e.g. `anthropic/claude-sonnet-4`).

## Used by

| Context | Purpose |
|---------|---------|
| Claude Code CLI | Run Agency OS skills (`/onboard-client`, `/report`, `/proposal`, etc.) |
| Not used by | `scripts/*.py` (those use integration keys only) |

## Get a key

**Anthropic:** [console.anthropic.com](https://console.anthropic.com/) → API keys → `ANTHROPIC_API_KEY=sk-ant-...`

**OpenRouter:** [openrouter.ai](https://openrouter.ai) → Settings → API Keys → paste into `.env` and `.claude/settings.local.json` per above.

## Adding / removing

1. Add or clear keys in `.env` (template in `.env.example`).
2. For OpenRouter, keep `.claude/settings.local.json` in sync (or regenerate from `.env`).
3. Full variable list: `references/env-api-keys.md`.
4. To use subscription only: remove or unset API keys and run `/login` in Claude Code.
