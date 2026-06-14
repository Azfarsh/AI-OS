#!/usr/bin/env python3
"""
Local HTTP bridge for Bombay Media Agency OS dashboard + browser voice client tools.

Serves web/jarvis/ on http://127.0.0.1:8765 and exposes workflow APIs used by the UI.
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import requests

from _common import REPO_ROOT, fail, load_env, ok
from jarvis_boot import get_boot_briefing
from workflow_tools import TOOL_REGISTRY, execute_tool

WEB_ROOT = REPO_ROOT / "web" / "jarvis"
DEFAULT_PORT = 8765


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    return data


def get_signed_url() -> str:
    load_env()
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")
    if not api_key or not agent_id:
        raise RuntimeError("Set ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID in .env")
    response = requests.get(
        "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
        params={"agent_id": agent_id},
        headers={"xi-api-key": api_key},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Signed URL request failed ({response.status_code}): {response.text[:400]}")
    signed = response.json().get("signed_url")
    if not signed:
        raise RuntimeError("ElevenLabs did not return signed_url")
    return signed


class JarvisHandler(BaseHTTPRequestHandler):
    server_version = "BombayMediaJarvis/1.0"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        if os.getenv("JARVIS_QUIET", "").lower() in {"1", "true", "yes"}:
            return
        super().log_message(format, *args)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/api/status":
            briefing = get_boot_briefing()
            _json_response(
                self,
                200,
                {
                    "status": "ok",
                    "agency": briefing["agency"],
                    "tagline": briefing["tagline"],
                    "date": briefing["date"],
                    "client_count": briefing["client_count"],
                    "clients": briefing["clients"],
                    "connected_count": briefing["connected_count"],
                    "connections": briefing["connections"],
                    "spoken": briefing["spoken"],
                    "command_phrases": briefing["command_phrases"],
                },
            )
            return

        if path == "/api/config":
            load_env()
            _json_response(
                self,
                200,
                {
                    "status": "ok",
                    "agent_id": os.getenv("ELEVENLABS_AGENT_ID", ""),
                    "voice_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
                },
            )
            return

        if path == "/api/signed-url":
            try:
                signed_url = get_signed_url()
            except Exception as exc:  # noqa: BLE001
                _json_response(self, 500, {"status": "error", "message": str(exc)})
                return
            _json_response(self, 200, {"status": "ok", "signed_url": signed_url})
            return

        if path == "/api/tools":
            _json_response(self, 200, {"status": "ok", "tools": sorted(TOOL_REGISTRY.keys())})
            return

        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path.startswith("/api/tools/"):
            tool_name = path.rsplit("/", 1)[-1]
            try:
                params = _read_json_body(self)
            except ValueError as exc:
                _json_response(self, 400, {"status": "error", "message": str(exc)})
                return
            result = execute_tool(tool_name, params)
            status = 200 if result.get("status") == "ok" else 500
            _json_response(self, status, result)
            return

        _json_response(self, 404, {"status": "error", "message": "Not found"})

    def _serve_static(self, path: str) -> None:
        if path in {"/", ""}:
            path = "/index.html"
        file_path = (WEB_ROOT / path.lstrip("/")).resolve()
        try:
            file_path.relative_to(WEB_ROOT.resolve())
        except ValueError:
            self.send_error(403)
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(file_path))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_server(port: int = DEFAULT_PORT, open_browser: bool = False) -> None:
    if not WEB_ROOT.exists():
        fail(f"Missing dashboard files: {WEB_ROOT}")

    server = ThreadingHTTPServer(("127.0.0.1", port), JarvisHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"Jarvis dashboard: {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        import webbrowser

        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nJarvis server stopped.")
        server.shutdown()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Bombay Media Jarvis local dashboard server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--open", action="store_true", help="Open browser after start")
    args = parser.parse_args()
    run_server(port=args.port, open_browser=args.open)


if __name__ == "__main__":
    main()
