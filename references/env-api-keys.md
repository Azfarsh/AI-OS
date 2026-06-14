# Environment variables & API keys

Agency OS stores secrets in a local **`.env`** file (gitignored). The template is **`.env.example`** — copy it once, then fill in values as you wire each service.

```bash
cp .env.example .env
```

**Rules**

- Never commit `.env`, service-account JSON, or real tokens.
- Check `connections.md` before running skills that call external APIs.
- Python scripts load `.env` via `scripts/_common.py` (`python-dotenv`).
- **Claude Code** reads project `.env` and `.claude/settings.local.json` for LLM auth when you run skills in the CLI.

---

## Quick reference

| Variable | Service | Used by |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude / Anthropic API (direct) | Claude Code CLI (`/skills`) |
| `OPENROUTER_API_KEY` | OpenRouter | Same — copy to `ANTHROPIC_AUTH_TOKEN` |
| `ANTHROPIC_BASE_URL` | OpenRouter endpoint | `https://openrouter.ai/api` when using OpenRouter |
| `ANTHROPIC_AUTH_TOKEN` | OpenRouter bearer | Claude Code when `ANTHROPIC_BASE_URL` is set |
| `CLICKUP_API_TOKEN` | ClickUp | `scripts/clickup_create_project.py`, `/onboard-client` |
| `CLICKUP_TEAM_ID` | ClickUp | Same |
| `CLICKUP_SPACE_ID` | ClickUp | Same |
| `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` | Google Drive | `scripts/gdrive_create_folder.py` |
| `GOOGLE_DRIVE_ROOT_FOLDER_ID` | Google Drive | Same |
| `DOCUSEAL_API_TOKEN` | DocuSeal | `scripts/docuseal_send_contract.py` |
| `DOCUSEAL_TEMPLATE_ID` | DocuSeal | Same |
| `META_APP_ID` | Meta Ads | `scripts/meta_ads_pull.py`, `/report` |
| `META_APP_SECRET` | Meta Ads | Same |
| `META_ACCESS_TOKEN` | Meta Ads | Same |
| `META_AD_ACCOUNT_ID` | Meta Ads | Default account id (skills / client brief) |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads | `scripts/google_ads_pull.py` |
| `GOOGLE_ADS_CLIENT_ID` | Google Ads | Same (+ `scripts/.google-ads.yaml`) |
| `GOOGLE_ADS_CLIENT_SECRET` | Google Ads | Same |
| `GOOGLE_ADS_REFRESH_TOKEN` | Google Ads | Same |
| `GOOGLE_ADS_CUSTOMER_ID` | Google Ads | Default customer id (optional; CLI can override) |
| `SMTP_HOST` | Email | `scripts/send_email.py` |
| `SMTP_PORT` | Email | Same |
| `SMTP_USER` | Email | Same |
| `SMTP_PASSWORD` | Email | Same |
| `EMAIL_FROM` | Email | Same |
| `AGENCY_NAME` | Agency defaults | Drive paths, email subjects, templates |
| `AGENCY_EMAIL` | Agency defaults | Reply-to / sender context in skills |

Per-integration API notes: `references/{tool}-api.md`.

---

## Claude Code (LLM auth)

Pick **one** mode. Detail: `references/claude-code-api.md`.

### OpenRouter (key starts with `sk-or-v1-`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_BASE_URL` | Yes | `https://openrouter.ai/api` |
| `ANTHROPIC_AUTH_TOKEN` | Yes | Your OpenRouter API key |
| `ANTHROPIC_API_KEY` | Yes (empty) | Must be `""` — not unset — so Claude Code does not use Anthropic login |
| `OPENROUTER_API_KEY` | Optional | Same key, for documentation in `.env` |

Also add the same three vars to **`.claude/settings.local.json`** (gitignored) under `"env"`.

**Get a key:** [openrouter.ai](https://openrouter.ai) → Settings → API Keys.

**Verify:** `/status` in Claude Code — base URL `https://openrouter.ai/api`, token via `ANTHROPIC_AUTH_TOKEN`.

### Direct Anthropic (key starts with `sk-ant-`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | For API billing | Anthropic Console key; sent as `X-Api-Key`. |

**When to set it**

- Pay-as-you-go Anthropic API instead of (or in addition to) Claude Pro/Team subscription.
- You run Agency OS skills inside **Claude Code** with a direct Anthropic key.

**When to leave it empty**

- You only use **Cursor** for dry runs (`TESTING_IN_CURSOR.md`) and do not run Claude Code here.
- You prefer `/login` subscription auth — unset keys so API billing does not override subscription.

**Get a key:** [console.anthropic.com](https://console.anthropic.com/) → API keys.

**Verify:** `/status` in Claude Code.

See [Claude Code env vars](https://code.claude.com/docs/en/env-vars).

---

## ClickUp

| Variable | Purpose |
|----------|---------|
| `CLICKUP_API_TOKEN` | Personal API token (`Authorization` header) |
| `CLICKUP_TEAM_ID` | Workspace / team id |
| `CLICKUP_SPACE_ID` | Space where client folders are created |

**Get values:** ClickUp → Settings → Apps → API Token. Team/space ids from the URL or API.

**Script:** `scripts/clickup_create_project.py`  
**Detail:** `references/clickup-api.md`

---

## Google Drive / Gmail (service account)

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` | Path to downloaded service-account JSON (keep outside git; see `.gitignore`) |
| `GOOGLE_DRIVE_ROOT_FOLDER_ID` | Drive folder id for agency root (`Clients/` tree is created under it) |

**Script:** `scripts/gdrive_create_folder.py` (also requires `AGENCY_NAME`)  
**Detail:** `references/gdrive-api.md`

---

## DocuSeal

| Variable | Purpose |
|----------|---------|
| `DOCUSEAL_API_TOKEN` | API bearer token |
| `DOCUSEAL_TEMPLATE_ID` | Template id for client contracts |

**Script:** `scripts/docuseal_send_contract.py`  
**Detail:** `references/docuseal-api.md`

---

## Meta Ads

| Variable | Purpose |
|----------|---------|
| `META_APP_ID` | Meta app id |
| `META_APP_SECRET` | App secret |
| `META_ACCESS_TOKEN` | Long-lived user/system token with `ads_read` |
| `META_AD_ACCOUNT_ID` | Default ad account (`act_…` without prefix); per-client overrides live in client brief |

**Script:** `scripts/meta_ads_pull.py` (pass `--account-id` or use client-specific id)  
**Detail:** `references/meta-ads-api.md`

---

## Google Ads

| Variable | Purpose |
|----------|---------|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads API developer token |
| `GOOGLE_ADS_CLIENT_ID` | OAuth client id |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_ADS_REFRESH_TOKEN` | OAuth refresh token for the authorized Google account |
| `GOOGLE_ADS_CUSTOMER_ID` | Default Ads customer id (optional; script uses `--customer-id`) |

After filling these, generate `scripts/.google-ads.yaml` per `references/google-ads-api.md`.

**Script:** `scripts/google_ads_pull.py`  
**Detail:** `references/google-ads-api.md`

---

## Email (SMTP)

| Variable | Purpose |
|----------|---------|
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_PORT` | Port (e.g. `587` for TLS) |
| `SMTP_USER` | Login username |
| `SMTP_PASSWORD` | Login password or app password |
| `EMAIL_FROM` | From address on outbound mail |

**Script:** `scripts/send_email.py` — used by `/onboard-client`, `/proposal`, `/report` (when sending).

---

## Agency defaults

| Variable | Purpose |
|----------|---------|
| `AGENCY_NAME` | Display name in Drive paths, contracts, reports, email subjects |
| `AGENCY_EMAIL` | Primary agency contact email for templates and client comms |
| `ELEVENLABS_API_KEY` | ElevenLabs | `scripts/voice_agent.py`, `scripts/elevenlabs_tts.py` |
| `ELEVENLABS_VOICE_ID` | ElevenLabs | TTS voice selection |
| `ELEVENLABS_AGENT_ID` | ElevenLabs | Conversational AI agent (from `setup_elevenlabs_agent.py`) |

Not secret — but kept in `.env` so scripts and skills share one source of truth with integrations.

---

## ElevenLabs

| Variable | Purpose |
|----------|---------|
| `ELEVENLABS_API_KEY` | API key from elevenlabs.io |
| `ELEVENLABS_VOICE_ID` | Voice for TTS (default: George) |
| `ELEVENLABS_AGENT_ID` | ConvAI agent id from setup script |

**Scripts:** `scripts/voice_agent.py`, `scripts/elevenlabs_tts.py`, `scripts/setup_elevenlabs_agent.py`  
**Detail:** `references/elevenlabs-api.md`, **`VOICE_SETUP.md`**

---

## Wiring checklist

1. Copy `.env.example` → `.env`.
2. Fill keys for one service.
3. Update `connections.md` (set Mechanism to `script`, set **Last checked**).
4. Run the matching `scripts/*` command or skill step.
5. Log the outcome in `decisions/log.md` if the skill requires it.

See `references/connections-guide.md` for add/remove steps.
