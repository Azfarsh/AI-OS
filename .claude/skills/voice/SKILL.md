# /voice

## Trigger

```
/voice
```

Or run directly:
```
python scripts/voice_agent.py
```

## Pre-flight

- `connections.md` — `elevenlabs` must be `connected`
- `.env` — `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`, `ELEVENLABS_VOICE_ID`
- Run `python scripts/setup_elevenlabs_agent.py` once if `ELEVENLABS_AGENT_ID` is empty

## What it does

Starts an ElevenLabs Conversational AI session. You **speak**; the agent asks for missing details, then runs Agency OS workflows via client tools:

| Voice intent | Tool | Required details |
|--------------|------|------------------|
| Performance report | `run_report` | client name, period (YYYY-MM), demo yes/no |
| New client | `run_onboard_client` | name, email, services, budget |
| Proposal | `run_proposal` | contact name, company, email |
| List clients | `list_clients` | — |
| Check integrations | `get_connections` | — |

## Steps

1. Verify `elevenlabs` is `connected` in `connections.md`.
2. Run `python scripts/voice_agent.py`.
3. Say the workflow you want (e.g. "Run a report for Demo Corp for January 2025").
4. Answer follow-up questions until the agent confirms and executes.
5. Agent calls `scripts/report_workflow.py`, `generate_contract.py`, or `generate_proposal.py` as needed.
6. Summarize result to user; append to `decisions/log.md` if a workflow ran.

## Text-only check (no microphone)

```
python scripts/voice_agent.py --text-only
```

## Connections required

`elevenlabs` (required). Other connections depend on the workflow invoked (e.g. `smtp` for report email).

## Setup guide

Full instructions: **`VOICE_SETUP.md`**
