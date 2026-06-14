# Voice Setup — Bombay Media Agency OS

Talk to Agency OS. ElevenLabs handles speech; client tools run your workflows locally.

---

## Quick start (recommended)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env               # fill ElevenLabs + SMTP keys
python scripts/setup_elevenlabs_agent.py
python scripts/jarvis.py
```

Opens **http://127.0.0.1:8765** — click the orb and speak.

Full test commands: **`VOICE_TESTING_GUIDE.md`**  
Marketing demo filming: **`MARKETING_VIDEO_GUIDE.md`**

---

## Launch modes

| Command | What it does |
|---------|----------------|
| `python scripts/jarvis.py` | Branded boot + dashboard + browser voice (Mac/Win/Linux) |
| `python scripts/jarvis.py --cli` | Terminal mic session via PyAudio |
| `python scripts/jarvis_server.py --open` | Dashboard only |
| `python scripts/voice_agent.py --text-only` | Config check, no mic |
| `python scripts/voice_agent.py --test-all-workflows` | Text test all 3 workflows |

---

## What you need from ElevenLabs

| Item | Where to get it | Put in `.env` |
|------|-----------------|---------------|
| **API key** | [elevenlabs.io](https://elevenlabs.io) → Profile → API Keys | `ELEVENLABS_API_KEY` |
| **Voice ID** | Voice Library or your cloned voice | `ELEVENLABS_VOICE_ID` |
| **Agent ID** | Auto-created by setup script | `ELEVENLABS_AGENT_ID` |

Run `python scripts/setup_elevenlabs_agent.py` after changing clients or connections — it refreshes the agent's opening briefing.

---

## Architecture

```
jarvis.py (launcher)
    ├── jarvis_boot.py      → status briefing
    ├── jarvis_server.py    → localhost:8765
    │       ├── web/jarvis/ → branded dashboard UI
    │       └── /api/tools  → workflow_tools.py
    └── voice_agent.py      → CLI mic (optional)
```

Browser voice uses ElevenLabs signed URL + client tools that POST to your local server. No API key exposed to the browser.

---

## Workflows the voice agent can run

| Say this | What runs |
|----------|-----------|
| "Status check" | Reads `connections.md` |
| "List clients" | Reads `context/clients.md` |
| "Run a report for Demo Corp, period 2025-01, demo, email it" | `report_workflow.py --demo --send-email` |
| "Onboard client Acme, john@acme.com, meta and content, budget 5000" | Scaffold + contract PPTX |
| "Create a proposal for Jane at Demo Corp, email jane@demo.com" | `generate_proposal.py` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Dashboard won't open | Run `python scripts/jarvis_server.py --open` manually |
| Orb won't connect | Check `.env` ElevenLabs keys; run setup script |
| Mic blocked | Allow microphone for localhost in browser settings |
| PyAudio fails | Use `python scripts/jarvis.py` (browser voice) instead of `--cli` |
| Email fails on report | Set SMTP in `.env`; `smtp` = `connected` in `connections.md` |

Detail: `references/elevenlabs-api.md`
