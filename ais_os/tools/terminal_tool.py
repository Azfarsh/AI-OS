"""Execute shell commands (permission-gated)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ais_os.config import get_config
from ais_os.tools.base import BaseTool, ToolResult

logger = logging.getLogger("ais_os.tools.terminal")


class TerminalTool(BaseTool):
    name = "run_terminal"
    description = (
        "Run a shell command in the AIS-OS workspace. "
        "Use for git, npm, python, build, deploy scripts. "
        "Returns stdout and stderr."
    )

    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute",
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": "Max runtime in seconds",
                    "default": 120,
                },
            },
            "required": ["command"],
        }

    async def run(self, **kwargs: Any) -> ToolResult:
        cfg = get_config()
        if not cfg.agent_permissions.get("terminal", False):
            return ToolResult(False, "Terminal tool disabled in config (agents.permissions.terminal)")

        command = kwargs.get("command", "").strip()
        if not command:
            return ToolResult(False, "No command provided")
        timeout = int(kwargs.get("timeout_seconds", 120))
        cwd = str(cfg.workspace)

        logger.info("Executing terminal: %s (cwd=%s)", command, cwd)
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return ToolResult(False, f"Command timed out after {timeout}s")

            stdout = stdout_b.decode(errors="replace")
            stderr = stderr_b.decode(errors="replace")
            code = proc.returncode or 0
            combined = f"exit_code={code}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
            return ToolResult(code == 0, combined, {"exit_code": code})
        except Exception as exc:
            logger.exception("Terminal execution failed")
            return ToolResult(False, str(exc))
