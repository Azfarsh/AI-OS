#!/usr/bin/env python3
"""
Bombay Media Agency OS — Jarvis launcher.

Default: local dashboard + browser voice (cross-platform, no PyAudio required).
CLI voice: python scripts/jarvis.py --cli

Usage:
  python scripts/jarvis.py
  python scripts/jarvis.py --cli
  python scripts/jarvis.py --server-only --port 8765
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from jarvis_boot import get_boot_briefing, print_boot_banner

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Bombay Media Agency OS — Jarvis")
    parser.add_argument("--cli", action="store_true", help="Terminal voice session (PyAudio mic)")
    parser.add_argument("--server-only", action="store_true", help="Dashboard server only")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    args = parser.parse_args()

    print_boot_banner()
    briefing = get_boot_briefing()
    print(f"\n  Briefing: {briefing['spoken']}\n")

    if args.cli:
        print("Starting CLI voice session...\n")
        result = subprocess.run([sys.executable, "scripts/voice_agent.py"], cwd=REPO_ROOT)
        sys.exit(result.returncode)

    open_browser = not args.no_browser
    cmd = [
        sys.executable,
        "scripts/jarvis_server.py",
        "--port",
        str(args.port),
    ]
    if open_browser:
        cmd.append("--open")

    print("Launching Jarvis dashboard...\n")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
