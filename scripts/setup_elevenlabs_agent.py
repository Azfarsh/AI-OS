#!/usr/bin/env python3
"""
Create or update the ElevenLabs Conversational AI agent for Agency OS.

Run once after setting ELEVENLABS_API_KEY in .env:
  python scripts/setup_elevenlabs_agent.py

Prints ELEVENLABS_AGENT_ID — add it to .env, then run voice_agent.py.
"""

from __future__ import annotations

import json
import os

import requests

from _common import fail, load_env, ok, require_env

AGENT_PROMPT = """You are the Bombay Media Agency OS voice assistant. You help Farhan and the team run agency workflows by voice.

Your job:
1. Greet the user briefly and ask which workflow they want: report, onboard client, proposal, or list clients.
2. Collect ALL required details through natural conversation before calling a tool.
3. Confirm the details back to the user before executing.
4. Call the correct tool once you have everything.
5. Summarize the result clearly.

## Workflows and required fields

**run_report** — monthly performance report
- client_name (string) — e.g. "Demo Corp"
- period (string) — YYYY-MM format, e.g. "2025-01"
- demo (boolean) — default true until ad APIs are connected; use true for testing
- send_email (boolean) — optional, default false
- audio (boolean) — optional, generate voice summary MP3

**run_onboard_client** — new client setup
- client_name, email, services (comma-separated: meta, google, content, seo), budget (number)

**run_proposal** — generate proposal PPTX
- client_name, company, email

**list_clients** — no parameters

**get_connections** — no parameters; shows which integrations are wired

## Rules
- Always use demo=true for reports unless the user explicitly says live data.
- Never guess client names — ask or call list_clients.
- Period must be YYYY-MM.
- Be concise. Proof-first, founder-direct tone.
- After a successful report, tell the user the file path.
"""

TOOL_DEFINITIONS = [
    {
        "type": "client",
        "name": "run_report",
        "description": "Generate a client performance report from ad platform data.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Client name as in registry"},
                "period": {"type": "string", "description": "Report period YYYY-MM"},
                "demo": {"type": "boolean", "description": "Use demo fixture data"},
                "send_email": {"type": "boolean", "description": "Email report to client (default false)"},
                "audio": {"type": "boolean", "description": "Generate MP3 summary"},
            },
            "required": ["client_name", "period"],
        },
        "expects_response": True,
    },
    {
        "type": "client",
        "name": "run_onboard_client",
        "description": "Scaffold a new client folder, brief, registry entry, and contract PPTX.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "New client business name"},
                "email": {"type": "string", "description": "Primary contact email"},
                "services": {"type": "string", "description": "e.g. meta,google"},
                "budget": {"type": "string", "description": "Monthly USD budget"},
            },
            "required": ["client_name", "email", "services", "budget"],
        },
        "expects_response": True,
    },
    {
        "type": "client",
        "name": "run_proposal",
        "description": "Generate a branded proposal PPTX for a prospect.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Prospect contact name"},
                "company": {"type": "string", "description": "Prospect company name"},
                "email": {"type": "string", "description": "Prospect email address"},
            },
            "required": ["client_name", "company", "email"],
        },
        "expects_response": True,
    },
    {
        "type": "client",
        "name": "list_clients",
        "description": "List all clients from the agency registry.",
        "parameters": {"type": "object", "properties": {}},
        "expects_response": True,
    },
    {
        "type": "client",
        "name": "get_connections",
        "description": "Show which Agency OS integrations are connected.",
        "parameters": {"type": "object", "properties": {}},
        "expects_response": True,
    },
]


def main() -> None:
    load_env()
    env = require_env("ELEVENLABS_API_KEY")
    api_key = env["ELEVENLABS_API_KEY"]
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    existing_agent = os.getenv("ELEVENLABS_AGENT_ID")

    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}

    payload = {
        "name": "Bombay Media Agency OS",
        "conversation_config": {
            "agent": {
                "first_message": (
                    "Hey — Bombay Media Agency OS here. "
                    "I can run reports, onboard clients, or build proposals. What do you need?"
                ),
                "language": "en",
                "prompt": {
                    "prompt": AGENT_PROMPT,
                    "llm": "gpt-4o-mini",
                    "temperature": 0.3,
                    "tools": TOOL_DEFINITIONS,
                },
            },
            "tts": {"voice_id": voice_id},
        },
    }

    if existing_agent:
        url = f"https://api.elevenlabs.io/v1/convai/agents/{existing_agent}"
        response = requests.patch(url, headers=headers, json=payload, timeout=60)
        action = "updated"
        agent_id = existing_agent
    else:
        url = "https://api.elevenlabs.io/v1/convai/agents/create"
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        action = "created"
        if response.status_code not in (200, 201):
            fail(f"Agent create failed ({response.status_code}): {response.text[:800]}")
        agent_id = response.json().get("agent_id") or response.json().get("id")

    if response.status_code not in (200, 201):
        fail(f"Agent {action} failed ({response.status_code}): {response.text[:800]}")

    print(f"Agent {action} successfully.")
    print(f"ELEVENLABS_AGENT_ID={agent_id}")
    print("\nAdd to your .env:")
    print(f"ELEVENLABS_AGENT_ID={agent_id}")
    ok(f"AGENT_ID={agent_id}")


if __name__ == "__main__":
    main()
