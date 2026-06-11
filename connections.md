# Connections — Bombay Media Agency OS

> Check this file before every external call in any skill.
> To add/remove a service: follow `references/connections-guide.md`.
> Status values: `connected` · `not connected` · `demo-mock`

| # | Service | Key | Mechanism | Auth | Status | Last Checked |
|---|---|---|---|---|---|---|
| 1 | Contract Generator | `contract-generator` | python-pptx script | Template PPTX in `references/assets/` | `not connected` | — |
| 2 | Google Drive | `google-drive` | `scripts/gdrive_create_folder.py` | `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` in .env | `not connected` | — |
| 3 | ClickUp | `clickup` | `scripts/clickup_create_project.py` | `CLICKUP_API_TOKEN` in .env | `not connected` | — |
| 4 | SMTP Email | `smtp` | `scripts/send_email.py` | `SMTP_USER` + `SMTP_PASSWORD` in .env (Gmail App Password) | `not connected` | — |
| 5 | Meta Ads | `meta-ads` | `scripts/meta_ads_pull.py` | `META_ACCESS_TOKEN` in .env | `not connected` | — |
| 6 | Google Ads | `google-ads` | `scripts/google_ads_pull.py` | `GOOGLE_ADS_REFRESH_TOKEN` in .env | `not connected` | — |

---

<<<<<<< Updated upstream
## Setup Guide (Demo — All Free)
=======
When wiring a tool: set Mechanism to `script`, fill Last checked (YYYY-MM-DD), ensure `references/{tool}-api.md` exists, copy `.env.example` keys into `.env`. Full key guide: `references/env-api-keys.md`. Claude Code LLM auth: OpenRouter (`ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`) or direct Anthropic (`ANTHROPIC_API_KEY`) — see `references/claude-code-api.md`.
>>>>>>> Stashed changes

### 1. Contract Generator
```
1. Copy Bombay_Media_Dummy_Contract.pptx → references/assets/Bombay_Media_Contract_Template.pptx
2. pip install python-pptx
3. Update status → "connected"
```
**Cost: Free**

### 2. Google Drive (Free Google Cloud)
```
1. Go to console.cloud.google.com
2. Create new project (e.g. "Bombay Media OS")
3. Enable "Google Drive API"
4. IAM → Service Accounts → Create → Download JSON key
5. Share your "Bombay Media" root Drive folder with the service account email
6. Set in .env:
   GOOGLE_SERVICE_ACCOUNT_JSON_PATH=path/to/key.json
   GOOGLE_DRIVE_ROOT_FOLDER_ID=your-folder-id-from-url
7. pip install google-api-python-client google-auth
8. Update status → "connected"
```
**Cost: Free (Google Cloud free tier)**

### 3. ClickUp (Free Plan)
```
1. Create account at clickup.com (free plan works)
2. Settings → Apps → API Token → Copy
3. Create a Space called "Clients"
4. Get Space ID from URL: app.clickup.com/{team_id}/v/s/{space_id}
5. Set in .env:
   CLICKUP_API_TOKEN=pk_xxxxx
   CLICKUP_TEAM_ID=xxxxxxx
   CLICKUP_SPACE_ID=xxxxxxx
6. pip install requests
7. Update status → "connected"
```
**Cost: Free**

### 4. SMTP Email (Gmail — Free)
```
1. Enable 2-Step Verification on Gmail account
2. myaccount.google.com → Security → App Passwords
3. Create App Password for "Mail"
4. Set in .env:
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=farhan@gmail.com (or your Gmail)
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx (the 16-char app password)
   EMAIL_FROM=farhan@bombay-media.com
5. Update status → "connected"
```
**Cost: Free**

### 5. Meta Ads (Requires Meta Business Account)
```
For demo: set status → "demo-mock" and use fixture JSON in scripts/fixtures/
For production: see references/meta-ads-api.md
```

### 6. Google Ads (Requires Developer Token)
```
For demo: set status → "demo-mock" and use fixture JSON in scripts/fixtures/
For production: see references/google-ads-api.md
```
