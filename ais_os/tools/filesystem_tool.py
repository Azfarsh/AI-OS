"""Filesystem read/write within workspace bounds."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ais_os.config import get_config
from ais_os.tools.base import BaseTool, ToolResult

logger = logging.getLogger("ais_os.tools.filesystem")


class FilesystemTool(BaseTool):
    name = "filesystem"
    description = (
        "Read, write, or list files under the AIS-OS workspace. "
        "Paths are relative to workspace root."
    )

    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "list"],
                },
                "path": {"type": "string"},
                "content": {"type": "string", "description": "Required for write"},
            },
            "required": ["action", "path"],
        }

    def _resolve(self, rel: str) -> Path:
        cfg = get_config()
        root = cfg.workspace.resolve()
        target = (root / rel).resolve()
        if not str(target).startswith(str(root)):
            raise ValueError("Path escapes workspace")
        return target

    async def run(self, **kwargs: Any) -> ToolResult:
        cfg = get_config()
        if not cfg.agent_permissions.get("filesystem", False):
            return ToolResult(False, "Filesystem tool disabled in config")

        action = kwargs.get("action", "read")
        rel = kwargs.get("path", "")
        try:
            path = self._resolve(rel)
        except ValueError as exc:
            return ToolResult(False, str(exc))

        try:
            if action == "read":
                if not path.exists():
                    return ToolResult(False, f"Not found: {rel}")
                text = path.read_text(encoding="utf-8")
                if len(text) > 50_000:
                    text = text[:50_000] + "\n...(truncated)"
                return ToolResult(True, text)

            if action == "write":
                content = kwargs.get("content", "")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                logger.info("Wrote file: %s", path)
                return ToolResult(True, f"Wrote {len(content)} bytes to {rel}")

            if action == "list":
                if not path.exists():
                    return ToolResult(False, f"Not found: {rel}")
                if path.is_file():
                    return ToolResult(True, rel)
                entries = sorted(p.name for p in path.iterdir())[:200]
                return ToolResult(True, "\n".join(entries))

            return ToolResult(False, f"Unknown action: {action}")
        except Exception as exc:
            logger.exception("Filesystem tool error")
            return ToolResult(False, str(exc))
