# /voice

## Trigger

```
/voice
```

Or run directly:
```
python scripts/jarvis.py
```

CLI mic fallback:
```
python scripts/jarvis.py --cli
```

## Pre-flight

- `connections.md` — `elevenlabs` must be `connected`
- `.env` — `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_VOICE_ID`
- Run `python scripts/setup_elevenlabs_agent.py` once if `ELEVENLABS_AGENT_ID` is empty

## What it does

Launches the **Jarvis dashboard** at http://127.0.0.1:8765 with browser voice (cross-platform).  
Optional `--cli` mode uses terminal mic via `voice_agent.py`.

| Voice intent | Tool | Required details |
|--------------|------|------------------|
| Status check | `get_connections` | — |
| List clients | `list_clients` | — |
| Performance report | `run_report` | client name, period (YYYY-MM), demo yes/no, email yes/no |
| New client | `run_onboard_client` | name, email, services, budget |
| Proposal | `run_proposal` | contact name, company, email |

## Steps

1. Verify `elevenlabs` is `connected` in `connections.md`.
2. Run `python scripts/jarvis.py`.
3. Click the orb → allow microphone.
4. Say the workflow (see `VOICE_TESTING_GUIDE.md` for exact phrases).
5. Confirm when the agent asks.
6. Agent calls local tools via `workflow_tools.py`.
7. Read `spoken_receipt` from tool result aloud; append to `decisions/log.md` if needed.

## Text-only check (no microphone)

```
python scripts/voice_agent.py --test-all-workflows
python scripts/voice_agent.py --text-only
```

## Connections required

`elevenlabs` (required). Other connections depend on workflow (`smtp` for report email, etc.).

## Setup guides

- **`VOICE_SETUP.md`** — install and launch
- **`VOICE_TESTING_GUIDE.md`** — test all 3 workflows
- **`MARKETING_VIDEO_GUIDE.md`** — film the marketing demo
