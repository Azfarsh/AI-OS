#!/usr/bin/env python3
"""Convert report executive summary (or any text) to MP3 via ElevenLabs TTS."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import requests

from _common import REPO_ROOT, fail, load_env, ok, require_env

DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George — free-tier API voice


def _extract_executive_summary(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    match = re.search(
        r"## Executive Summary\s*\n+(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return text[:1500]


def synthesize_speech(text: str, voice_id: str, api_key: str, output: Path) -> None:
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    def _request(vid: str) -> requests.Response:
        return requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
            json=payload,
            headers=headers,
            timeout=120,
        )

    response = _request(voice_id)
    if (
        response.status_code == 402
        and "paid_plan_required" in response.text
        and voice_id != DEFAULT_VOICE_ID
    ):
        print(f"Note: voice {voice_id} requires paid plan - falling back to default voice.")
        response = _request(DEFAULT_VOICE_ID)
    if response.status_code != 200:
        fail(f"ElevenLabs TTS failed ({response.status_code}): {response.text[:500]}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(response.content)


def main() -> None:
    parser = argparse.ArgumentParser(description="ElevenLabs text-to-speech for Agency OS")
    parser.add_argument("--text", default=None, help="Raw text to speak")
    parser.add_argument("--text-file", default=None, help="Path to text file")
    parser.add_argument("--report-path", default=None, help="Extract Executive Summary from report MD")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--voice-id", default=None, help="Override ELEVENLABS_VOICE_ID")
    args = parser.parse_args()

    load_env()
    env = require_env("ELEVENLABS_API_KEY")
    voice_id = args.voice_id or os.getenv("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE_ID

    if args.report_path:
        path = Path(args.report_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        text = _extract_executive_summary(path)
    elif args.text_file:
        path = Path(args.text_file)
        if not path.is_absolute():
            path = REPO_ROOT / path
        text = path.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        fail("Provide --text, --text-file, or --report-path")

    output = Path(args.output)
    if not output.is_absolute():
        output = REPO_ROOT / output

    synthesize_speech(text.strip(), voice_id, env["ELEVENLABS_API_KEY"], output)
    ok(f"AUDIO_PATH={output}")


if __name__ == "__main__":
    main()
