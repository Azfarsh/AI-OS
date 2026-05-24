# AIS-OS — API & credentials checklist (for client)

Share this list with your client. Mark what they need **now** vs **later** based on which phase you enable.

---

## Free testing mode (recommended to start — $0 models)

The project ships with **`AIS_USE_FREE_MODELS=true`** (see `.env`). You only need:

| Credential | Cost | Notes |
|------------|------|--------|
| **OpenRouter API key** | **$0** for chat | Uses models ending in `:free` and `openrouter/free` router — no paid credits required for free models |

**No paid embedding API** — memory vectors use local hashing in free mode (`embed_provider: local`).

**Free OpenRouter models used by default:**

| Task | Model ID |
|------|----------|
| General chat | `openrouter/free` |
| Code / tools | `qwen/qwen3-coder:free` |
| Research / planning | `deepseek/deepseek-v4-flash:free` |
| Fast replies | `google/gemma-4-27b-it:free` |

Override: `/model qwen/qwen3-coder:free` in the REPL.

Verify: `.\scripts\test-free-models.ps1` after setting `OPENROUTER_API_KEY`.

Agency memory layout (from architecture doc): `memory/leads/`, `clients/`, `campaigns/`, `reports/`, `transcripts/`, `context/`.

To use **paid** models later: set `AIS_USE_FREE_MODELS=false` in `.env`.

---

## Required to run Phase 1 (terminal chat + agents + memory)

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **OpenRouter API key** | https://openrouter.ai/keys | All chat, agents, model routing (Claude, GPT, Gemini, DeepSeek via one key) | `OPENROUTER_API_KEY` |

**Optional but recommended on OpenRouter account:**

- Billing / credits enabled (pay-as-you-go)
- Model access enabled for: Claude 3.5+, GPT-4.1, Gemini 2.0 Flash, DeepSeek (as listed in `configs/default.yaml`)

Embeddings for long-term memory also go through OpenRouter (`openai/text-embedding-3-small`). Same key.

---

## Optional — Phase 1 (no client key if skipped)

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **Ollama (local)** | https://ollama.com — runs on client machine | Local models, offline fallback | `OLLAMA_BASE_URL`, `OLLAMA_API_KEY` |

No API key needed if Ollama runs locally; default `OLLAMA_API_KEY=ollama`.

---

## Phase 2 — Voice “Jarvis” mode

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **ElevenLabs API key** | https://elevenlabs.io/app/settings/api-keys | Text-to-speech, streaming voice | `ELEVENLABS_API_KEY` |
| **ElevenLabs voice ID** | ElevenLabs voice library | Which voice Jarvis uses | `ELEVENLABS_VOICE_ID` (in `configs/default.yaml` → `voice.elevenlabs_voice_id`) |

Whisper runs **locally** (no API key) via `faster-whisper` when Phase 2 is installed.

---

## Phase 3 — Browser & integrations

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **GitHub personal access token** | GitHub → Settings → Developer settings → PAT | Repos, issues, PRs | `GITHUB_TOKEN` |
| **Slack bot token** | https://api.slack.com/apps | Slack read/post (bot scopes) | `SLACK_BOT_TOKEN` |
| **Slack signing secret** | Same Slack app | Verify Slack events (if webhooks added) | `SLACK_SIGNING_SECRET` |
| **Google service account JSON** | Google Cloud Console → IAM → Service account | Gmail, Calendar, Drive (Workspace) | `GOOGLE_APPLICATION_CREDENTIALS` (path to `.json` file) |

**Browser automation (LinkedIn, forms, scraping):**

- Usually **no separate API** — Playwright uses the client’s **logged-in browser session** or stored session cookies.
- Client may need to provide: LinkedIn login (or session export), 2FA process, and approval to automate on their account.

---

## Phase 3+ — Email & outreach (if you wire them)

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **Gmail / Google OAuth** | Google Cloud OAuth client | Read/send email | OAuth client ID/secret + refresh token (or service account) |
| **Microsoft Graph** | Azure App registration | Outlook email/calendar | `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` |
| **Resend / SendGrid / Mailgun** | Provider dashboard | Transactional email API | Provider-specific (`RESEND_API_KEY`, etc.) |

Pick one email stack per client; not all are required.

---

## Phase 3+ — Web search & research

| Credential | Where to get it | Used for | Env variable |
|------------|-----------------|----------|--------------|
| **Tavily API key** | https://tavily.com | Agent web search (common choice) | `TAVILY_API_KEY` |
| **Serper API key** | https://serper.dev | Google search API | `SERPER_API_KEY` |
| **Brave Search API** | https://brave.com/search/api | Alternative search | `BRAVE_API_KEY` |

One search provider is enough.

---

## MCP servers (optional, per client stack)

If the client uses MCP tools in Cursor/Claude, they may share:

- MCP server URLs and auth tokens (varies per server)
- Config lives in `configs/default.yaml` → `mcp.servers` and/or `.cursor/mcp.json`

Examples: Notion, Linear, Postgres, custom internal APIs — **ask per integration**.

---

## What you do NOT need for terminal-only Phase 1

- No frontend hosting
- No database server (ChromaDB is local files under `memory/chroma/`)
- No ElevenLabs / Slack / GitHub keys until you enable those features
- Claude Code / Anthropic console key is **not** required if using OpenRouter only

---

## Client handoff template (copy/paste to email)

```
Please provide the following for AIS-OS terminal setup:

REQUIRED (Phase 1):
1. OpenRouter API key — https://openrouter.ai/keys
   - Confirm billing/credits are active
   - Confirm access to: Claude 3.5+, GPT-4.1, Gemini 2.0 Flash (or tell us which models you prefer)

OPTIONAL NOW:
2. Ollama installed locally? (yes/no) — for offline models

FOR VOICE (Phase 2):
3. ElevenLabs API key + preferred voice ID

FOR AUTOMATIONS (Phase 3+):
4. GitHub token (repo scope: __________)
5. Slack bot token (workspace: __________)
6. Google service account JSON (Workspace admin approval: yes/no)
7. LinkedIn: OK to automate logged-in browser? (yes/no)
8. Email provider: Gmail / Outlook / other: __________
9. Web search API: Tavily / Serper / other: __________

Security: send secrets via a password manager share or encrypted channel — not plain email if possible.
```

---

## Local setup file

All secrets go in `.env` (copy from `.env.example`). Never commit `.env` to git.
