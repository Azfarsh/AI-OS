# AIS-OS Terminal Runtime — Architecture

This document maps the **original AIS-OS kit** (Claude Code skills + Four Cs) to the **Python terminal runtime** added in v0.1.0.

## Reuse map (original → runtime)

| Original AIS-OS | Runtime role |
|-----------------|--------------|
| **Context** (`context/`, `CLAUDE.md`, `aios-intake.md`) | Loaded into every agent prompt via `MemoryManager.build_system_context()` |
| **Connections** (`connections.md`) | Injected into context; Phase 3+ `integrations/` |
| **Capabilities** (`.claude/skills/`, future agents) | `agents/` + LangGraph `orchestrator/` |
| **Cadence** (future automations) | `workflows/` (Phase 4) |
| **Three Ms** (`references/3ms-framework.md`) | Executive + Automation agent system prompts |
| `/onboard`, `/audit`, `/level-up` | Unchanged Claude Code skills in `.claude/skills/` |
| `decisions/log.md` | Readable via filesystem tool + context loader |
| `EXPANSIONS.md` | Guides folder growth; Memory agent enforces rules |

## Directory layout

```
AIS-OS/
├── ais_os/                 # Python package (terminal runtime)
│   ├── agents/             # Modular agents (9)
│   ├── memory/             # ChromaDB, sessions, markdown, short-term
│   ├── models/             # OpenRouter + model routing
│   ├── orchestrator/       # LangGraph routing graph
│   ├── terminal/           # Rich REPL + slash commands
│   └── tools/              # Terminal, filesystem (MCP-ready registry)
├── configs/default.yaml    # YAML configuration
├── context/                # Four Cs — Context (kit)
├── memory/notes|chroma     # Long-term memory stores
├── sessions/               # Persisted chat sessions
├── voice/                  # Phase 2 — Jarvis
├── workflows/              # Phase 4 — Cadence
├── integrations/           # Phase 3 — Connections implementations
├── .claude/skills/         # Original kit skills (preserved)
└── scripts/setup.*         # Install helpers
```

## Request flow (Phase 1)

```
User input (terminal)
    → CommandRouter (/chat, /code, …) or default chat
    → MemoryManager: context files + vector retrieval
    → LangGraph Orchestrator: route → specialist agent
    → OpenRouter (routed model) + optional tools
    → Rich UI output + memory write-back
```

## Phases

| Phase | Scope |
|-------|--------|
| **1** (current) | Terminal REPL, OpenRouter, commands, ChromaDB memory, LangGraph agents, tools |
| **2** | ElevenLabs TTS, Whisper STT, wake word, `/voice` |
| **3** | Playwright browser agent, LinkedIn flows, integrations |
| **4** | Autonomous workflows, planning, long-running tasks |

## Model routing

`ModelRouter` classifies messages (code / research / planning / fast) and selects models from `configs/default.yaml` → `models.routing`. Override with `/model <openrouter-id>` or `ais chat -m ...`.

## Security

- Filesystem and terminal tools are bounded to `AIS_WORKSPACE`.
- Agent permissions in YAML (`agents.permissions`).
- API keys only via `.env` (never committed).
