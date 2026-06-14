# ElevenLabs — voice agent & TTS

Agency OS uses ElevenLabs for:

1. **Conversational AI** — speak to run workflows (`scripts/voice_agent.py`)
2. **TTS** — narrated executive summary on reports (`scripts/elevenlabs_tts.py`)

## Env vars

| Variable | Required | Purpose |
|----------|----------|---------|
| `ELEVENLABS_API_KEY` | Yes | API key from elevenlabs.io |
| `ELEVENLABS_AGENT_ID` | Yes (voice) | Created by `setup_elevenlabs_agent.py` |
| `ELEVENLABS_VOICE_ID` | Yes (TTS) | Voice ID for speech output |

## Get an API key

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Profile → **API Keys** → Create key
3. Add to `.env`: `ELEVENLABS_API_KEY=sk_...`

## Voice ID

- **Default:** `JBFqnCBsd6RMkjVDRZzb` (George — works out of the box)
- **Custom clone:** Voice Lab → Add Generative or Instant Voice Clone → copy Voice ID → `ELEVENLABS_VOICE_ID=...`

## Create the agent (one time)

```powershell
python scripts/setup_elevenlabs_agent.py
```

Copy printed `ELEVENLABS_AGENT_ID` into `.env`.

## Scripts

| Script | Purpose |
|--------|---------|
| `setup_elevenlabs_agent.py` | Create/update ConvAI agent with workflow tools |
| `voice_agent.py` | Start microphone voice session |
| `elevenlabs_tts.py` | Text or report → MP3 |

## Client tools (must match agent config)

Registered in `voice_agent.py`:

- `run_report`
- `run_onboard_client`
- `run_proposal`
- `list_clients`
- `get_connections`

## Pricing note

Conversational AI and TTS consume ElevenLabs credits. Use `--demo` for report testing to avoid live ad API + minimize tool calls during dev.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Missing elevenlabs SDK` | `pip install elevenlabs pyaudio` |
| PyAudio install fails on Windows | `pip install pipwin && pipwin install pyaudio` or use prebuilt wheel |
| Agent tool not called | Re-run `setup_elevenlabs_agent.py`; tool names must match |
| No microphone | Run `voice_agent.py --text-only`; use CLI workflows instead |
