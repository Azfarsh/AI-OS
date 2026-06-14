# Voice Testing Guide — Bombay Media Agency OS

Test all three core workflows (report, onboard, proposal) via voice or text. Works on **Mac, Windows, and Linux**.

---

## One-time setup

```bash
cd AI-OS
python -m venv .venv
```

**Mac / Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows: copy .env.example .env
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env`:
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `SMTP_USER` + `SMTP_PASSWORD` (if testing report email)

Then:
```bash
python scripts/setup_elevenlabs_agent.py
# Copy printed ELEVENLABS_AGENT_ID into .env
python scripts/validate_repo.py
```

Set `elevenlabs` and `smtp` to `connected` in `connections.md`.

---

## Launch options

| Mode | Command | Best for |
|------|---------|----------|
| **Dashboard + browser voice** (recommended) | `python scripts/jarvis.py` | Marketing demo, no PyAudio issues |
| CLI mic voice | `python scripts/jarvis.py --cli` | Terminal-only session |
| Server only | `python scripts/jarvis_server.py --open` | Custom port / no launcher banner |
| Text tool tests (no mic) | `python scripts/voice_agent.py --test-all-workflows` | CI / quick validation |

Dashboard URL: **http://127.0.0.1:8765**

1. Click the purple **orb** → allow microphone
2. Wait for “Listening…”
3. Speak naturally (see commands below)
4. Watch the **Activity Log** for tool results and spoken receipts

---

## Voice commands for all 3 workflows

Speak clearly. The agent confirms before running.

### 0. Warm-up (optional)

| Say this | What happens |
|----------|----------------|
| “Status check” | Reads connected integrations |
| “List clients” | Reads client registry |

### 1. Report workflow

**Full demo command (recommended for video):**

> “Run a report for Demo Corp, period January 2025, use demo data, and email it to the client.”

**Shorter variants:**

> “Report for Demo Corp, 2025-01, demo, email it.”

> “Generate a performance report for Demo Corp for January 2025 with demo data.”

**Agent will confirm:** client name, period, demo yes/no, email yes/no.

**Pass criteria:**
- `clients/demo-corp/reports/report-2025-01.md` created/updated
- `clients/demo-corp/reports/report-2025-01.pptx` created/updated
- Email to `hannanchougle28@gmail.com` (Demo Corp brief) if SMTP wired
- Agent says spoken receipt: *“Report complete… PPTX ready… Email sent…”*

### 2. Onboard client workflow

**Demo command:**

> “Onboard a new client called Voice Test Co, email hannanchougle28@gmail.com, services meta and content, budget five thousand.”

**Shorter:**

> “Onboard client Voice Test Co, hannanchougle28@gmail.com, meta and content, budget 5000.”

**Pass criteria:**
- Folder `clients/voice-test-co/` with brief, notes, contracts
- Row added to `context/clients.md`
- Contract PPTX generated
- Agent receipt: *“Onboarding complete… contract PPTX ready.”*

### 3. Proposal workflow

**Demo command:**

> “Create a proposal for Jane Doe at Demo Corp, email hannanchougle28@gmail.com.”

**Shorter:**

> “Proposal for Jane at Demo Corp, email hannanchougle28@gmail.com.”

**Note:** Demo Corp has meeting notes in `clients/demo-corp/notes.md` — required for a rich proposal.

**Pass criteria:**
- New file under `clients/demo-corp/proposals/proposal-*.pptx`
- Agent receipt: *“Proposal ready for Demo Corp…”*

---

## Text-only testing (no microphone)

Run all three workflows in sequence:

```bash
python scripts/voice_agent.py --test-all-workflows
```

Individual tools:

```bash
python scripts/voice_agent.py --test-tool run_report --test-params "{\"client_name\":\"Demo Corp\",\"period\":\"2025-01\",\"demo\":true,\"send_email\":false}"

python scripts/voice_agent.py --test-tool run_onboard_client --test-params "{\"client_name\":\"Voice Test Co\",\"email\":\"hannanchougle28@gmail.com\",\"services\":\"meta,content\",\"budget\":\"5000\"}"

python scripts/voice_agent.py --test-tool run_proposal --test-params "{\"client_name\":\"Jane Doe\",\"company\":\"Demo Corp\",\"email\":\"hannanchougle28@gmail.com\"}"
```

Dashboard API (server must be running):

```bash
curl -X POST http://127.0.0.1:8765/api/tools/run_report \
  -H "Content-Type: application/json" \
  -d '{"client_name":"Demo Corp","period":"2025-01","demo":true}'
```

---

## Recommended test sequence (5 minutes)

1. `python scripts/jarvis.py`
2. Click orb → say **“Status check”**
3. Say **report command** (full sentence above)
4. Say **onboard command**
5. Say **proposal command**
6. Open generated files in `clients/` to verify
7. Click **End Session**

Re-run agent setup after adding clients (updates boot briefing):

```bash
python scripts/setup_elevenlabs_agent.py
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Orb does not connect | Check `ELEVENLABS_API_KEY` + `ELEVENLABS_AGENT_ID` in `.env` |
| Mic blocked | Browser permission → allow microphone for localhost |
| PyAudio fails (CLI mode) | Use dashboard mode: `python scripts/jarvis.py` |
| Report email fails | Set Gmail App Password in `.env`; `smtp` = connected |
| Proposal empty | Ensure `clients/demo-corp/notes.md` has content |
| Tool error in log | Read Activity Log; fix missing env or connection status |

---

## Cursor / Claude Code

Skill: `/voice` or paste:

```
Run python scripts/jarvis.py and guide me through testing report, onboard, and proposal via voice commands.
```
