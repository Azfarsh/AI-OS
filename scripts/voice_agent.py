#!/usr/bin/env python3
"""
Voice-controlled Agency OS — talk to run workflows via ElevenLabs Conversational AI.

Prerequisites:
  1. pip install -r requirements.txt  (includes elevenlabs, pyaudio)
  2. Copy .env.example → .env and set ELEVENLABS_API_KEY
  3. python scripts/setup_elevenlabs_agent.py  → copy ELEVENLABS_AGENT_ID to .env
  4. python scripts/voice_agent.py

Text-only test (no microphone):
  python scripts/voice_agent.py --text-only
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from typing import Any

from _common import fail, load_env, ok, require_env

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import ClientTools, Conversation
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
except ImportError:
    fail("Missing elevenlabs SDK. Run: pip install elevenlabs pyaudio")


def _stringify_tool(tool_fn: Callable[[dict], Any]) -> Callable[[dict], str]:
    """ElevenLabs ConvAI requires client tool results to be strings, not dicts."""

    def wrapper(params: dict) -> str:
        result = tool_fn(params)
        if isinstance(result, str):
            return result
        return json.dumps(result)

    return wrapper


def _register_tools(client_tools: ClientTools) -> None:
    from workflow_tools import get_connections, list_clients, run_onboard_client, run_proposal, run_report

    for name, fn in (
        ("run_report", run_report),
        ("run_onboard_client", run_onboard_client),
        ("run_proposal", run_proposal),
        ("list_clients", list_clients),
        ("get_connections", get_connections),
    ):
        client_tools.register(name, _stringify_tool(fn), is_async=False)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Agency OS voice agent")
    parser.add_argument("--text-only", action="store_true", help="Print setup info; skip mic session")
    parser.add_argument(
        "--test-tool",
        default=None,
        help="Invoke a client tool without mic (e.g. run_report) and print string result",
    )
    parser.add_argument(
        "--test-params",
        default="{}",
        help="JSON params for --test-tool",
    )
    parser.add_argument(
        "--test-report",
        action="store_true",
        help="Shortcut: run demo report tool (Demo Corp, 2025-01, audio) without mic",
    )
    parser.add_argument(
        "--test-xenvo",
        action="store_true",
        help="Shortcut: test report, onboard, and proposal for Xenvo without mic",
    )
    args = parser.parse_args()

    if args.test_report:
        args.test_tool = "run_report"
        args.test_params = json.dumps(
            {"client_name": "Demo Corp", "period": "2025-01", "demo": True, "audio": True}
        )

    if args.test_xenvo:
        from workflow_tools import run_onboard_client, run_proposal, run_report

        xenvo_tests = [
            ("run_report", {"client_name": "Xenvo", "period": "2025-01", "demo": True, "audio": False}),
            (
                "run_onboard_client",
                {
                    "client_name": "Xenvo",
                    "email": "azfarshaikh7860@gmail.com",
                    "services": "meta,content",
                    "budget": "5000",
                },
            ),
            (
                "run_proposal",
                {
                    "client_name": "Xenvo",
                    "company": "Xenvo",
                    "email": "azfarshaikh7860@gmail.com",
                    "budget": "5000",
                    "services": "meta,content",
                },
            ),
        ]
        tools = {
            "run_report": run_report,
            "run_onboard_client": run_onboard_client,
            "run_proposal": run_proposal,
        }
        failed = False
        for tool_name, params in xenvo_tests:
            print(f"\n--- {tool_name} ---")
            result = _stringify_tool(tools[tool_name])(params)
            print(result)
            if '"status": "error"' in result:
                failed = True
        if failed:
            fail("One or more Xenvo workflow tests failed")
        ok("XENVO_WORKFLOWS_OK")

    env = require_env("ELEVENLABS_API_KEY", "ELEVENLABS_AGENT_ID")
    api_key = env["ELEVENLABS_API_KEY"]
    agent_id = env["ELEVENLABS_AGENT_ID"]

    if args.test_tool:
        from workflow_tools import get_connections, list_clients, run_onboard_client, run_proposal, run_report

        tools = {
            "run_report": run_report,
            "run_onboard_client": run_onboard_client,
            "run_proposal": run_proposal,
            "list_clients": list_clients,
            "get_connections": get_connections,
        }
        if args.test_tool not in tools:
            fail(f"Unknown tool: {args.test_tool}. Choose from: {', '.join(tools)}")
        try:
            params = json.loads(args.test_params)
        except json.JSONDecodeError as exc:
            fail(f"Invalid --test-params JSON: {exc}")
        if not isinstance(params, dict):
            fail("--test-params must be a JSON object")
        result = _stringify_tool(tools[args.test_tool])(params)
        print(result)
        ok(f"TOOL_OK={args.test_tool}")

    if args.text_only:
        print("ElevenLabs voice agent configured.")
        print(f"  Agent ID: {agent_id}")
        print("  Run without --text-only to start a voice session.")
        print("  Or test report directly:")
        print('  python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo')
        sys.exit(0)

    client_tools = ClientTools()
    _register_tools(client_tools)

    client = ElevenLabs(api_key=api_key)
    audio = DefaultAudioInterface()

    conversation = Conversation(
        client=client,
        agent_id=agent_id,
        requires_auth=False,
        audio_interface=audio,
        client_tools=client_tools,
    )

    print("=" * 60)
    print("Bombay Media Agency OS — Voice Agent")
    print("Speak to run reports, onboard clients, or proposals.")
    print("Press Ctrl+C to end the session.")
    print("=" * 60)

    try:
        conversation.start_session()
        conversation.wait_for_session_end()
    except KeyboardInterrupt:
        print("\nSession ended.")


if __name__ == "__main__":
    main()
