"""Persist chat sessions to disk."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiofiles

from ais_os.config import get_config

logger = logging.getLogger("ais_os.memory.session")


class SessionStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or get_config().sessions_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.base_dir / f"{session_id}.json"

    def create_session(self, title: str = "New session") -> str:
        session_id = str(uuid.uuid4())[:8]
        payload = {
            "id": session_id,
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
            "metadata": {},
        }
        self._path(session_id).write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        return session_id

    async def aload(self, session_id: str) -> dict[str, Any]:
        path = self._path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        async with aiofiles.open(path, encoding="utf-8") as f:
            return json.loads(await f.read())

    async def asave(self, session_id: str, data: dict[str, Any]) -> None:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        path = self._path(session_id)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2))

    def list_sessions(self) -> list[dict[str, str]]:
        sessions: list[dict[str, str]] = []
        for p in sorted(self.base_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                sessions.append(
                    {
                        "id": data.get("id", p.stem),
                        "title": data.get("title", p.stem),
                        "updated_at": data.get("updated_at", ""),
                    }
                )
            except json.JSONDecodeError:
                logger.warning("Skipping corrupt session file: %s", p)
        return sessions
