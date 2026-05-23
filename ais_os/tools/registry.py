"""Central tool registry — extensible for MCP and integrations."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from ais_os.tools.base import BaseTool, ToolResult
from ais_os.tools.filesystem_tool import FilesystemTool
from ais_os.tools.terminal_tool import TerminalTool

logger = logging.getLogger("ais_os.tools.registry")


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self.register(TerminalTool())
        self.register(FilesystemTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    async def execute(self, name: str, arguments: str | dict[str, Any]) -> ToolResult:
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(False, f"Unknown tool: {name}")
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments) if arguments.strip() else {}
            except json.JSONDecodeError:
                args = {"command": arguments} if name == "run_terminal" else {}
        else:
            args = arguments
        return await tool.run(**args)


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()
