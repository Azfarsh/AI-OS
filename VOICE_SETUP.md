# Voice Setup — Bombay Media Agency OS

Talk to Agency OS. ElevenLabs handles speech; client tools run your workflows locally.

---

## What you need from ElevenLabs

| Item | Where to get it | Put in `.env` |
|------|-----------------|---------------|
| **API key** | [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys | `ELEVENLABS_API_KEY` |
| **Voice ID** | Voice Library or your cloned voice | `ELEVENLABS_VOICE_ID` |
| **Agent ID** | Auto-created by setup script | `ELEVENLABS_AGENT_ID` |

Optional: clone Farhan's voice in ElevenLabs Voice Lab for branded audio on reports.

---

## One-time setup (10 minutes)

### 1. Python environment

```powershell
cd "C:\Users\Azfar\OneDrive\Desktop\AI OS"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

If `pyaudio` fails on Windows:

```powershell
pip install pipwin
pipwin install pyaudio
```

### 2. Environment file

```powershell
copy .env.example .env
```

Edit `.env` and set:

```env
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
```

### 3. Create the voice agent

```powershell
python scripts/setup_elevenlabs_agent.py
```

Copy the printed `ELEVENLABS_AGENT_ID` into `.env`.

### 4. Mark ElevenLabs connected

In `connections.md`, set row 7 (`elevenlabs`) status to `connected`.

### 5. Validate structure

```powershell
python scripts/validate_repo.py
```

Expect: `OK — Agency OS structure valid`.

---

## How to run the project

### Option A — Voice (recommended once ElevenLabs is wired)

```powershell
.\.venv\Scripts\activate
python scripts/voice_agent.py
```

**Example conversation:**

> You: "Run a performance report."  
> Agent: "Which client and period?"  
> You: "Demo Corp, January 2025, use demo data."  
> Agent: "Generating report… Done. Saved to clients/demo-corp/reports/report-2025-01.md."

### Option B — Cursor Agent (text, dry run)

Follow `TESTING_IN_CURSOR.md` — paste prompts with `DRY RUN`.

### Option C — Direct CLI (no voice)

```powershell
# Report with dummy data (no ad APIs needed)
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo

# With audio summary (needs ElevenLabs)
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo --audio
```

### Option D — Claude Code slash commands

Same skills as Cursor: `/report`, `/onboard-client`, `/proposal`, `/voice`.

---

## Report workflow — template locations

Edit these files to change report layout (same pattern as proposal/contract):

| Purpose | File |
|---------|------|
| **Sections & tables** (main content) | `references/report-template.md` |
| **Header wrapper** (`{{CLIENT_NAME}}`, etc.) | `templates/report-template.md` |
| **Dummy test data** | `clients/demo-corp/fixtures/meta-YYYY-MM.json`, `google-YYYY-MM.json` |

Generated output: `clients/{slug}/reports/report-{period}.md`

To test a new period, copy fixture files:

```
clients/demo-corp/fixtures/meta-2025-02.json
clients/demo-corp/fixtures/google-2025-02.json
```

---

## Workflows the voice agent can run

| Say this | What runs |
|----------|-----------|
| "Run a report for Demo Corp, period 2025-01, demo data" | `report_workflow.py --demo` |
| "Onboard client Acme Coaching, john@acme.com, meta and google, budget 5000" | Scaffold + contract PPTX |
| "Create a proposal for Jane at Demo Corp, jane@demo-corp.example" | `generate_proposal.py` |
| "List clients" | Reads `context/clients.md` |
| "What's connected?" | Reads `connections.md` |

---

## Test report with dummy data (right now)

```powershell
python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo
```

Open: `clients/demo-corp/reports/report-2025-01.md`

---

## Wiring live ad platforms (later)

When ready for real Meta/Google data:

1. Fill Meta/Google vars in `.env` (see `references/env-api-keys.md`)
2. Set `meta-ads` / `google-ads` to `connected` in `connections.md`
3. Run without `--demo`:

```powershell
python scripts/report_workflow.py --client-name "Xenvo" --period 2025-05
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Voice agent won't start | Check `ELEVENLABS_API_KEY` and `ELEVENLABS_AGENT_ID` |
| No mic / PyAudio error | Use CLI: `report_workflow.py --demo` |
| Report empty | Ensure fixtures exist for that period under `clients/{slug}/fixtures/` |
| Email fails | Set SMTP in `.env`; use `--send-email` only when `smtp` is connected |

Detail: `references/elevenlabs-api.md`
